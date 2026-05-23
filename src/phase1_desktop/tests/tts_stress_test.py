#!/usr/bin/env python3
"""TTS Pipeline Stress Test — mimics how the orchestrator uses TTS."""
import threading
import queue
import time

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.tts import TTS

print("=" * 60)
print("TTS Pipeline Stress Test")
print("=" * 60)

tts = TTS()

# Utterances the pipeline would produce
utterances = [
    "Hello",
    "Sprache auf Deutsch umgestellt",
    "Hallo wie geht es dir",
    "Language switched",
]

print("\nQueuing 4 utterances (like the pipeline does)...")
for u in utterances:
    print(f"  speak('{u}')")
    tts.speak(u)

print("\nWaiting for TTS worker to process (15s)...")
for i in range(30):
    time.sleep(0.5)
    if tts._queue.empty():
        print("  Queue empty — all utterances processed")
        break
    print(f"  ... queue size: {tts._queue.qsize()}")
else:
    print("  [WARN] Queue still has items after 15s")

print("\n" + "=" * 60)
print("Test complete. Did you hear all 4 phrases?")
print("=" * 60)

tts.stop()
