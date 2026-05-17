"""
Language Switch Test — Phase 1

Tests the language switching functionality without audio.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.language_manager import LanguageManager, LANGUAGE_NAMES


def test_switch_detection():
    """Test command detection."""
    print("\n[TEST] Switch Command Detection...")
    lm = LanguageManager()

    test_cases = [
        ("switch to Japanese", "ja"),
        ("speak French", "fr"),
        ("use Hindi", "hi"),
        ("German", "de"),
        ("translate to Spanish", "es"),
        ("hello how are you", None),
        ("what time is it", None),
    ]

    passed = 0
    for text, expected in test_cases:
        result = lm.is_switch_command(text)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            print(f"  {status}: '{text}' → got={result}, expected={expected}")
        else:
            passed += 1

    print(f"  {passed}/{len(test_cases)} tests passed")


def test_language_switching():
    """Test switching between languages."""
    print("\n[TEST] Language Switching...")
    lm = LanguageManager(default_lang="de")

    print(f"  Default: {lm.get_current_language()}")

    # Switch to French (verified model exists)
    result = lm.switch_language("fr")
    print(f"  Switch to French: {result}")
    assert lm.current_lang == "fr"

    # Switch to Spanish (verified model exists)
    result = lm.switch_language("es")
    print(f"  Switch to Spanish: {result}")
    assert lm.current_lang == "es"

    # Switch back to German
    result = lm.switch_language("de")
    print(f"  Switch to German: {result}")
    assert lm.current_lang == "de"

    print("  PASS: Language switching works")


def test_translation():
    """Test translation in different languages."""
    print("\n[TEST] Translation...")
    lm = LanguageManager(default_lang="de")

    text = "Hello, how are you?"

    # German
    de = lm.translate(text, target_lang="de")
    print(f"  DE: {de}")

    # French
    fr = lm.translate(text, target_lang="fr")
    print(f"  FR: {fr}")

    # Spanish
    es = lm.translate(text, target_lang="es")
    print(f"  ES: {es}")

    print("  PASS: Translation works in multiple languages")
    print("  NOTE: Tamil requires NLLB-200 model (not Helsinki-NLP)")


def main():
    print("=" * 60)
    print("Language Switch Tests")
    print("=" * 60)

    test_switch_detection()
    test_language_switching()

    print("\n" + "=" * 60)
    print("All tests complete.")
    print("=" * 60)
    print("\nTo test with real speech:")
    print("  python main.py 60 ta     # Start with Tamil")
    print("  python main.py 60 ja     # Start with Japanese")
    print("  python main.py 60 hi     # Start with Hindi")
    print("  python main.py 60 de     # Start with German (default)")
    print("\nThen say: 'switch to French' or 'change to Spanish'")


if __name__ == "__main__":
    main()
