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
python3 -m pytest \
    tests/test_*.py \
    -v \
    --junitxml=junit.xml \
    --html report.html \
    --self-contained-html

# Check if reports were generated
if [ -f "junit.xml" ] && [ -f "report.html" ]; then
    echo "✓ Test reports generated successfully"
else
    echo "ERROR: Test reports not generated"
    exit 1
fi

echo "=== Jenkinsfile Test Completed Successfully ===" 