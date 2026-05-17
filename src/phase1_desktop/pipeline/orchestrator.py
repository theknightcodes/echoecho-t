import threading
import queue
import time
import numpy as np
from typing import Optional

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.capture import AudioCapture
from audio.playback import AudioPlayback
from ai.vad import VAD
from ai.stt import STT
from ai.translate import Translator
from ai.tts import TTS
from utils.latency import LatencyLogger, Timer

"""
Pipeline Orchestrator — Phase 1

Coordinates the full audio pipeline:
  Capture → VAD → STT → Translation → TTS → (text output)

Each stage runs in a worker thread connected by queues.
"""


class Pipeline:
    def __init__(
        self,
        sample_rate: int = 16000,
        block_size: int = 512,
        latency_log: str = "logs/latency.csv",
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.logger = LatencyLogger(latency_log)

        # Modules
        self.capture = AudioCapture(sample_rate, block_size)
        self.vad = VAD(threshold=0.5, min_speech_duration_ms=250)
        self.stt = STT(model_size="tiny", device="cpu", compute_type="int8")
        self.translator = Translator()
        self.tts = TTS()

        # Queues between stages
        self._vad_queue = queue.Queue(maxsize=10)
        self._stt_queue = queue.Queue(maxsize=10)
        self._trans_queue = queue.Queue(maxsize=10)
        self._tts_queue = queue.Queue(maxsize=10)

        # Threads
        self._threads = []
        self._running = False

        # Callbacks
        self.on_transcript = None
        self.on_translation = None
        self.on_status = None

    def _vad_worker(self):
        """Read audio from capture, detect speech segments."""
        while self._running:
            chunk = self.capture.read(timeout=0.5)
            if chunk is None:
                continue

            with Timer(self.logger, "vad", "speech detection"):
                segment = self.vad.process(chunk)

            if segment is not None:
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

            with Timer(self.logger, "stt", "whisper transcription"):
                text, lang = self.stt.transcribe(segment)

            if text.strip():
                if self.on_transcript:
                    self.on_transcript(text, lang)
                try:
                    self._trans_queue.put_nowait((text, lang))
                except queue.Full:
                    pass

    def _translate_worker(self):
        """Translate transcribed text."""
        while self._running:
            try:
                text, lang = self._trans_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            with Timer(self.logger, "translate", "helsinki translation"):
                translated = self.translator.translate(text)

            if translated.strip():
                if self.on_translation:
                    self.on_translation(translated)
                try:
                    self._tts_queue.put_nowait(translated)
                except queue.Full:
                    pass

    def _tts_worker(self):
        """Speak translated text."""
        while self._running:
            try:
                text = self._tts_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            with Timer(self.logger, "tts", "text-to-speech"):
                self.tts.speak(text)

    def start(self):
        """Start all pipeline stages."""
        self._running = True
        self.capture.start()

        workers = [
            ("VAD", self._vad_worker),
            ("STT", self._stt_worker),
            ("Translate", self._translate_worker),
            ("TTS", self._tts_worker),
        ]

        for name, target in workers:
            t = threading.Thread(target=target, name=f"Pipeline-{name}", daemon=True)
            t.start()
            self._threads.append(t)

        if self.on_status:
            self.on_status("Pipeline started. Speak into your microphone.")

    def stop(self):
        """Stop all pipeline stages."""
        self._running = False
        self.capture.stop()
        for t in self._threads:
            t.join(timeout=2.0)
        self._threads = []
        self.logger.report()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
