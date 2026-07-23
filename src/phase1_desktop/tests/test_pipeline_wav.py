"""
WAV File Pipeline Test — EchoEcho-T Phase 1

Tests the full pipeline with a pre-recorded WAV file (no mic needed).
This proves the pipeline works end-to-end.

Usage:
    python tests/test_pipeline_wav.py [wav_file] [language_code]

Example:
    # Record a test file first:
    python -c "import sounddevice as sd; import numpy as np; fs=16000; d=3; a=sd.rec(int(fs*d), samplerate=fs, channels=1, dtype='float32'); sd.wait(); np.save('test_speech.npy', a[:,0])"

    # Then test:
    python tests/test_pipeline_wav.py test_speech.npy de
"""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.stt import STT
from ai.language_manager import LanguageManager, LANGUAGE_NAMES
from ai.tts import TTS
from ai.vad import VAD


def test_wav_pipeline(audio_path: str, target_lang: str = "de"):
    """Test pipeline with a numpy audio file."""
    print("=" * 60)
    print("EchoEcho-T — WAV Pipeline Test (no mic needed)")
    print("=" * 60)
    print(f"Audio:  {audio_path}")
    print(f"Target: English → {LANGUAGE_NAMES.get(target_lang, target_lang)}")
    print("-" * 60)

    # Load audio
    audio = np.load(audio_path)
    if audio.ndim > 1:
        audio = audio[:, 0]  # Take first channel
    print(f"Loaded {len(audio)} samples ({len(audio)/16000:.2f}s) at 16kHz")

    # Modules
    vad = VAD(threshold=0.3, min_speech_duration_ms=250)
    stt = STT(language="en")
    lm = LanguageManager(default_lang=target_lang)
    tts = TTS()

    # Confirm target language
    greeting = lm.switch_language(target_lang)
    print(f"[TTS] {greeting}")
    tts.speak(greeting, target_lang)
    time.sleep(2)

    # Feed audio through VAD in 512-sample chunks
    chunk_size = 512
    segments = []
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        if len(chunk) < chunk_size:
            chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
        segment = vad.process(chunk)
        if segment is not None:
            segments.append(segment)

    # Flush remaining
    remaining = vad.flush()
    if remaining is not None:
        segments.append(remaining)

    print(f"\n[VAD]  Detected {len(segments)} speech segments")

    for idx, segment in enumerate(segments, 1):
        duration_ms = len(segment) / 16000 * 1000
        print(f"\n  Segment {idx}: {duration_ms:.0f}ms")

        # STT
        print(f"  [STT]  Transcribing...")
        text, lang = stt.transcribe(segment)
        if not text.strip():
            print(f"  [STT]  No text detected")
            continue
        print(f"  [STT]  ({lang}): '{text}'")

        # Check switch command
        switch_lang = lm.is_switch_command(text)
        if switch_lang:
            confirmation = lm.switch_language(switch_lang)
            print(f"  [SWITCH] → {LANGUAGE_NAMES.get(switch_lang, switch_lang)}")
            print(f"  [TTS] {confirmation}")
            tts.speak(confirmation, switch_lang)
            time.sleep(2)
            continue

        # Translate
        t0 = time.time()
        translated = lm.translate(text)
        elapsed = time.time() - t0
        print(f"  [→]    {translated}  ({elapsed:.3f}s)")

        # Speak
        tts.speak(translated, lm.current_lang)
        time.sleep(2)

    tts.stop()
    print("\n" + "=" * 60)
    print("Test complete.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pipeline_wav.py <audio.npy> [language_code]")
        print("\nTo record a test file:")
        print('  python -c "')
        print('    import sounddevice as sd, numpy as np')
        print('    fs = 16000; d = 5')
        print('    print(\"Speak now!\")')
        print('    a = sd.rec(int(fs*d), samplerate=fs, channels=1, dtype=\"float32\")')
        print('    sd.wait()')
        print('    np.save(\"my_speech.npy\", a[:,0])')
        print('    print(\"Saved to my_speech.npy\")')
        print('  "')
        sys.exit(1)

    audio_path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "de"
    test_wav_pipeline(audio_path, lang)
