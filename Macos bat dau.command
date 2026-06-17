#!/bin/bash
cd "$(dirname "$0")"

echo "==================================================="
echo "    Laptop Battery Test - macOS Launcher"
echo "==================================================="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 is not installed or not in PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it does not exist
if [ ! -d "battery_test_env" ]; then
    echo "Creating virtual environment (battery_test_env)..."
    python3 -m venv battery_test_env
fi

# Activate environment and install/upgrade requirements
if [ -f "battery_test_env/bin/activate" ]; then
    echo "Activating virtual environment..."
    source battery_test_env/bin/activate
    echo "Installing/Updating dependencies from requirements.txt..."
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Installing/Updating dependencies globally..."
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
fi

echo
echo "==================================================="
echo "    Dependencies ready! Starting Battery Test..."
echo "==================================================="
echo
# Run the test wrapped in caffeinate to prevent macOS display and system sleep
caffeinate -i -d python3 test.py
