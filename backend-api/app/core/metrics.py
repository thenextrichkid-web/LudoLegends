"""Metrics collection — in-memory counters for business + system metrics."""

import time
import threading
from collections import defaultdict
from datetime import datetime, timezone


class MetricsCollector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._start_time = time.time()

    def increment(self, name: str, value: int = 1):
        self._counters[name] += value

    def decrement(self, name: str, value: int = 1):
        self._counters[name] -= value

    def set_gauge(self, name: str, value: float):
        self._gauges[name] = value

    def observe(self, name: str, value: float):
        self._histograms[name].append(value)
        if len(self._histograms[name]) > 1000:
            self._histograms[name] = self._histograms[name][-500:]

    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    def get_histogram_stats(self, name: str) -> dict:
        values = self._histograms.get(name, [])
        if not values:
            return {"count": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
        sorted_v = sorted(values)
        n = len(sorted_v)
        return {
            "count": n,
            "avg": round(sum(sorted_v) / n, 3),
            "p50": sorted_v[int(n * 0.5)] if n > 0 else 0,
            "p95": sorted_v[int(n * 0.95)] if n > 1 else sorted_v[-1],
            "p99": sorted_v[int(n * 0.99)] if n > 2 else sorted_v[-1],
            "max": sorted_v[-1],
        }

    def snapshot(self) -> dict:
        return {
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                name: self.get_histogram_stats(name)
                for name in self._histograms
            },
        }

    def reset(self):
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._start_time = time.time()


metrics = MetricsCollector()
