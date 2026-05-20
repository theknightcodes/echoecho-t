"""
Comprehensive Language QA — Phase 1 (NLLB-200 Backend)

Tests translation quality for ALL supported languages using NLLB-200-distilled-600M.
Uses text input (not speech) to isolate translation quality.

Reports: model load success, translation output, quality assessment.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from ai.language_manager import LanguageManager, LANGUAGE_NAMES

# Standard test phrases for consistent comparison
TEST_PHRASES = [
    "Hello, how are you?",
    "Thank you very much.",
    "Where is the train station?",
    "I would like to order food.",
    "Good morning.",
    "How much does this cost?",
    "Please help me.",
]


def test_single_language(lang_code: str, test_phrases: list, lm: LanguageManager) -> dict:
    """Test one language thoroughly."""
    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
    print(f"\n{'='*60}")
    print(f"Testing: {lang_name} ({lang_code})")
    print(f"{'='*60}")

    results = {
        "code": lang_code,
        "name": lang_name,
        "load_success": True,
        "translations": [],
        "avg_time": 0,
        "errors": [],
    }

    # Test translations
    times = []
    for phrase in test_phrases:
        try:
            t0 = time.time()
            translated = lm.translate(phrase, target_lang=lang_code)
            elapsed = time.time() - t0
            times.append(elapsed)

            result = {
                "source": phrase,
                "translated": translated,
                "time": elapsed,
                "status": "OK",
            }
            results["translations"].append(result)
            print(f"  [{elapsed:.3f}s] '{phrase}' -> '{translated}'")
        except Exception as e:
            result = {
                "source": phrase,
                "translated": f"ERROR: {e}",
                "time": 0,
                "status": "ERROR",
            }
            results["translations"].append(result)
            results["errors"].append(f"TRANSLATE FAILED for '{phrase}': {e}")
            print(f"  ERROR: '{phrase}' -> {e}")

    if times:
        results["avg_time"] = sum(times) / len(times)
        print(f"  Average translation time: {results['avg_time']:.3f}s")

    return results


def quality_assessment(result: dict) -> str:
    """Basic quality check on translation output."""
    if not result["translations"]:
        return "FAIL — No translations produced"

    empty_count = 0
    same_count = 0
    for t in result["translations"]:
        trans = t["translated"]
        if trans.startswith("ERROR"):
            return "FAIL — Translation errors occurred"
        if not trans or trans.strip() == "":
            empty_count += 1
        if trans.lower().strip() == t["source"].lower().strip():
            same_count += 1

    if empty_count > len(result["translations"]) // 2:
        return "FAIL — Most translations are empty"

    if same_count > len(result["translations"]) // 2:
        return "FAIL — Most translations identical to source (pass-through)"

    sample = result["translations"][0]["translated"]
    source = result["translations"][0]["source"]
    if sample.lower().strip() == source.lower().strip():
        return "WARN — Translation same as source (possible pass-through)"

    return "PASS — Translations appear valid"


def main():
    print("=" * 80)
    print("COMPREHENSIVE LANGUAGE QA — NLLB-200-distilled-600M")
    print("=" * 80)
    print(f"Testing {len(LANGUAGE_NAMES)} languages with {len(TEST_PHRASES)} phrases each")
    print("Model: facebook/nllb-200-distilled-600M (~2.4GB fp16)")
    print("First run downloads model (~2.4GB) — this will take a few minutes")
    print("-" * 80)

    lm = LanguageManager()
    # Pre-load model once
    print("\n[Loading model...]")
    try:
        lm._load_model()
        print("[Model ready]\n")
    except Exception as e:
        print(f"[FATAL] Could not load model: {e}")
        return

    all_results = []
    total_start = time.time()

    for lang_code in sorted(LANGUAGE_NAMES.keys()):
        result = test_single_language(lang_code, TEST_PHRASES, lm)
        result["quality"] = quality_assessment(result)
        all_results.append(result)

    total_time = time.time() - total_start

    # Summary report
    print("\n" + "=" * 80)
    print("QA SUMMARY REPORT")
    print("=" * 80)
    print(f"{'Language':<12} {'Code':<6} {'Avg Time':<12} {'Quality':<30}")
    print("-" * 80)

    pass_count = 0
    fail_count = 0
    for r in all_results:
        status = r["quality"]
        if status.startswith("PASS"):
            pass_count += 1
        else:
            fail_count += 1

        time_str = f"{r['avg_time']:.3f}s" if r["avg_time"] > 0 else "N/A"
        print(f"{r['name']:<12} {r['code']:<6} {time_str:<12} {status:<30}")

    print("-" * 80)
    print(f"Total time: {total_time:.1f}s")
    print(f"Pass: {pass_count} | Fail: {fail_count} | Total: {len(all_results)}")

    # Detailed failures
    failures = [r for r in all_results if not r["quality"].startswith("PASS")]
    if failures:
        print("\n" + "=" * 80)
        print("FAILURE DETAILS")
        print("=" * 80)
        for r in failures:
            print(f"\n{r['name']} ({r['code']}):")
            for err in r["errors"]:
                print(f"  - {err}")
            for t in r["translations"]:
                if t["status"] != "OK":
                    print(f"  - '{t['source']}' -> {t['translated']}")

    # Best performers
    successes = [r for r in all_results if r["quality"].startswith("PASS")]
    if successes:
        print("\n" + "=" * 80)
        print("BEST PERFORMERS (by speed)")
        print("=" * 80)
        sorted_by_speed = sorted(successes, key=lambda x: x["avg_time"])
        for r in sorted_by_speed[:5]:
            print(f"  {r['name']:<12} {r['avg_time']:.3f}s avg")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
