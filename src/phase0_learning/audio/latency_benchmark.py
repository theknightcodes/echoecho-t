import sounddevice as sd
import numpy as np
import time
import sys
from collections import deque

"""
Latency Benchmark — Phase 0, Week 1

Measures audio system latency more precisely by generating
a test tone and measuring the round-trip delay.

Usage:
    python latency_benchmark.py [duration_seconds]
"""

SAMPLE_RATE = 16000
BLOCK_SIZE = 512
CHANNELS = 1


class LatencyBenchmark:
    def __init__(self):
        self.latencies = deque(maxlen=1000)
        self.test_tone_active = False
        self.tone_start_time = None

    def callback(self, indata, outdata, frames, time_info, status):
        if status:
            print(f"[Status] {status}", file=sys.stderr)

        # Generate a short test impulse every 2 seconds on output
        current_time = time_info.currentTime
        outdata[:] = 0

        if int(current_time) % 2 == 0 and current_time % 1 < 0.05:
            # 1kHz tone burst for 50ms
            t = np.linspace(0, 0.05, int(SAMPLE_RATE * 0.05), endpoint=False)
            tone = 0.3 * np.sin(2 * np.pi * 1000 * t)
            samples_to_write = min(len(tone), len(outdata))
            outdata[:samples_to_write, 0] = tone[:samples_to_write]
            self.test_tone_active = True
            self.tone_start_time = current_time

        # Detect the tone in input and measure delay
        if self.test_tone_active and self.tone_start_time is not None:
            # Simple energy detection
            energy = np.mean(indata ** 2)
            if energy > 0.01:
                delay = current_time - self.tone_start_time
                self.latencies.append(delay)
                self.test_tone_active = False
                print(f"  Detected echo delay: {delay*1000:.2f} ms", end="\r")

    def run(self, duration=10):
        print("=" * 60)
        print("Latency Benchmark")
        print("=" * 60)
        print(f"Sample Rate: {SAMPLE_RATE} Hz")
        print(f"Block Size:  {BLOCK_SIZE} samples")
        print(f"Duration:    {duration} seconds")
        print("-" * 60)
        print("Generating test tones and measuring echo delay...")
        print("Ensure your microphone can hear your speakers (no headphones).")
        print("-" * 60)

        try:
            with sd.Stream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                channels=CHANNELS,
                dtype=np.float32,
                callback=self.callback,
            ):
                time.sleep(duration)
        except KeyboardInterrupt:
            pass

        print("\n" + "-" * 60)
        if len(self.latencies) > 0:
            latencies_ms = [l * 1000 for l in self.latencies]
            print(f"Measurements:     {len(latencies_ms)}")
            print(f"Min latency:      {min(latencies_ms):.2f} ms")
            print(f"Max latency:      {max(latencies_ms):.2f} ms")
            print(f"Mean latency:     {np.mean(latencies_ms):.2f} ms")
            print(f"Median latency:   {np.median(latencies_ms):.2f} ms")
            print(f"Std deviation:    {np.std(latencies_ms):.2f} ms")
            print(f"P95 latency:      {np.percentile(latencies_ms, 95):.2f} ms")

            if np.median(latencies_ms) < 100:
                print("\nPASS: Latency < 100ms target")
            else:
                print("\nFAIL: Latency > 100ms target")
                print("Try a smaller block size or lower sample rate.")
        else:
            print("No measurements captured. Check audio routing.")
        print("-" * 60)


def main():
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    benchmark = LatencyBenchmark()
    benchmark.run(duration)


if __name__ == "__main__":
    main()
