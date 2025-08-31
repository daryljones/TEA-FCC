#!/bin/bash
# FCC ULS Web Application Production Launcher
# This script starts the Flask web application using gunicorn for production

echo "Starting FCC ULS Web Lookup Tool (Production Mode)..."
echo "Make sure the database exists by running: uv run python main.py"
echo ""

# Check if database exists
if [ ! -f "fcc_uls.db" ]; then
    echo "❌ Database not found! Please run 'uv run python main.py' first to create the database."
    exit 1
fi

echo "✅ Database found"
echo "🚀 Starting web application in production mode..."
echo "📡 Local access: http://localhost:8000"
echo "🌐 Network access: http://$(hostname -I | awk '{print $1}'):8000"
echo "   (Use the network address for remote testing)"
echo ""

# Start with gunicorn
cd webapp
uv run gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
