#!/bin/bash
# FCC ULS Web Application Launcher
# This script starts the Flask web application using uv

echo "Starting FCC ULS Web Lookup Tool..."
echo "Make sure the database exists by running: uv run python main.py"
echo ""

# Check if database exists
if [ ! -f "fcc_uls.db" ]; then
    echo "❌ Database not found! Please run 'uv run python main.py' first to create the database."
    exit 1
fi

echo "✅ Database found"
echo "🚀 Starting web application..."
echo "📡 Local access: http://localhost:5001"
echo "🌐 Network access: http://$(hostname -I | awk '{print $1}'):5001"
echo "   (Use the network address for remote testing)"
echo ""

# Start the web application
uv run python webapp/app.py
