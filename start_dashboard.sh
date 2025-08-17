#!/bin/bash
# AI Trading Bot Dashboard Startup Script

echo "🌐 Starting AI Trading Bot Dashboard..."
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

echo "🔍 Starting web dashboard server..."
echo "📊 Dashboard will be available at: http://localhost:8000"
echo "💡 Press Ctrl+C to stop"

# Start the dashboard
python dashboard_server.py