#!/usr/bin/env python3
"""Quick TTS diagnostic — run this to verify pyttsx3 works on your system."""

import pyttsx3
import time

print("=" * 60)
print("TTS Diagnostic")
print("=" * 60)

print("\n1. Initializing pyttsx3 engine...")
try:
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 0.9)
    print("   [OK] Engine initialized")
except Exception as e:
    print(f"   [FAIL] Could not initialize: {e}")
    exit(1)

print("\n2. Checking available voices...")
voices = engine.getProperty("voices")
print(f"   Found {len(voices)} voice(s)")
if voices:
    for i, v in enumerate(voices[:3]):
        print(f"   [{i}] {v.id} ({v.name})")
    engine.setProperty("voice", voices[0].id)
    print(f"   [OK] Set voice to: {voices[0].id}")
else:
    print("   [WARN] No voices found — TTS may fail")

print("\n3. Speaking test phrase synchronously (blocking)...")
try:
    engine.say("Hello, this is a test")
    print("   Saying 'Hello, this is a test'... (should hear audio now)")
    engine.runAndWait()
    print("   [OK] runAndWait() returned")
except Exception as e:
    print(f"   [FAIL] {e}")

print("\n4. Speaking test phrase from background thread...")
import threading

result = {"ok": False, "error": None}

def bg_speak():
    try:
        engine2 = pyttsx3.init()
        engine2.setProperty("rate", 150)
        engine2.setProperty("volume", 0.9)
        if voices:
            engine2.setProperty("voice", voices[0].id)
        engine2.say("Background thread test")
        print("   Saying 'Background thread test'...")
        engine2.runAndWait()
        result["ok"] = True
    except Exception as e:
        result["error"] = str(e)

t = threading.Thread(target=bg_speak, name="TTS-Diag")
t.start()
t.join(timeout=10.0)

if t.is_alive():
    print("   [FAIL] Background thread hung — runAndWait() did not return within 10s")
    print("   This is the likely cause of your pipeline issue.")
elif result["error"]:
    print(f"   [FAIL] Background thread error: {result['error']}")
else:
    print("   [OK] Background thread succeeded")

print("\n5. Checking if main-thread vs background matters...")
print("   On macOS, pyttsx3 uses NSSpeechSynthesizer which may require")
print("   the main thread. If step 3 worked but step 4 hung, that's the issue.")

print("\n" + "=" * 60)
if result["ok"]:
    print("DIAGNOSIS: TTS works. Check pipeline TTS wiring.")
else:
    print("DIAGNOSIS: TTS background thread is broken on this system.")
    print("Fix: Switch to main-thread TTS or use an alternative engine.")
print("=" * 60)
