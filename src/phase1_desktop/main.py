#!/usr/bin/env python3
"""
EchoEcho-T Phase 1 — Desktop Prototype v2

Real-time speech translation with multi-language support.

Pipeline: Mic → VAD → STT → [Switch Check] → Translation → TTS

Usage:
    python main.py [duration_seconds] [default_language]

Examples:
    python main.py                  # 30s, default German
    python main.py 60               # 60s, default German
    python main.py 60 ta            # 60s, default Tamil

Voice Commands:
    "switch to Tamil"     → Switch to Tamil
    "change to Japanese"  → Switch to Japanese
    "speak French"      → Switch to French
    "use Hindi"         → Switch to Hindi

Press Ctrl+C to stop.
"""

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.orchestrator_v2 import Pipeline
from ai.language_manager import LANGUAGE_NAMES, LANGUAGE_CODES
from ai.tts import _sanitize_for_tts


_DEFAULT_DURATION = 30
_DEFAULT_LANG = "de"


def _validate_args() -> tuple[int, str]:
    """Parse and validate CLI arguments."""
    duration = _DEFAULT_DURATION
    default_lang = _DEFAULT_LANG

    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
            if duration < 1 or duration > 3600:
                print(f"[WARN] Duration must be 1-3600 seconds. Using {_DEFAULT_DURATION}.")
                duration = _DEFAULT_DURATION
        except ValueError:
            print(f"[WARN] Invalid duration '{sys.argv[1]}'. Using {_DEFAULT_DURATION}.")

    if len(sys.argv) > 2:
        lang = sys.argv[2].lower().strip()
        if lang not in LANGUAGE_CODES:
            print(
                f"[WARN] Unsupported language '{lang}'. "
                f"Supported: {', '.join(LANGUAGE_CODES.keys())}. Using {_DEFAULT_LANG}."
            )
        else:
            default_lang = lang

    return duration, default_lang


def main():
    duration, default_lang = _validate_args()

    print("=" * 60)
    print("EchoEcho-T — Desktop Prototype (Phase 1 v2)")
    print("=" * 60)
    print("Pipeline: Mic → VAD → STT → Translation → TTS")
    print(f"Duration: {duration} seconds")
    print(f"Default:  English → {LANGUAGE_NAMES.get(default_lang, default_lang)}")
    print("-" * 60)
    print("Speak in English. You'll hear the translation.")
    print("Say 'switch to [language]' to change target language.")
    print("Supported languages:")
    langs = ", ".join([f"{k}={v}" for k, v in LANGUAGE_NAMES.items()])
    for line in _wrap_text(langs, 58):
        print(f"  {line}")
    print("-" * 60)
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    def on_transcript(text, lang):
        print(f"  [STT] {lang.upper()}: {text}")

    def on_translation(text):
        clean = _sanitize_for_tts(text)
        print(f"  [→]   {clean}")

    def on_status(msg):
        print(f"  [STATUS] {msg}")

    def on_language_switch(lang_code, confirmation):
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
        print(f"  [SWITCH] → {lang_name}")
        print(f"  [CONFIRM] {confirmation}")

    pipeline = Pipeline(default_lang=default_lang)
    pipeline.on_transcript = on_transcript
    pipeline.on_translation = on_translation
    pipeline.on_status = on_status
    pipeline.on_language_switch = on_language_switch

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


def _wrap_text(text: str, width: int) -> list:
    """Wrap text to specified width."""
    words = text.split(", ")
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 2 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current}, {word}" if current else word
    if current:
        lines.append(current)
    return lines


if __name__ == "__main__":
    main()
