#!/bin/bash
# Helper script to run the cleanup utility

# Make sure we're in the project root
cd "$(dirname "$0")"

# Run the cleanup script
python3 scripts/cleanup.py
