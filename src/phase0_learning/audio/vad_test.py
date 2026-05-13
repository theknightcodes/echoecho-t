import torch
import sounddevice as sd
import numpy as np
import time
import sys

"""
Silero VAD Setup + Test — Phase 0, Week 1

Downloads Silero VAD, runs it on a live microphone stream,
and demonstrates speech detection with tunable thresholds.

Usage:
    python vad_test.py [threshold] [min_speech_duration_ms]

Example:
    python vad_test.py 0.5 250
"""

SAMPLE_RATE = 16000  # Silero VAD expects 16kHz
BLOCK_SIZE = 512     # ~32ms chunks


def get_silero_vad():
    """Download and load Silero VAD model."""
    print("Loading Silero VAD model...")
    model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        force_reload=False,
        onnx=False,
    )
    print("Model loaded successfully.")
    return model, utils


def vad_stream(model, threshold=0.5, min_speech_duration_ms=250):
    """Run VAD on live microphone stream."""
    print("=" * 60)
    print("Silero VAD Live Test")
    print("=" * 60)
    print(f"Threshold:              {threshold}")
    print(f"Min speech duration:    {min_speech_duration_ms} ms")
    print(f"Sample rate:            {SAMPLE_RATE} Hz")
    print("-" * 60)
    print("Speak into your microphone. Status will show below.")
    print("Press Ctrl+C to stop.")
    print("-" * 60)

    # VAD state tracking
    is_speaking = False
    speech_start_time = None
    speech_buffer = []

    def callback(indata, outdata, frames, time_info, status):
        nonlocal is_speaking, speech_start_time, speech_buffer

        if status:
            print(f"[Status] {status}", file=sys.stderr)

        # Convert to tensor (Silero expects float32, shape: [batch, samples])
        audio_tensor = torch.from_numpy(indata[:, 0].astype(np.float32))
        audio_tensor = audio_tensor.unsqueeze(0)  # Add batch dimension

        # Run VAD
        with torch.no_grad():
            speech_prob = model(audio_tensor, SAMPLE_RATE).item()

        # Detect speech start/stop with hysteresis
        if not is_speaking and speech_prob >= threshold:
            is_speaking = True
            speech_start_time = time.time()
            speech_buffer = [audio_tensor]
            print("[SPEECH START]", end="\r")

        elif is_speaking and speech_prob < threshold - 0.15:
            # Check minimum duration
            duration_ms = (time.time() - speech_start_time) * 1000
            if duration_ms >= min_speech_duration_ms:
                print(f"[SPEECH END] Duration: {duration_ms:.0f} ms | Prob: {speech_prob:.3f}")
                speech_buffer = []
            is_speaking = False
            speech_start_time = None

        elif is_speaking:
            speech_buffer.append(audio_tensor)
            duration_ms = (time.time() - speech_start_time) * 1000
            print(f"[SPEAKING] {duration_ms:.0f} ms | Prob: {speech_prob:.3f}  ", end="\r")

        else:
            print(f"[SILENCE] Prob: {speech_prob:.3f}  ", end="\r")

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype=np.float32,
            callback=callback,
        ):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[Stopped by user]")
    except Exception as e:
        print(f"\n[Error] {e}")
        sys.exit(1)


def main():
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    min_duration = int(sys.argv[2]) if len(sys.argv) > 2 else 250

    model, utils = get_silero_vad()
    vad_stream(model, threshold=threshold, min_speech_duration_ms=min_duration)


if __name__ == "__main__":
    main()
