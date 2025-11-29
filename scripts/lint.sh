#!/bin/bash

# Run all linters and code quality checks
set -e

echo "Running Flake8..."
flake8 src/

echo "Running Pylint..."
pylint --rcfile=pyproject.toml src/

echo "Running Bandit..."
bandit -r src/ -c pyproject.toml

echo "Running pip-audit..."
pip-audit -r requirements.txt

echo "All linting checks passed!"
