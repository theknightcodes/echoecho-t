import subprocess
import threading
import queue
import re
import unicodedata
from typing import Optional

"""
Text-to-Speech Wrapper — Phase 1

Phase 1 uses macOS `say` (system TTS) because pyttsx3 is silently
broken on macOS Sonoma — runAndWait() returns with no audio.
Phase 2+ will switch to Piper TTS for better quality and language
support (Tamil, Japanese, etc.).
"""


def _sanitize_for_tts(text: str) -> str:
    """Strip all punctuation that TTS reads aloud as words."""
    # Remove leading dash + space (some models prefix "- ")
    text = re.sub(r"^-\s+", "", text)
    # Remove ALL punctuation characters (Unicode categories starting with 'P')
    text = ''.join(ch for ch in text if not unicodedata.category(ch).startswith('P'))
    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class TTS:
    def __init__(self, rate: int = 150, volume: float = 0.9):
        self.rate = rate
        self.volume = volume
        self._queue = queue.Queue(maxsize=20)
        self._thread = None
        self._running = False
        self._start_worker()

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
        """Synchronous speak via macOS `say` command."""
        clean = _sanitize_for_tts(text)
        if not clean:
            return
        try:
            # Use macOS `say` because pyttsx3 is silently broken on Sonoma.
            # rate: words per minute (80-450). We map our 150 default.
            cmd = [
                "say",
                "-r", str(self.rate),
                clean,
            ]
            subprocess.run(cmd, check=True, timeout=30.0)
        except FileNotFoundError:
            # Fallback: print if `say` not available (Linux, etc.)
            print(f"[TTS] {clean}")
        except subprocess.TimeoutExpired:
            print(f"[TTS] Timeout speaking: {clean[:50]}")
        except Exception as e:
            print(f"[TTS] Error: {e}")

    def speak(self, text: str):
        """Queue text to be spoken (non-blocking)."""
        if not text.strip():
            return
        try:
            self._queue.put_nowait(text)
        except queue.Full:
            print("[TTS] Queue full, dropping utterance")

    def stop(self):
        """Stop the TTS worker."""
        self._running = False
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
        if self._thread:
            self._thread.join(timeout=2.0)

    def synthesize(self, text: str) -> Optional[object]:
        """
        Synthesize text to audio array.
        Returns None in Phase 1 (`say` doesn't expose audio buffer).
        """
        self.speak(text)
        return None
