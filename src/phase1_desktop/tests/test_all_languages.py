"""
Comprehensive Language QA — Phase 1

Tests translation quality for ALL supported languages.
Uses text input (not speech) to isolate translation quality.

Reports: model load success, translation output, quality assessment.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from ai.language_manager import LanguageManager, LANGUAGE_MODELS, LANGUAGE_NAMES

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


def test_single_language(lang_code: str, test_phrases: list) -> dict:
    """Test one language thoroughly."""
    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
    print(f"\n{'='*60}")
    print(f"Testing: {lang_name} ({lang_code})")
    print(f"{'='*60}")

    lm = LanguageManager(default_lang=lang_code)
    results = {
        "code": lang_code,
        "name": lang_name,
        "model": LANGUAGE_MODELS.get(lang_code, "N/A"),
        "load_success": False,
        "load_time": 0,
        "translations": [],
        "avg_time": 0,
        "errors": [],
    }

    # Test model loading
    t0 = time.time()
    try:
        confirmation = lm.switch_language(lang_code)
        results["load_time"] = time.time() - t0
        results["load_success"] = True
        print(f"  Model loaded in {results['load_time']:.2f}s")
        print(f"  Confirmation: {confirmation}")
    except Exception as e:
        results["load_time"] = time.time() - t0
        results["errors"].append(f"LOAD FAILED: {e}")
        print(f"  LOAD FAILED: {e}")
        return results

    # Test translations
    times = []
    for phrase in test_phrases:
        try:
            t0 = time.time()
            translated = lm.translate(phrase)
            elapsed = time.time() - t0
            times.append(elapsed)

            result = {
                "source": phrase,
                "translated": translated,
                "time": elapsed,
                "status": "OK",
            }
            results["translations"].append(result)
            print(f"  [{elapsed:.3f}s] '{phrase}' → '{translated}'")
        except Exception as e:
            result = {
                "source": phrase,
                "translated": f"ERROR: {e}",
                "time": 0,
                "status": "ERROR",
            }
            results["translations"].append(result)
            results["errors"].append(f"TRANSLATE FAILED for '{phrase}': {e}")
            print(f"  ERROR: '{phrase}' → {e}")

    if times:
        results["avg_time"] = sum(times) / len(times)
        print(f"  Average translation time: {results['avg_time']:.3f}s")

    return results


def quality_assessment(result: dict) -> str:
    """Basic quality check on translation output."""
    if not result["load_success"]:
        return "FAIL — Model did not load"

    if not result["translations"]:
        return "FAIL — No translations produced"

    # Check if translations are empty or same as source
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

    # Check if translation looks different enough
    sample = result["translations"][0]["translated"]
    source = result["translations"][0]["source"]
    if sample.lower().strip() == source.lower().strip():
        return "WARN — Translation same as source (possible pass-through)"

    return "PASS — Translations appear valid"


def main():
    print("=" * 80)
    print("COMPREHENSIVE LANGUAGE QA")
    print("=" * 80)
    print(f"Testing {len(LANGUAGE_MODELS)} languages with {len(TEST_PHRASES)} phrases each")
    print("This will take several minutes (models download on first use)")
    print("-" * 80)

    all_results = []
    total_start = time.time()

    for lang_code in sorted(LANGUAGE_MODELS.keys()):
        result = test_single_language(lang_code, TEST_PHRASES)
        result["quality"] = quality_assessment(result)
        all_results.append(result)

    total_time = time.time() - total_start

    # Summary report
    print("\n" + "=" * 80)
    print("QA SUMMARY REPORT")
    print("=" * 80)
    print(f"{'Language':<12} {'Code':<6} {'Load':<8} {'Avg Time':<12} {'Quality':<30}")
    print("-" * 80)

    pass_count = 0
    fail_count = 0
    for r in all_results:
        status = r["quality"]
        if status.startswith("PASS"):
            pass_count += 1
        else:
            fail_count += 1

        load_str = f"{r['load_time']:.1f}s" if r["load_success"] else "FAIL"
        time_str = f"{r['avg_time']:.3f}s" if r["avg_time"] > 0 else "N/A"

        print(f"{r['name']:<12} {r['code']:<6} {load_str:<8} {time_str:<12} {status:<30}")

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
                    print(f"  - '{t['source']}' → {t['translated']}")

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
