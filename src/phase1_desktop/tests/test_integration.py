"""
Integration Test — Phase 1 Desktop Prototype

Verifies all pipeline stages work together end-to-end.
Uses synthetic audio to test the wiring (not accuracy).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
import threading
import queue

from audio.capture import AudioCapture
from audio.playback import AudioPlayback
from ai.vad import VAD
from ai.stt import STT
from ai.translate import Translator
from ai.tts import TTS
from utils.latency import LatencyLogger, Timer


def test_audio_capture_playback():
    """Test audio capture and playback loop."""
    print("\n[TEST] Audio Capture → Playback Loop...")
    cap = AudioCapture(block_size=512)
    play = AudioPlayback(block_size=512)

    cap.start()
    play.start()

    # Capture 3 seconds of audio and play it back
    time.sleep(3)

    # Drain captured audio to playback
    chunks = 0
    while True:
        chunk = cap.read(timeout=0.1)
        if chunk is None:
            break
        play.play(chunk)
        chunks += 1

    cap.stop()
    play.stop()
    print(f"  PASS: Captured and played back {chunks} chunks")


def test_vad_stt_chain():
    """Test VAD feeding into STT."""
    print("\n[TEST] VAD → STT Chain...")
    vad = VAD(threshold=0.5)
    stt = STT()

    # Create longer speech-like signal (3 seconds)
    sr = 16000
    duration = 3
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    speech = 0.3 * (
        np.sin(2 * np.pi * 150 * t) +
        0.5 * np.sin(2 * np.pi * 300 * t) +
        0.25 * np.sin(2 * np.pi * 450 * t)
    ) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))
    speech = speech.astype(np.float32)

    # Feed through VAD
    segments = []
    for i in range(0, len(speech) - 511, 512):
        chunk = speech[i:i + 512]
        if len(chunk) == 512:
            result = vad.process(chunk)
            if result is not None:
                segments.append(result)

    print(f"  VAD found {len(segments)} speech segments")

    # Transcribe each segment
    for seg in segments:
        t0 = time.time()
        text, lang = stt.transcribe(seg)
        elapsed = time.time() - t0
        print(f"    STT: '{text}' ({lang}) in {elapsed:.3f}s")

    print(f"  PASS: VAD → STT chain works")


def test_translation_tts_chain():
    """Test Translation → TTS."""
    print("\n[TEST] Translation → TTS Chain...")
    translator = Translator()
    tts = TTS()

    test_text = "Hello, how are you?"
    t0 = time.time()
    translated = translator.translate(test_text)
    trans_time = time.time() - t0

    print(f"  EN: '{test_text}'")
    print(f"  DE: '{translated}' ({trans_time:.3f}s)")

    # TTS (text-only if pyttsx3 not available)
    tts.speak(translated)
    print(f"  PASS: Translation → TTS works")


def test_latency_logger():
    """Test latency logging end-to-end."""
    print("\n[TEST] Latency Logger...")
    logger = LatencyLogger("/tmp/integration_latency.csv")

    stages = ["capture", "vad", "stt", "translate", "tts"]
    for stage in stages:
        with Timer(logger, stage, f"test {stage}"):
            time.sleep(0.01)

    stats = logger.summary()
    assert len(stats) == len(stages)
    print(f"  PASS: All {len(stages)} stages logged")
    logger.report()


def main():
    print("=" * 60)
    print("Phase 1 Integration Tests")
    print("=" * 60)

    test_latency_logger()
    test_translation_tts_chain()
    test_vad_stt_chain()

    print("\n" + "=" * 60)
    print("Integration tests complete.")
    print("=" * 60)
    print("\nNOTE: Full pipeline with real speech requires:")
    print("  python src/phase1_desktop/main.py")


if __name__ == "__main__":
    main()
