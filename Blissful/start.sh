#!/bin/bash

echo "========================================"
echo "Blissful - Lidarr Music Downloader"
echo "========================================"
echo ""

# Ask if user wants to run tests first
read -p "Run setup tests first? (y/n): " RUNTEST

if [ "$RUNTEST" = "y" ] || [ "$RUNTEST" = "Y" ]; then
    echo ""
    echo "Running setup tests..."
    echo "========================================"
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    $PYTHON_CMD test_setup.py
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "Setup tests failed! Please fix issues before starting."
        exit 1
    fi
    
    echo ""
    echo "All tests passed!"
    echo ""
    read -p "Press Enter to continue..."
fi

echo ""
echo "Prerequisites Check:"
echo "===================="

# Check Python
if command -v python3 &> /dev/null; then
    echo "[OK] Python found: $(python3 --version)"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "[OK] Python found: $(python --version)"
    PYTHON_CMD="python"
else
    echo "[X] Python not found! Please install Python 3.8 or higher."
    exit 1
fi

# Check FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "[OK] FFmpeg found"
else
    echo "[!] FFmpeg not found! Some features may not work."
    echo "    Install with: sudo apt install ffmpeg (Debian/Ubuntu)"
    echo "               or: brew install ffmpeg (macOS)"
fi

echo ""
echo "Installing/Updating dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "===================="
echo "Starting Blissful Microservice..."
echo ""
echo "Web Interface: http://localhost:7373"
echo ""
echo "To test the API (in another terminal):"
echo "  $PYTHON_CMD test_api.py"
echo ""
echo "Press Ctrl+C to stop the service"
echo "===================="
echo ""

$PYTHON_CMD Blissful.py
