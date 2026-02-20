"""Latency measurement utility."""
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def measure_latency(func: Callable[[], T]) -> tuple[T, float]:
    """Run func(), return (result, execution_time_seconds)."""
    start = time.perf_counter()
    result = func()
    elapsed = time.perf_counter() - start
    return result, elapsed
