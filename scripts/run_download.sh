#!/bin/bash

# FCC ULS Downloader Service Script
# This script can be used with cron or systemd to schedule daily downloads

# Set the working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the downloader
uv run python main.py --download-now

# Log the execution
echo "$(date): FCC ULS download completed" >> scheduler.log
