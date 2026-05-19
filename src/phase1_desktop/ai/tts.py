import numpy as np
import threading
import queue
from typing import Optional

"""
Text-to-Speech Wrapper — Phase 1

Phase 1 uses pyttsx3 (system TTS) for simplicity.
Phase 2+ will switch to Piper TTS for better quality.
"""


class TTS:
    def __init__(self, rate: int = 150, volume: float = 0.9):
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._init_engine()
        self._queue = queue.Queue()
        self._thread = None
        self._running = False
        self._start_worker()

    def _init_engine(self):
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)
        except ImportError:
            print("[TTS] pyttsx3 not installed. TTS will be text-only.")
            print("Install with: pip install pyttsx3")

    def _start_worker(self):
        """Start background TTS thread."""
        self._running = True
        self._thread = threading.Thread(target=self._worker, name="TTS-Worker", daemon=True)
        self._thread.start()

    def _worker(self):
        """Background thread that speaks queued text."""
        while self._running:
            try:
                text = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if text is None:
                break
            self._speak_sync(text)

    def _speak_sync(self, text: str):
        """Synchronous speak (called from worker thread)."""
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print(f"[TTS] {text}")

    def speak(self, text: str):
        """Queue text to be spoken (non-blocking)."""
        if not text.strip():
            return
        self._queue.put_nowait(text)

    def stop(self):
        """Stop the TTS worker."""
        self._running = False
        self._queue.put(None)
        if self._thread:
            self._thread.join(timeout=2.0)

    def synthesize(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize text to audio array.
        Returns None in Phase 1 (pyttsx3 doesn't expose audio buffer easily).
        """
        self.speak(text)
        return None
