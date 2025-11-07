#!/bin/bash

# WeBook Startup Script

echo "Starting WeBook - Manga & Novel Recommendation System"
echo "======================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Run the application
echo "Starting WeBook server..."
echo "Access the application at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
python run.py
