#!/bin/bash

echo "=== Testing Jenkinsfile Setup ==="

# Check if Jenkinsfile exists
if [ ! -f "Jenkinsfile" ]; then
    echo "ERROR: Jenkinsfile not found"
    exit 1
fi

# Create test directory if it doesn't exist
if [ ! -d "tests" ]; then
    mkdir -p tests
fi

# Run tests
echo "Running tests..."
pytest --junitxml=test-results/junit.xml --html=test-results/report.html --self-contained-html

# Verify test reports were generated
if [ ! -f "test-results/junit.xml" ] || [ ! -f "test-results/report.html" ]; then
    echo "ERROR: Test reports not generated"
    exit 1
fi

echo "=== Jenkinsfile Test Completed Successfully ===" 