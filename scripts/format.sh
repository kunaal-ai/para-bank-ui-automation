#!/bin/bash

# Format Python code with Black and isort
echo "Running Black..."
black .

echo "Running isort..."
isort .

echo "Formatting complete!"
