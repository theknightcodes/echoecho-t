"""
Text-Mode Pipeline Test — EchoEcho-T Phase 1

Tests the full pipeline chain (STT→Translation→TTS) WITHOUT microphone.
Type English text and see/hear the translation.

Usage:
    python tests/test_pipeline_text.py [language_code]

Example:
    python tests/test_pipeline_text.py de     # Test German
    python tests/test_pipeline_text.py fr     # Test French
    python tests/test_pipeline_text.py hi     # Test Hindi
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.language_manager import LanguageManager, LANGUAGE_NAMES
from ai.tts import TTS


def test_text_pipeline(target_lang: str = "de"):
    """Test pipeline with typed text (no mic)."""
    print("=" * 60)
    print("EchoEcho-T — Text Pipeline Test (no mic needed)")
    print("=" * 60)
    print(f"Target: English → {LANGUAGE_NAMES.get(target_lang, target_lang)}")
    print("-" * 60)

    lm = LanguageManager(default_lang=target_lang)
    tts = TTS()

    # Confirm target language
    greeting = lm.switch_language(target_lang)
    print(f"[TTS] {greeting}")
    tts.speak(greeting, target_lang)
    print()

    while True:
        try:
            text = input("Type English text (or 'switch to [language]' / 'quit'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not text:
            continue

        if text.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # Check for language switch
        switch_lang = lm.is_switch_command(text)
        if switch_lang:
            confirmation = lm.switch_language(switch_lang)
            print(f"  [SWITCH] → {LANGUAGE_NAMES.get(switch_lang, switch_lang)}")
            print(f"  [TTS] {confirmation}")
            tts.speak(confirmation, switch_lang)
            continue

        # Translate
        t0 = time.time()
        translated = lm.translate(text)
        elapsed = time.time() - t0

        print(f"  [STT]  EN: {text}")
        print(f"  [→]    {target_lang.upper()}: {translated}  ({elapsed:.3f}s)")

        # Speak
        tts.speak(translated, lm.current_lang)
        print()


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "de"
    test_text_pipeline(lang)
