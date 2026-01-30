#!/bin/bash

echo "========================================"
echo "Starting UX Transcript Analysis Backend"
echo "========================================"
echo

cd backend

echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found!"
    echo "Please install Python 3.8+"
    exit 1
fi

echo
echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo
echo "Starting Flask server..."
echo
python3 app.py
