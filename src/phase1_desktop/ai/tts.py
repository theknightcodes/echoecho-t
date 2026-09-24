import asyncio
import subprocess
import threading
import queue
import re
import unicodedata
from typing import Optional

"""
Text-to-Speech Wrapper — Phase 1

Default backend: local macOS say, with printed text fallback on other systems.
Explicit allow_network=True enables Edge TTS before the local fallback.

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

# Language code → macOS `say` voice (used when edge-tts is unavailable/fails).
# Without this, `say` uses the default English voice, which cannot pronounce
# non-Latin scripts like Tamil/Hindi/Arabic/etc. — output is garbled.
_SAY_VOICES = {
    "de": "Anna",
    "fr": "Thomas",
    "es": "Monica",
    "it": "Alice",
    "pt": "Luciana",
    "nl": "Xander",
    "ru": "Milena",
    "zh": "Tingting",
    "ja": "Kyoko",
    "ko": "Yuna",
    "ta": "Vani",
    "hi": "Lekha",
    "ar": "Majed",
    "tr": "Yelda",
    "pl": "Zosia",
}

_EDGE_TTS_MAX_ATTEMPTS = 3


def _sanitize_for_tts(text: str) -> str:
    """Normalize whitespace without changing decimals, signs or contractions."""
    text = ''.join(ch for ch in text if not unicodedata.category(ch).startswith('C')
                   or ch in "\n\t\r")
    return re.sub(r'\s+', ' ', text).strip()



class TTS:
    def __init__(self, rate: int = 150, volume: float = 0.9, *, allow_network: bool = False):
        self.rate = rate
        self.volume = volume
        self._queue = queue.Queue(maxsize=20)
        self._thread = None
        self._running = False
        self._edge_tts_available = allow_network and self._check_edge_tts()
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
                self._queue.task_done()
                break
            text, lang = item
            try:
                self._speak_sync(text, lang)
            except Exception as exc:
                print(f"[TTS] Playback failed: {type(exc).__name__}")
            finally:
                self._queue.task_done()

    def _speak_sync(self, text: str, lang: str = "en"):
        clean = _sanitize_for_tts(text)
        if not clean:
            return

        # Try edge-tts first (supports all 15 languages). It occasionally fails
        # with transient connection errors, so retry a couple times before
        # giving up on it entirely.
        if self._edge_tts_available:
            voice = _EDGE_TTS_VOICES.get(lang, "en-US-AriaNeural")
            for attempt in range(1, _EDGE_TTS_MAX_ATTEMPTS + 1):
                try:
                    asyncio.run(self._edge_tts_speak(clean, voice))
                    return
                except Exception as e:
                    print(f"[TTS] edge-tts attempt {attempt}/{_EDGE_TTS_MAX_ATTEMPTS} failed: {e}")
            print("[TTS] edge-tts exhausted retries, falling back to say")

        # Fallback to macOS say — use the language's native voice so
        # non-Latin scripts (Tamil, Hindi, Arabic, etc.) are pronounced
        # correctly instead of read with the default English voice.
        say_voice = _SAY_VOICES.get(lang)
        say_cmd = ["say", "-r", str(self.rate)]
        if say_voice:
            say_cmd += ["-v", say_voice]

        try:
            subprocess.run(say_cmd, input=clean, text=True, check=True, timeout=30.0)
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
            await asyncio.wait_for(communicate.save(mp3_path), timeout=30.0)

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
        if not self._running:
            raise RuntimeError("TTS has been stopped")
        if not text.strip():
            return
        try:
            self._queue.put_nowait((text, lang))
        except queue.Full:
            print("[TTS] Queue full, dropping utterance")

    @property
    def busy(self) -> bool:
        with self._queue.mutex:
            return self._queue.unfinished_tasks > 0

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
