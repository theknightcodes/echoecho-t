import time
import sys
import numpy as np

"""
Whisper STT Benchmark — Phase 0, Week 2

Downloads and benchmarks Whisper (tiny) for speech-to-text inference.
Measures: load time, transcription time, memory usage.

Usage:
    python whisper_benchmark.py [audio_file.wav]
    (if no file provided, uses synthetic test audio)
"""

SAMPLE_RATE = 16000


def get_whisper_model():
    """Load faster-whisper tiny model."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "faster-whisper", "--quiet"])
        from faster_whisper import WhisperModel

    print("Loading Whisper tiny...")
    t0 = time.time()
    # Use CPU by default; MPS can be flaky with Whisper
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    load_time = time.time() - t0
    print(f"Model loaded in {load_time:.2f}s")
    return model, load_time


def generate_test_audio(duration_sec=5):
    """Generate synthetic speech-like audio for benchmarking."""
    t = np.linspace(0, duration_sec, int(SAMPLE_RATE * duration_sec), endpoint=False)
    # Multiple harmonics + modulation to resemble voiced speech
    audio = 0.3 * (
        np.sin(2 * np.pi * 150 * t) +
        0.5 * np.sin(2 * np.pi * 300 * t) +
        0.25 * np.sin(2 * np.pi * 450 * t)
    ) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))
    return audio.astype(np.float32)


def benchmark_transcription(model, audio, runs=3):
    """Run multiple inference passes and collect timing."""
    times = []
    segments_list = []

    for i in range(runs):
        t0 = time.time()
        segments, info = model.transcribe(audio, beam_size=5, language="en")
        # Force generator to complete
        text = " ".join([s.text for s in segments])
        elapsed = time.time() - t0
        times.append(elapsed)
        segments_list.append(text)
        print(f"  Run {i+1}: {elapsed:.3f}s | Detected lang: {info.language} | Text: {text[:60]}...")

    return times, segments_list


def main():
    print("=" * 60)
    print("Whisper Tiny Benchmark")
    print("=" * 60)

    # Load model
    model, load_time = get_whisper_model()

    # Get audio
    if len(sys.argv) > 1:
        import sounddevice as sd
        import wave
        with wave.open(sys.argv[1], "rb") as wf:
            n = wf.getnframes()
            audio = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
            if wf.getnchannels() == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)
        print(f"Loaded audio file: {len(audio)/SAMPLE_RATE:.1f}s")
    else:
        audio = generate_test_audio(5)
        print(f"Using synthetic audio: {len(audio)/SAMPLE_RATE:.1f}s")

    # Benchmark
    print("-" * 60)
    print("Running transcription benchmark (3 passes)...")
    times, texts = benchmark_transcription(model, audio, runs=3)

    # Report
    print("-" * 60)
    print("Results")
    print("-" * 60)
    print(f"Model:           Whisper tiny (int8)")
    print(f"Load time:       {load_time:.2f}s")
    print(f"Audio duration:  {len(audio)/SAMPLE_RATE:.1f}s")
    print(f"Inference times: {times}")
    print(f"Mean inference:  {np.mean(times):.3f}s")
    print(f"Min inference:   {np.min(times):.3f}s")
    print(f"Max inference:   {np.max(times):.3f}s")
    print(f"Std deviation:   {np.std(times):.3f}s")
    print(f"Real-time factor: {len(audio)/SAMPLE_RATE / np.mean(times):.2f}x")

    if np.mean(times) < 2.0:
        print("\nPASS: Inference < 2s target")
    else:
        print("\nFAIL: Inference > 2s target")
    print("=" * 60)


if __name__ == "__main__":
    main()
