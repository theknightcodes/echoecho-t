import time
import sys
import numpy as np

"""
Manual Pipeline Test — Phase 0, Week 2

Runs a basic STT → Translation → TTS chain manually
using synthetic audio, to verify each stage works.

This is a learning exercise, not the final pipeline.
"""

SAMPLE_RATE = 16000


def get_whisper():
    from faster_whisper import WhisperModel
    return WhisperModel("tiny", device="cpu", compute_type="int8")


def get_translator():
    from transformers import pipeline
    print("Loading translation model...")
    # Use Helsinki-NLP opus-mt for simplicity (lighter than NLLB)
    return pipeline("text2text-generation", model="Helsinki-NLP/opus-mt-en-de")


def generate_test_audio(duration_sec=3):
    """Generate synthetic speech-like audio."""
    t = np.linspace(0, duration_sec, int(SAMPLE_RATE * duration_sec), endpoint=False)
    audio = 0.3 * (
        np.sin(2 * np.pi * 150 * t) +
        0.5 * np.sin(2 * np.pi * 300 * t) +
        0.25 * np.sin(2 * np.pi * 450 * t)
    ) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))
    return audio.astype(np.float32)


def main():
    print("=" * 60)
    print("Manual Pipeline Test (STT → Translation)")
    print("=" * 60)

    # Generate audio
    audio = generate_test_audio(3)
    print(f"Generated synthetic audio: {len(audio)/SAMPLE_RATE:.1f}s")

    # Stage 1: STT
    print("\n[STAGE 1] Speech-to-Text")
    stt_model = get_whisper()
    t0 = time.time()
    segments, info = stt_model.transcribe(audio, beam_size=5, language="en")
    text = " ".join([s.text for s in segments])
    stt_time = time.time() - t0
    print(f"  Transcribed: '{text}'")
    print(f"  Time: {stt_time:.3f}s")

    # Stage 2: Translation
    print("\n[STAGE 2] Translation (EN → DE)")
    if not text.strip():
        print("  Skipping translation — STT produced empty text (synthetic audio)")
        translated = "[no text to translate]"
        trans_time = 0.0
    else:
        translator = get_translator()
        t0 = time.time()
        result = translator(text, max_length=100)
        translated = result[0]["generated_text"]
        trans_time = time.time() - t0
        print(f"  Translated: '{translated}'")
        print(f"  Time: {trans_time:.3f}s")

    # Summary
    print("\n" + "=" * 60)
    print("Pipeline Summary")
    print("=" * 60)
    print(f"STT:         {stt_time:.3f}s")
    print(f"Translation: {trans_time:.3f}s")
    print(f"Total:       {stt_time + trans_time:.3f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
