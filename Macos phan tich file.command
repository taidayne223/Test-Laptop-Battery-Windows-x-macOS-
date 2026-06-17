#!/bin/bash
cd "$(dirname "$0")"

echo "==================================================="
echo "    Laptop Battery Test - macOS Log Analyzer"
echo "==================================================="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 is not installed or not in PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Activate environment if present
if [ -f "battery_test_env/bin/activate" ]; then
    source battery_test_env/bin/activate
fi

python3 datetime_calculator.py

echo
echo "==================================================="
