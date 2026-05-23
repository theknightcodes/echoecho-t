#!/usr/bin/env python3
"""TTS macOS Deep Diagnostic — tests pyttsx3 vs system `say` command."""
import subprocess
import sys

print("=" * 60)
print("TTS macOS Deep Diagnostic")
print("=" * 60)

# 1. Check macOS version
print("\n1. macOS version:")
try:
    result = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True)
    print(f"   {result.stdout.strip()}")
except Exception as e:
    print(f"   Could not detect: {e}")

# 2. Check system volume
print("\n2. System output volume:")
try:
    result = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True, text=True
    )
    vol = result.stdout.strip()
    print(f"   {vol}%")
    if vol and int(vol) == 0:
        print("   [WARN] System volume is 0% — TTS will be silent!")
except Exception as e:
    print(f"   Could not detect: {e}")

# 3. Check output device
print("\n3. Current audio output device:")
try:
    result = subprocess.run(
        ["osascript", "-e", "output device of (get volume settings)"],
        capture_output=True, text=True
    )
    print(f"   {result.stdout.strip()}")
except Exception as e:
    print(f"   Could not detect: {e}")

# 4. Test system `say` command
print("\n4. Testing system 'say' command (direct)...")
try:
    subprocess.run(["say", "System say command works"], check=True)
    print("   [OK] 'say' command produced audio")
except Exception as e:
    print(f"   [FAIL] {e}")

# 5. Test pyttsx3 with explicit voice
print("\n5. Testing pyttsx3 with explicit voice selection...")
try:
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    print(f"   Found {len(voices)} voices")

    # Try each of the first few compact English voices
    test_voices = [v for v in voices if "en-US" in v.id or "en-GB" in v.id or "Samantha" in v.id or "Daniel" in v.id][:3]
    if not test_voices:
        test_voices = voices[:3]

    for v in test_voices:
        print(f"\n   Trying voice: {v.id}")
        engine.setProperty("voice", v.id)
        engine.say("Testing pyttsx3 voice")
        engine.runAndWait()
        print("   runAndWait() returned")

except Exception as e:
    print(f"   [FAIL] {e}")

# 6. Alternative: use `say` via subprocess from Python
print("\n6. Testing Python subprocess to 'say'...")
try:
    subprocess.run(["say", "Python subprocess say works"], check=True)
    print("   [OK] subprocess + say produced audio")
except Exception as e:
    print(f"   [FAIL] {e}")

print("\n" + "=" * 60)
print("Summary:")
print("  - If step 4 worked but step 5 didn't: pyttsx3 is broken.")
print("  - If step 4 also didn't work: system audio is muted/wrong device.")
print("  - If step 6 worked: we can switch TTS backend to subprocess+say.")
print("=" * 60)
