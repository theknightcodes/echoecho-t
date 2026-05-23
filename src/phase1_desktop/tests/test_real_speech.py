#!/usr/bin/env python3
"""
Real-Speech End-to-End Test — EchoEcho-T Phase 1

Runs the full pipeline (Mic → VAD → STT → Translation → TTS) for 60 seconds.
Guides the user through a scripted utterance sequence.
Validates: no punctuation in TTS output, no feedback loops, latency < 3s.

Usage:
    python tests/test_real_speech.py [duration_seconds] [default_language] [log_file]
"""

import sys
import os
import time
import re
import unicodedata
import threading
from datetime import datetime
from collections import deque
from io import TextIOBase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.orchestrator_v2 import Pipeline
from ai.language_manager import LANGUAGE_NAMES
from ai.tts import _sanitize_for_tts


class Tee(TextIOBase):
    """Write to multiple streams simultaneously."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()
        return len(data)

    def flush(self):
        for s in self.streams:
            s.flush()


class RealSpeechTest:
    """End-to-end real-speech test harness."""

    PROMPTS = [
        ("Hello how are you", "English → target language translation"),
        ("switch to Tamil", "Language switch to Tamil"),
        ("Good morning", "English → Tamil translation"),
        ("switch to German", "Language switch back to German"),
    ]

    HALLUCINATION_WORDS = {"dot", "comma", "question mark", "period", "don't", "bye", "hi", "ok"}

    def __init__(self, duration: int = 60, default_lang: str = "ta", log_file: str = None):
        self.duration = duration
        self.default_lang = default_lang
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        if log_file:
            self.log_file = log_file
        else:
            self.log_file = os.path.join(
                self.log_dir, f"e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )

        # Validation state
        self.tts_outputs = []
        self.transcripts = []
        self.switch_events = []
        self.punctuation_violations = []
        self.feedback_artifacts = []
        self.hallucination_hits = []

        self._lock = threading.Lock()
        self._last_tts_time = 0.0
        self._recent_tts_texts = deque(maxlen=10)
        self._test_start = 0.0

    def _log_event(self, tag: str, message: str):
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] [{tag}] {message}")

    def _on_transcript(self, text: str, lang: str):
        self._log_event("STT", f"{lang.upper()}: {text}")
        with self._lock:
            self.transcripts.append({"time": time.time(), "text": text, "lang": lang})
            lower = text.lower().strip()
            # Check hallucination filter bypass
            if len(lower) <= 15 and any(word in lower for word in self.HALLUCINATION_WORDS):
                self.hallucination_hits.append(text)
            # Check feedback loop: transcript resembles a recent TTS output
            for tts in self._recent_tts_texts:
                if lower in tts or tts in lower:
                    self.feedback_artifacts.append(
                        f"Transcript '{text}' resembles TTS '{tts}'"
                    )

    def _on_translation(self, text: str):
        self._log_event("TRANS", text)

    def _on_language_switch(self, lang_code: str, confirmation: str):
        self._log_event("SWITCH", f"→ {LANGUAGE_NAMES.get(lang_code, lang_code)}")
        self._log_event("CONFIRM", confirmation)
        with self._lock:
            self.switch_events.append(
                {"time": time.time(), "lang": lang_code, "text": confirmation}
            )
            self._recent_tts_texts.append(confirmation.lower())

    def _monkeypatch_tts(self, pipeline: Pipeline):
        """Hook into TTS to validate spoken text and detect feedback."""
        original_speak = pipeline.tts.speak

        def speak_hook(text: str):
            clean = _sanitize_for_tts(text)
            # Validate no punctuation remains in what TTS will actually speak
            bad_chars = [ch for ch in clean if unicodedata.category(ch).startswith("P")]
            if bad_chars:
                with self._lock:
                    self.punctuation_violations.append((clean, bad_chars))
            with self._lock:
                self._recent_tts_texts.append(clean.lower())
                self._last_tts_time = time.time()
                self.tts_outputs.append({"time": time.time(), "text": clean})
            return original_speak(text)

        pipeline.tts.speak = speak_hook

    def run(self):
        print("=" * 60)
        print("EchoEcho-T — Real-Speech E2E Test")
        print("=" * 60)
        print(f"Duration: {self.duration}s | Default: {self.default_lang}")
        print(f"Log file: {self.log_file}")
        print("-" * 60)

        os.makedirs(self.log_dir, exist_ok=True)
        with open(self.log_file, "w", buffering=1) as log_fh:
            tee = Tee(sys.stdout, log_fh)
            old_stdout = sys.stdout
            sys.stdout = tee

            try:
                self._run_test()
            finally:
                sys.stdout = old_stdout

    def _run_test(self):
        pipeline = Pipeline(default_lang=self.default_lang)
        self._monkeypatch_tts(pipeline)

        pipeline.on_transcript = self._on_transcript
        pipeline.on_translation = self._on_translation
        pipeline.on_language_switch = self._on_language_switch
        pipeline.on_status = lambda msg: self._log_event("STATUS", msg)

        prompt_interval = self.duration // (len(self.PROMPTS) + 1)
        next_prompt_idx = 0
        next_prompt_time = time.time() + 3  # First prompt after 3s warmup

        self._test_start = time.time()
        try:
            with pipeline:
                while time.time() - self._test_start < self.duration:
                    now = time.time()
                    remaining = int(self.duration - (now - self._test_start))

                    if next_prompt_idx < len(self.PROMPTS) and now >= next_prompt_time:
                        utterance, desc = self.PROMPTS[next_prompt_idx]
                        print("\n" + "=" * 60)
                        print(
                            f"PROMPT {next_prompt_idx + 1}/{len(self.PROMPTS)}: '{utterance}'"
                        )
                        print(f"  Expected: {desc}")
                        print(f"  Time remaining: {remaining}s")
                        print("=" * 60 + "\n")
                        next_prompt_idx += 1
                        next_prompt_time = now + prompt_interval

                    time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[Interrupted by user]")
        except Exception as e:
            print(f"\n[Error] {e}")
            import traceback

            traceback.print_exc()

        self._print_report()

    def _print_report(self):
        print("\n" + "=" * 60)
        print("E2E TEST REPORT")
        print("=" * 60)

        stats = {}
        try:
            stats = self._get_latency_stats()
        except Exception as e:
            print(f"[WARN] Could not read latency stats: {e}")

        checks = []

        # 1. Punctuation check
        if self.punctuation_violations:
            checks.append(
                (
                    "No punctuation in TTS output",
                    False,
                    f"{len(self.punctuation_violations)} violation(s): {self.punctuation_violations[:3]}",
                )
            )
        else:
            checks.append(("No punctuation in TTS output", True, "PASS"))

        # 2. Feedback loop check
        if self.feedback_artifacts:
            checks.append(
                (
                    "No feedback loop artifacts",
                    False,
                    f"{len(self.feedback_artifacts)} artifact(s): {self.feedback_artifacts[:3]}",
                )
            )
        else:
            checks.append(("No feedback loop artifacts", True, "PASS"))

        # 3. Hallucination filter check
        if self.hallucination_hits:
            checks.append(
                (
                    "STT hallucination filter",
                    False,
                    f"{len(self.hallucination_hits)} hit(s): {self.hallucination_hits[:3]}",
                )
            )
        else:
            checks.append(("STT hallucination filter", True, "PASS"))

        # 4. Latency check (sum of mean stage latencies)
        total_mean_ms = stats.get("total_mean_ms", 0)
        total_mean_s = total_mean_ms / 1000.0
        latency_pass = total_mean_s < 3.0 or total_mean_ms == 0
        if latency_pass:
            checks.append(
                (
                    "Latency < 3s",
                    True,
                    f"Mean total: {total_mean_s:.2f}s" if total_mean_ms > 0 else "No latency data",
                )
            )
        else:
            checks.append(
                (
                    "Latency < 3s",
                    False,
                    f"Mean total: {total_mean_s:.2f}s (exceeds 3s)",
                )
            )

        # 5. Translation produced
        tx_count = len(self.tts_outputs)
        checks.append(
            (
                "Translations produced",
                tx_count > 0,
                f"{tx_count} translation(s) produced" if tx_count > 0 else "No translations produced",
            )
        )

        # 6. Language switches
        switch_count = len(self.switch_events)
        checks.append(
            (
                "Language switches detected",
                switch_count > 0,
                f"{switch_count} switch(es) detected" if switch_count > 0 else "No switches detected",
            )
        )

        for name, passed, detail in checks:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name}: {detail}")

        overall = "PASS" if all(c[1] for c in checks) else "FAIL"
        print("-" * 60)
        print(f"OVERALL: {overall}")
        print(f"Log saved to: {self.log_file}")
        print("=" * 60)

    def _get_latency_stats(self):
        """Read latency.csv and compute per-stage means for this test run only."""
        csv_path = os.path.join(self.log_dir, "latency.csv")
        if not os.path.exists(csv_path):
            return {}

        import csv

        by_stage = {}
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ts = float(row.get("timestamp", 0))
                except ValueError:
                    continue
                if ts < self._test_start:
                    continue
                stage = row.get("stage", "")
                try:
                    dur = float(row.get("duration_ms", 0))
                except ValueError:
                    continue
                by_stage.setdefault(stage, []).append(dur)

        if not by_stage:
            return {}

        import numpy as np

        stats = {}
        total = 0.0
        for stage, durs in by_stage.items():
            mean = float(np.mean(durs))
            stats[f"{stage}_mean_ms"] = round(mean, 2)
            total += mean
        stats["total_mean_ms"] = round(total, 2)
        return stats


if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    lang = sys.argv[2] if len(sys.argv) > 2 else "ta"
    log_file = sys.argv[3] if len(sys.argv) > 3 else None
    test = RealSpeechTest(duration=duration, default_lang=lang, log_file=log_file)
    test.run()
