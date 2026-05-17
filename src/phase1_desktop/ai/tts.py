import numpy as np
import io
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

    def _init_engine(self):
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)
        except ImportError:
            print("[TTS] pyttsx3 not installed. TTS will be text-only.")
            print("Install with: pip install pyttsx3")

    def speak(self, text: str):
        """Speak text aloud."""
        if not text.strip():
            return
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print(f"[TTS] {text}")

    def synthesize(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize text to audio array.
        Returns None in Phase 1 (pyttsx3 doesn't expose audio buffer easily).
        """
        # Phase 1: Just speak. Phase 2 will implement real synthesis with Piper.
        self.speak(text)
        return None
