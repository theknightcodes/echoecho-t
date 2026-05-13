import sounddevice as sd
import numpy as np
import time

"""
Audio Buffer Management Test — Phase 0, Week 1

Explores different buffer sizes and their impact on latency
and audio quality. Helps tune the optimal chunk size for
the main pipeline.
"""

SAMPLE_RATE = 16000
DURATION = 5


def test_buffer_size(block_size):
    """Test a specific buffer size and report stats."""
    chunk_ms = block_size / SAMPLE_RATE * 1000
    print(f"\nTesting block_size={block_size} ({chunk_ms:.1f} ms chunks)...")

    latencies = []

    def callback(indata, outdata, frames, time_info, status):
        outdata[:] = indata
        adc = time_info.inputBufferAdcTime
        dac = time_info.outputBufferDacTime
        if adc and dac:
            latencies.append(dac - adc)

    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=block_size,
            channels=1,
            dtype=np.float32,
            callback=callback,
        ):
            time.sleep(DURATION)
    except sd.PortAudioError as e:
        print(f"  Failed: {e}")
        return None

    if latencies:
        mean_ms = np.mean(latencies) * 1000
        std_ms = np.std(latencies) * 1000
        print(f"  Mean latency: {mean_ms:.2f} ms (std: {std_ms:.2f} ms)")
        return mean_ms
    return None


def main():
    print("=" * 60)
    print("Audio Buffer Size Benchmark")
    print("=" * 60)
    print("Testing various buffer sizes to find optimal latency/quality tradeoff.")
    print(f"Duration per test: {DURATION} seconds")
    print("-" * 60)

    sizes = [128, 256, 512, 1024, 2048]
    results = {}

    for size in sizes:
        result = test_buffer_size(size)
        if result is not None:
            results[size] = result

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"{'Block Size':<12} {'Chunk (ms)':<12} {'Latency (ms)':<15} {'Quality':<10}")
    print("-" * 60)

    for size, latency in sorted(results.items()):
        chunk_ms = size / SAMPLE_RATE * 1000
        if latency < 50:
            quality = "Excellent"
        elif latency < 100:
            quality = "Good"
        elif latency < 200:
            quality = "Fair"
        else:
            quality = "Poor"
        print(f"{size:<12} {chunk_ms:<12.1f} {latency:<15.2f} {quality:<10}")

    print("-" * 60)
    if results:
        best = min(results.items(), key=lambda x: x[1])
        print(f"Recommended: block_size={best[0]} (lowest latency: {best[1]:.2f} ms)")
    print("=" * 60)


if __name__ == "__main__":
    main()
