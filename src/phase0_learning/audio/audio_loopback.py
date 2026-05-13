import sounddevice as sd
import numpy as np
import time
import sys

"""
Audio Loopback Test — Phase 0, Week 1

Captures audio from the microphone and immediately plays it back
through the speakers to measure round-trip latency.

Usage:
    python audio_loopback.py [duration_seconds]

Press Ctrl+C to stop early.
"""

SAMPLE_RATE = 16000  # 16kHz — Whisper default, good for speech
BLOCK_SIZE = 512     # Samples per callback (~32ms at 16kHz)
CHANNELS = 1         # Mono


def audio_callback(indata, outdata, frames, time_info, status):
    """Pass input directly to output (loopback) with latency logging."""
    if status:
        print(f"[Status] {status}", file=sys.stderr)

    # indata is input buffer, outdata is pre-allocated output buffer
    outdata[:] = indata

    # Log timing info for analysis
    # time_info contains:
    #   input_adc_time: time when first sample was captured
    #   output_dac_time: time when first sample will play
    #   current_time: current stream time
    adc_time = time_info.input_adc_time
    dac_time = time_info.output_dac_time

    if adc_time is not None and dac_time is not None:
        latency = dac_time - adc_time
        print(f"  Latency: {latency*1000:.2f} ms | ADC: {adc_time:.4f} | DAC: {dac_time:.4f}", end="\r")


def main():
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    print("=" * 60)
    print("Audio Loopback Test")
    print("=" * 60)
    print(f"Sample Rate: {SAMPLE_RATE} Hz")
    print(f"Block Size:  {BLOCK_SIZE} samples ({BLOCK_SIZE/SAMPLE_RATE*1000:.1f} ms)")
    print(f"Channels:    {CHANNELS} (mono)")
    print(f"Duration:    {duration} seconds")
    print("-" * 60)
    print("Speak into your microphone. You should hear your voice immediately.")
    print("Press Ctrl+C to stop.")
    print("-" * 60)

    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=CHANNELS,
            dtype=np.float32,
            callback=audio_callback,
        ):
            time.sleep(duration)

    except KeyboardInterrupt:
        print("\n[Interrupted by user]")
    except sd.PortAudioError as e:
        print(f"\n[Audio Error] {e}")
        print("Common fixes:")
        print("  - Check that a microphone is connected and allowed")
        print("  - Try a different default audio device")
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
