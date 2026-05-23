#!/usr/bin/env python3
"""Quick edge-tts test — verifies Tamil audio before running full pipeline."""
import asyncio
import sys

print("=" * 60)
print("edge-tts Tamil Test")
print("=" * 60)

try:
    import edge_tts
    import sounddevice as sd
    import soundfile as sf
    import tempfile
    import os
    print("[OK] edge-tts, sounddevice, soundfile all imported")
except ImportError as e:
    print(f"[FAIL] Missing dependency: {e}")
    print("Install with: pip install edge-tts sounddevice soundfile")
    sys.exit(1)

async def test_tamil():
    text = "வணக்கம்"
    voice = "ta-IN-PallaviNeural"
    print(f"\nSynthesizing: '{text}' with voice {voice}")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        mp3_path = f.name

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(mp3_path)
        print(f"[OK] MP3 saved to {mp3_path}")

        data, samplerate = sf.read(mp3_path, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        print(f"[OK] Audio loaded: {len(data)} samples @ {samplerate}Hz")

        print("Playing... (should hear Tamil 'Vanakkam')")
        sd.play(data, samplerate)
        sd.wait()
        print("[OK] Playback complete")
    finally:
        try:
            os.remove(mp3_path)
        except OSError:
            pass

asyncio.run(test_tamil())
print("\n" + "=" * 60)
print("If you heard 'Vanakkam', edge-tts works. Run the pipeline now.")
print("=" * 60)
