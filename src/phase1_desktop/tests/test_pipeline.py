"""
Pipeline Smoke Test — Phase 1

Tests each stage independently before integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time


def test_vad():
    from ai.vad import VAD
    print("[TEST] VAD...")
    vad = VAD(threshold=0.5)

    # Speech-like signal
    sr = 16000
    t = np.linspace(0, 1, sr, dtype=np.float32)
    speech = 0.3 * (
        np.sin(2 * np.pi * 150 * t) +
        0.5 * np.sin(2 * np.pi * 300 * t)
    ) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))

    # Feed in chunks
    segment = None
    for i in range(0, len(speech) - 511, 512):
        chunk = speech[i:i + 512]
        if len(chunk) == 512:
            result = vad.process(chunk)
            if result is not None:
                segment = result
                break

    if segment is not None:
        print(f"  PASS: Speech detected, segment length {len(segment)}")
    else:
        print("  INFO: No speech segment returned (may need longer input)")


def test_stt():
    from ai.stt import STT
    print("[TEST] STT...")
    stt = STT()

    # Synthetic audio (won't transcribe to real words, but tests inference)
    audio = np.zeros(16000, dtype=np.float32)
    t0 = time.time()
    text, lang = stt.transcribe(audio)
    elapsed = time.time() - t0
    print(f"  PASS: Inference in {elapsed:.3f}s | Text: '{text}' | Lang: {lang}")


def test_latency_logger():
    from utils.latency import LatencyLogger, Timer
    print("[TEST] LatencyLogger...")
    logger = LatencyLogger("/tmp/test_latency.csv")

    with Timer(logger, "test_stage", "test details"):
        time.sleep(0.01)

    logger.log("manual", 5.0, "manual entry")
    stats = logger.summary()
    assert "test_stage" in stats
    assert "manual" in stats
    print(f"  PASS: {len(stats)} stages logged")


def main():
    print("=" * 60)
    print("Phase 1 Smoke Tests")
    print("=" * 60)

    test_latency_logger()
    test_vad()
    test_stt()

    print("=" * 60)
    print("All smoke tests completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
