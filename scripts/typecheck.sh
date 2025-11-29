#!/bin/bash

# Run static type checking with mypy
echo "Running mypy..."
mypy src/ --config-file pyproject.toml

echo "Type checking complete!"
