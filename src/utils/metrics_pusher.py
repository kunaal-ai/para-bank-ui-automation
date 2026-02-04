#!/usr/bin/env python3
"""
Metrics pusher for Para Bank UI Automation

This script pushes test metrics to a Prometheus Pushgateway, which can then be
scraped by Prometheus. This approach ensures metrics are available even after
tests complete.
"""

import time
import types
from typing import Optional, Type

import psutil
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    delete_from_gateway,
    push_to_gateway,
)

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
TEST_RERUNS = Counter(
    "test_reruns_total",
    "Total number of test reruns (flakes)",
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
def push_metrics(job_name: str = "para-bank-tests", grouping_key: Optional[dict] = None) -> None:
    """Push metrics to the Pushgateway

    Args:
        job_name: Name of the job to identify the metrics in Prometheus
        grouping_key: Optional dictionary of labels for grouping metrics (e.g., {"worker": "gw0"})
    """
    try:
        push_to_gateway(
            "localhost:9091", job=job_name, registry=registry, grouping_key=grouping_key
        )
        print(
            f"Metrics pushed successfully to Pushgateway (job={job_name}, grouping={grouping_key})"
        )
    except Exception as e:
        print(f"Error pushing metrics: {e}")


def cleanup_metrics(job_name: str = "para-bank-tests") -> None:
    """Cleanup old metrics from the Pushgateway.

    This attempts to delete all potential grouping keys used in this project
    to ensure the next run starts with a clean slate.
    """
    # 1. Delete metrics with no grouping keys (legacy or default pushes)
    try:
        delete_from_gateway("localhost:9091", job=job_name, grouping_key=None)
    except Exception:  # nosec B110
        pass

    # 2. Delete metrics with worker labels (current strategy)
    common_workers = ["master"] + [f"gw{i}" for i in range(32)]
    for worker in common_workers:
        try:
            delete_from_gateway("localhost:9091", job=job_name, grouping_key={"worker": worker})
        except Exception:  # nosec B110
            pass


# Test execution metrics
class ExecutionMetrics:
    """Context manager for tracking test execution metrics"""

    def __init__(self, test_name: str = "default", grouping_key: Optional[dict] = None) -> None:
        self.test_name = test_name
        self.grouping_key = grouping_key
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
            elif self.status == "rerun":
                TEST_RERUNS.inc()
            else:
                TEST_FAILURES.inc()
        elif exc_type is None:
            TEST_PASSES.inc()
        else:
            TEST_FAILURES.inc()

        # Push metrics after each test with the grouping key
        push_metrics(grouping_key=self.grouping_key)


# For direct execution
if __name__ == "__main__":
    # Example usage
    TEST_RUNS.inc()
    TEST_PASSES.inc()
    push_metrics()
    print("Metrics pushed to Pushgateway")
