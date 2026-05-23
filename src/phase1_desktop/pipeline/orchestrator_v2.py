import threading
import queue
import time
import numpy as np
from typing import Optional

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.capture import AudioCapture
from ai.vad import VAD
from ai.stt import STT
from ai.language_manager import LanguageManager
from ai.tts import TTS
from utils.latency import LatencyLogger, Timer

"""
Pipeline Orchestrator v2 — Phase 1

Coordinates the full audio pipeline with multi-language support.

  Capture → VAD → STT → [Switch Check] → Translation → TTS

Switch commands (e.g., "switch to Tamil") are intercepted before translation
and trigger a language change + confirmation.
"""


class Pipeline:
    def __init__(
        self,
        sample_rate: int = 16000,
        block_size: int = 512,
        latency_log: str = "logs/latency.csv",
        default_lang: str = "de",
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.logger = LatencyLogger(latency_log)

        # Modules
        self.capture = AudioCapture(sample_rate, block_size)
        self.vad = VAD(threshold=0.3, min_speech_duration_ms=500)
        self.stt = STT(model_size="tiny", device="cpu", compute_type="int8")
        self.lang_manager = LanguageManager(default_lang=default_lang)
        self.tts = TTS()

        # Queues
        self._stt_queue = queue.Queue(maxsize=10)
        self._trans_queue = queue.Queue(maxsize=10)

        # Threads
        self._threads = []
        self._running = False

        # Callbacks
        self.on_transcript = None
        self.on_translation = None
        self.on_status = None
        self.on_language_switch = None

        # TTS cooldown — ignore mic audio after speaking to prevent feedback loop
        self._tts_cooldown_until = 0.0

    def _drain_queue(self, q: queue.Queue):
        """Remove all pending items from a queue."""
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                break

    def _vad_worker(self):
        """Read audio, detect speech segments."""
        while self._running:
            chunk = self.capture.read(timeout=0.5)
            if chunk is None:
                continue

            # Skip audio during TTS cooldown to prevent feedback loop
            if time.time() < self._tts_cooldown_until:
                continue

            with Timer(self.logger, "vad", "speech detection"):
                segment = self.vad.process(chunk)

            if segment is not None:
                duration_ms = len(segment) / self.sample_rate * 1000
                print(f"  [VAD]  Speech detected: {duration_ms:.0f}ms")
                try:
                    self._stt_queue.put_nowait(segment)
                except queue.Full:
                    pass

    def _stt_worker(self):
        """Transcribe speech segments."""
        while self._running:
            try:
                segment = self._stt_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                with Timer(self.logger, "stt", "whisper transcription"):
                    text, lang = self.stt.transcribe(segment)
            except Exception as e:
                if self.on_status:
                    self.on_status(f"STT error: {e}")
                continue

            if not text.strip():
                continue

            if self.on_transcript:
                self.on_transcript(text, lang)

            try:
                self._trans_queue.put_nowait(text)
            except queue.Full:
                pass

    def _process_worker(self):
        """Check for switch commands, then translate."""
        while self._running:
            try:
                text = self._trans_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            # Skip very short transcripts — Whisper tiny hallucinates on 1-2 word utterances
            stripped = text.strip()
            if len(stripped) < 3:
                continue

            # Skip obvious TTS feedback: Tamil text getting re-transcribed as English
            lower = stripped.lower()
            if len(stripped) <= 4 and lower in ("bye", "hi", "dot", "don't", "yes", "no", "ok"):
                print(f"  [SKIP] Short/hallucinated transcript: '{text}'")
                continue

            # Check if this is a language switch command
            switch_lang = self.lang_manager.is_switch_command(text)
            if switch_lang:
                confirmation = self.lang_manager.switch_language(switch_lang)
                if self.on_language_switch:
                    self.on_language_switch(switch_lang, confirmation)
                self.tts.speak(confirmation, self.lang_manager.current_lang)
                self._clear_feedback()
                continue

            # Normal translation
            try:
                with Timer(self.logger, "translate", f"to {self.lang_manager.current_lang}"):
                    translated = self.lang_manager.translate(text)
            except Exception as e:
                if self.on_status:
                    self.on_status(f"Translation error: {e}")
                continue

            if translated.strip():
                if self.on_translation:
                    self.on_translation(translated)
                self.tts.speak(translated, self.lang_manager.current_lang)
                self._clear_feedback()

    def _clear_feedback(self):
        """Reset VAD, drain all queues, and mute mic after TTS to prevent feedback loop."""
        self._tts_cooldown_until = time.time() + 3.0
        self.vad.reset()
        self.capture.drain()
        # Drain all queues
        self._drain_queue(self._stt_queue)
        self._drain_queue(self._trans_queue)

    def start(self):
        """Start all pipeline stages."""
        self._running = True
        self.capture.start()

        workers = [
            ("VAD", self._vad_worker),
            ("STT", self._stt_worker),
            ("Process", self._process_worker),
        ]

        for name, target in workers:
            t = threading.Thread(target=target, name=f"Pipeline-{name}", daemon=True)
            t.start()
            self._threads.append(t)

        if self.on_status:
            current = self.lang_manager.get_current_language()
            self.on_status(
                f"Pipeline started. Speak in English. Translation: {current}. "
                f"Say 'switch to [language]' to change."
            )

    def stop(self):
        """Stop all pipeline stages."""
        self._running = False
        self.capture.stop()
        self.tts.stop()
        for t in self._threads:
            t.join(timeout=2.0)
        self._threads = []
        self.logger.report()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
