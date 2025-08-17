#!/bin/bash
# AI Trading Bot System Startup Script

echo "🚀 Starting AI Trading Bot System..."
echo "========================================"

# Check if virtual environment should be activated
if [ -f "venv/bin/activate" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check Python availability
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "🔍 Checking system requirements..."

# Start the complete system
echo "🤖 Starting AI Trading Bot..."
python complete_system.py