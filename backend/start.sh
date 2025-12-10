#!/bin/bash
# Start PySpark Ride-Sharing Matchmaking Backend
# Unix/Linux/macOS Shell Script

echo "========================================"
echo "PySpark Backend Startup Script"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[INFO] Python found:"
python3 --version
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    echo "[SUCCESS] Virtual environment created"
    echo
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
echo

# Install/Update dependencies
echo "[INFO] Installing dependencies from requirements.txt..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "[SUCCESS] Dependencies installed"
echo

# Start Flask server
echo "========================================"
echo "Starting Flask Server with PySpark Backend..."
echo "========================================"
echo
echo "Server will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo

python3 app.py

# Deactivate virtual environment on exit
deactivate
