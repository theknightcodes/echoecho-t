import csv
import time
import os
import threading
from collections import deque
from dataclasses import dataclass, asdict
from typing import Optional

"""
Latency Logger — Phase 1

Tracks timing for each pipeline stage and end-to-end latency.
Outputs to CSV for analysis.
"""


@dataclass
class LatencyRecord:
    timestamp: float
    stage: str
    duration_ms: float
    details: str = ""


class LatencyLogger:
    def __init__(self, log_path: str = "logs/latency.csv"):
        self.log_path = log_path
        self.records = deque(maxlen=10000)
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["timestamp", "stage", "duration_ms", "details"],
                )
                writer.writeheader()

    def log(self, stage: str, duration_ms: float, details: str = ""):
        record = LatencyRecord(
            timestamp=time.time(),
            stage=stage,
            duration_ms=duration_ms,
            details=details,
        )
        self.records.append(record)
        self._write(record)

    def _write(self, record: LatencyRecord):
        with self._lock:
            with open(self.log_path, "a", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["timestamp", "stage", "duration_ms", "details"],
                )
                writer.writerow(asdict(record))

    def summary(self) -> dict:
        """Return statistics for each stage."""
        from collections import defaultdict

        by_stage = defaultdict(list)
        for r in self.records:
            by_stage[r.stage].append(r.duration_ms)

        stats = {}
        for stage, durations in by_stage.items():
            import numpy as np

            stats[stage] = {
                "count": len(durations),
                "mean_ms": round(float(np.mean(durations)), 2),
                "min_ms": round(float(np.min(durations)), 2),
                "max_ms": round(float(np.max(durations)), 2),
                "p95_ms": round(float(np.percentile(durations, 95)), 2),
            }
        return stats

    def report(self):
        """Print formatted latency report."""
        stats = self.summary()
        print("\n" + "=" * 60)
        print("Latency Report")
        print("=" * 60)
        print(f"{'Stage':<20} {'Count':<8} {'Mean':<10} {'Min':<10} {'Max':<10} {'P95':<10}")
        print("-" * 60)
        total_mean = 0
        for stage, s in sorted(stats.items()):
            print(
                f"{stage:<20} {s['count']:<8} {s['mean_ms']:<10.2f} {s['min_ms']:<10.2f} {s['max_ms']:<10.2f} {s['p95_ms']:<10.2f}"
            )
            total_mean += s["mean_ms"]
        print("-" * 60)
        print(f"{'TOTAL (mean)':<20} {'':<8} {total_mean:<10.2f}")
        print("=" * 60)


class Timer:
    """Context manager for timing a block of code."""

    def __init__(self, logger: LatencyLogger, stage: str, details: str = ""):
        self.logger = logger
        self.stage = stage
        self.details = details
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self.start) * 1000
        self.logger.log(self.stage, elapsed, self.details)
