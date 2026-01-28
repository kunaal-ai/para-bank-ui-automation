#!/usr/bin/env python3
"""
Metrics pusher for Para Bank UI Automation

This script pushes test metrics to a Prometheus Pushgateway, which can then be
scraped by Prometheus. This approach ensures metrics are available even after
tests complete.
"""

import time
import types
from typing import Any, Optional, Type

import psutil
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, push_to_gateway

# Create a registry
registry = CollectorRegistry()

# Define metrics with the registry
TEST_RUNS = Counter("test_runs_total", "Total number of test runs", registry=registry)
TEST_PASSES = Counter("test_passes_total", "Total number of passed tests", registry=registry)
TEST_FAILURES = Counter(
    "test_failures_total",
    "Total number of failed tests",
    registry=registry,
)
TEST_SKIPPED = Counter(
    "test_skipped_total",
    "Total number of skipped tests",
    registry=registry,
)
TEST_DURATION = Histogram(
    "test_duration_seconds",
    "Test execution time in seconds",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0],
    registry=registry,
)
MEMORY_USAGE = Gauge(
    "test_memory_usage_bytes",
    "Memory usage during test execution",
    registry=registry,
)
TEST_PERFORMANCE = Histogram(
    "test_performance_score",
    "Test performance score (1-100)",
    buckets=[20, 40, 60, 80, 100],
    registry=registry,
)


# Function to push metrics
def push_metrics(metrics: Optional[Any] = None, job_name: str = "para-bank-tests") -> None:
    """Push metrics to the Pushgateway

    Args:
        metrics: Optional TestMetrics object (for backward compatibility)
        job_name: Name of the job to identify the metrics in Prometheus
    """
    try:
        push_to_gateway("localhost:9091", job=job_name, registry=registry)
        print("Metrics pushed successfully to Pushgateway")
    except Exception as e:
        print(f"Error pushing metrics: {e}")


# Test execution metrics
class ExecutionMetrics:
    """Context manager for tracking test execution metrics"""

    def __init__(self, test_name: str = "default") -> None:
        self.test_name = test_name
        self.start_time: Optional[float] = None
        self.process = psutil.Process()
        self.status: Optional[str] = None

    def __enter__(self) -> "ExecutionMetrics":
        self.start_time = time.time()
        TEST_RUNS.inc()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        if self.start_time is None:
            return
        duration = time.time() - self.start_time
        TEST_DURATION.observe(duration)

        # Track memory usage
        memory_info = self.process.memory_info()
        MEMORY_USAGE.set(memory_info.rss)

        # Calculate performance score (100 - duration in seconds, capped)
        performance_score = max(0, min(100, 100 - duration))
        TEST_PERFORMANCE.observe(performance_score)

        if self.status:
            if self.status == "passed":
                TEST_PASSES.inc()
            elif self.status == "skipped":
                TEST_SKIPPED.inc()
            else:
                TEST_FAILURES.inc()
        elif exc_type is None:
            TEST_PASSES.inc()
        else:
            TEST_FAILURES.inc()

        # Push metrics after each test
        push_metrics()


# For direct execution
if __name__ == "__main__":
    # Example usage
    TEST_RUNS.inc()
    TEST_PASSES.inc()
    push_metrics()
    print("Metrics pushed to Pushgateway")
