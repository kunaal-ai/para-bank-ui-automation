#!/bin/bash

echo "=== Testing Security Scanning Setup ==="

# Install security tools if not already installed
echo "Installing security tools..."
pip install bandit pip-audit

# Run dependency security scan
echo "Running dependency security scan..."
if [ -f "requirements.txt" ]; then
    pip-audit -r requirements.txt -o safety-report.json
    echo "✓ Dependency scan completed"
else
    echo "ERROR: requirements.txt not found"
    exit 1
fi

# Run code security scan
echo "Running code security scan..."
if [ -d "src" ] || [ -d "tests" ]; then
    bandit -c .bandit.yaml -r src/ tests/ -o bandit-report.json
    echo "✓ Code scan completed"
else
    echo "ERROR: src/ or tests/ directory not found"
    exit 1
fi

echo "=== Security Scanning Test Completed Successfully ===" 