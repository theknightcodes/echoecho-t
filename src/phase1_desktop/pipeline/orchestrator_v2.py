import threading
import queue
import time
import numpy as np
from typing import Optional

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.capture import AudioCapture
from audio.playback import AudioPlayback
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
        self.vad = VAD(threshold=0.3, min_speech_duration_ms=250)
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

    def _vad_worker(self):
        """Read audio, detect speech segments."""
        while self._running:
            chunk = self.capture.read(timeout=0.5)
            if chunk is None:
                continue

            with Timer(self.logger, "vad", "speech detection"):
                segment = self.vad.process(chunk)

            if segment is not None:
                duration_ms = len(segment) / self.sample_rate * 1000
                print(f"  [VAD]  Speech detected: {duration_ms:.0f}ms")
                try:
                    self._stt_queue.put_nowait(segment)
                except queue.Full:
                    print("  [VAD]  STT queue full — dropping segment")
                    pass

    def _stt_worker(self):
        """Transcribe speech segments."""
        while self._running:
            try:
                segment = self._stt_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            print(f"  [STT]  Transcribing {len(segment)} samples...")
            with Timer(self.logger, "stt", "whisper transcription"):
                text, lang = self.stt.transcribe(segment)

            if not text.strip():
                print("  [STT]  No text detected")
                continue

            print(f"  [STT]  Detected ({lang}): '{text}'")
            if self.on_transcript:
                self.on_transcript(text, lang)

            try:
                self._trans_queue.put_nowait(text)
            except queue.Full:
                print("  [TRANS] Queue full — dropping text")
                pass

    def _process_worker(self):
        """Check for switch commands, then translate."""
        while self._running:
            try:
                text = self._trans_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            # Check if this is a language switch command
            switch_lang = self.lang_manager.is_switch_command(text)
            if switch_lang:
                print(f"  [PROC] Switch command detected: '{text}' → {switch_lang}")
                confirmation = self.lang_manager.switch_language(switch_lang)
                if self.on_language_switch:
                    self.on_language_switch(switch_lang, confirmation)
                # Speak confirmation in new language
                print(f"  [TTS]  Speaking confirmation...")
                self.tts.speak(confirmation)
                continue

            # Normal translation
            print(f"  [PROC] Translating to {self.lang_manager.current_lang}...")
            with Timer(self.logger, "translate", f"to {self.lang_manager.current_lang}"):
                translated = self.lang_manager.translate(text)

            if translated.strip():
                print(f"  [→]    {translated}")
                if self.on_translation:
                    self.on_translation(translated)
                self.tts.speak(translated)
            else:
                print("  [PROC] Translation empty — skipping TTS")

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
            self.on_status(f"Pipeline started. Speak in English. Translation: {current}. Say 'switch to [language]' to change.")

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
