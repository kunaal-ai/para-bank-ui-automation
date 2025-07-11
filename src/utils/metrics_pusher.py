#!/usr/bin/env python3
"""
Metrics pusher for Para Bank UI Automation

This script pushes test metrics to a Prometheus Pushgateway, which can then be
scraped by Prometheus. This approach ensures metrics are available even after tests complete.
"""

import time
import os
import sys
import psutil
from prometheus_client import Counter, Histogram, Gauge, push_to_gateway, CollectorRegistry

# Create a registry
registry = CollectorRegistry()

# Define metrics with the registry
TEST_RUNS = Counter('test_runs_total', 'Total number of test runs', registry=registry)
TEST_PASSES = Counter('test_passes_total', 'Total number of passed tests', registry=registry)
TEST_FAILURES = Counter('test_failures_total', 'Total number of failed tests', registry=registry)
TEST_DURATION = Histogram('test_duration_seconds', 'Test execution time in seconds',
                         buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0],
                         registry=registry)
MEMORY_USAGE = Gauge('test_memory_usage_bytes', 'Memory usage during test execution', registry=registry)
TEST_PERFORMANCE = Histogram('test_performance_score', 'Test performance score (1-100)',
                           buckets=[20, 40, 60, 80, 100],
                           registry=registry)

# Function to push metrics
def push_metrics(job_name='para-bank-tests'):
    """Push metrics to the Pushgateway"""
    try:
        push_to_gateway('localhost:9091', job=job_name, registry=registry)
        print(f"Metrics pushed successfully to Pushgateway")
    except Exception as e:
        print(f"Error pushing metrics: {e}")

# Test execution metrics
class TestMetrics:
    """Context manager for tracking test execution metrics"""
    def __init__(self, test_name):
        self.test_name = test_name
        self.start_time = None
        self.process = psutil.Process()
        
    def __enter__(self):
        self.start_time = time.time()
        TEST_RUNS.inc()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        TEST_DURATION.observe(duration)
        
        # Track memory usage
        memory_info = self.process.memory_info()
        MEMORY_USAGE.set(memory_info.rss)
        
        # Calculate performance score (100 - duration in seconds, capped at 100)
        performance_score = max(0, min(100, 100 - duration))
        TEST_PERFORMANCE.observe(performance_score)
        
        if exc_type is None:
            TEST_PASSES.inc()
        else:
            TEST_FAILURES.inc()
            
        # Push metrics after each test
        push_metrics()
        
        return False  # Don't suppress exceptions

# For direct execution
if __name__ == "__main__":
    # Example usage
    TEST_RUNS.inc()
    TEST_PASSES.inc()
    push_metrics()
    print("Metrics pushed to Pushgateway")
