#!/usr/bin/env python3
"""
EchoEcho-T Phase 1 — Desktop Prototype

Real-time speech translation pipeline:
  Mic → VAD → STT → Translation → TTS (speaks translation)

Usage:
    python main.py [duration_seconds]

Press Ctrl+C to stop.
"""

import sys
import time
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.orchestrator import Pipeline


def main():
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    print("=" * 60)
    print("EchoEcho-T — Desktop Prototype (Phase 1)")
    print("=" * 60)
    print("Pipeline: Mic → VAD → STT → Translation → TTS")
    print(f"Duration: {duration} seconds")
    print("-" * 60)
    print("Speak in English. You'll hear the German translation.")
    print("Press Ctrl+C to stop.")
    print("-" * 60)

    def on_transcript(text, lang):
        print(f"  [STT] {lang.upper()}: {text}")

    def on_translation(text):
        print(f"  [DE]  {text}")

    def on_status(msg):
        print(f"  [STATUS] {msg}")

    pipeline = Pipeline()
    pipeline.on_transcript = on_transcript
    pipeline.on_translation = on_translation
    pipeline.on_status = on_status

    try:
        with pipeline:
            time.sleep(duration)
    except KeyboardInterrupt:
        print("\n[Interrupted by user]")
    except Exception as e:
        print(f"\n[Error] {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Pipeline stopped.")
    print("=" * 60)


if __name__ == "__main__":
    main()
