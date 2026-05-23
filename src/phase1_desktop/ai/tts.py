import asyncio
import subprocess
import threading
import queue
import re
import unicodedata
from typing import Optional

"""
Text-to-Speech Wrapper — Phase 1

Backend priority:
1. edge-tts (Microsoft Edge, free, 100+ languages, natural voice)
2. macOS say (native, no install, limited languages)
3. Print text (fallback)

Phase 2+ will switch to Piper TTS for fully offline operation.
"""

# Language code → edge-tts voice mapping
_EDGE_TTS_VOICES = {
    "de": "de-DE-KatjaNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "nl": "nl-NL-ColetteNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "ta": "ta-IN-PallaviNeural",
    "hi": "hi-IN-SwaraNeural",
    "ar": "ar-SA-ZariyahNeural",
    "tr": "tr-TR-EmelNeural",
    "pl": "pl-PL-AgnieszkaNeural",
}


def _sanitize_for_tts(text: str) -> str:
    """Strip all punctuation that TTS reads aloud as words."""
    text = re.sub(r"^-\s+", "", text)
    text = ''.join(ch for ch in text if not unicodedata.category(ch).startswith('P'))
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class TTS:
    def __init__(self, rate: int = 150, volume: float = 0.9):
        self.rate = rate
        self.volume = volume
        self._queue = queue.Queue(maxsize=20)
        self._thread = None
        self._running = False
        self._edge_tts_available = self._check_edge_tts()
        self._start_worker()

    def _check_edge_tts(self) -> bool:
        """Check if edge-tts is installed."""
        try:
            import edge_tts
            return True
        except ImportError:
            print("[TTS] edge-tts not installed. Tamil/Japanese/Hindi/Arabic/etc. will be silent.")
            print("        Install with: pip install edge-tts")
            return False

    def _start_worker(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker, name="TTS-Worker", daemon=True)
        self._thread.start()

    def _worker(self):
        while self._running:
            try:
                item = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                break
            text, lang = item
            self._speak_sync(text, lang)

    def _speak_sync(self, text: str, lang: str = "en"):
        clean = _sanitize_for_tts(text)
        if not clean:
            return

        # Try edge-tts first (supports all 15 languages)
        if self._edge_tts_available:
            try:
                voice = _EDGE_TTS_VOICES.get(lang, "en-US-AriaNeural")
                asyncio.run(self._edge_tts_speak(clean, voice))
                return
            except Exception as e:
                print(f"[TTS] edge-tts failed: {e}, falling back to say")

        # Fallback to macOS say (only supports a subset)
        try:
            subprocess.run(["say", "-r", str(self.rate), clean], check=True, timeout=30.0)
        except FileNotFoundError:
            print(f"[TTS] {clean}")
        except subprocess.TimeoutExpired:
            print(f"[TTS] Timeout speaking: {clean[:50]}")
        except Exception as e:
            print(f"[TTS] Error: {e}")

    async def _edge_tts_speak(self, text: str, voice: str):
        import edge_tts
        import tempfile
        import sounddevice as sd
        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            mp3_path = f.name

        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(mp3_path)

            data, samplerate = sf.read(mp3_path, dtype="float32")
            if data.ndim > 1:
                data = data.mean(axis=1)
            sd.play(data, samplerate)
            sd.wait()
        finally:
            import os
            try:
                os.remove(mp3_path)
            except OSError:
                pass

    def speak(self, text: str, lang: str = "en"):
        """Queue text to be spoken (non-blocking)."""
        if not text.strip():
            return
        try:
            self._queue.put_nowait((text, lang))
        except queue.Full:
            print("[TTS] Queue full, dropping utterance")

    def stop(self):
        self._running = False
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
        if self._thread:
            self._thread.join(timeout=2.0)

    def synthesize(self, text: str, lang: str = "en") -> Optional[object]:
        self.speak(text, lang)
        return None
