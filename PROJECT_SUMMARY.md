# FCC ULS Land Mobile Database Downloader - Project Summary

## Overview
This project provides a complete solution for downloading the FCC ULS (Universal Licensing System) land mobile database and storing it in a local SQLite database with scheduling capabilities.

## Key Files and Their Purposes

### Core Application Files
- **`main.py`** - Main application with download, processing, and scheduling logic
- **`config.py`** - Configuration settings (database path, URLs, logging, etc.)
- **`pyproject.toml`** - Project dependencies managed by uv

### Utility Scripts
- **`test_connectivity.py`** - Tests FCC server connectivity and database initialization
- **`check_fcc_status.py`** - Comprehensive FCC server status checker with retry logic
- **`discover_urls.py`** - Discovers current FCC download URLs (URLs change weekly)
- **`query_examples.py`** - Database query examples and interactive query tool
- **`schema_inspector.py`** - Database schema inspection and management utility
- **`smart_download.py`** - Smart downloader with automatic retry and error handling

### Scheduling Scripts
- **`run_download.sh`** - Shell script for cron-based scheduling
- **`fcc-uls-downloader.service`** - Systemd service file (Linux)
- **`fcc-uls-downloader.timer`** - Systemd timer file (Linux)
- **`com.local.fcc-uls-downloader.plist`** - macOS launchd configuration

### Documentation
- **`README.md`** - Comprehensive documentation and usage instructions
- **`DATABASE_SCHEMA.md`** - Complete SQLite database schema documentation
- **`PROJECT_SUMMARY.md`** - This file - quick reference guide

## Quick Start Commands

```bash
# Install dependencies
uv sync

# Check FCC server status first
uv run python check_fcc_status.py

# Test setup
uv run python test_connectivity.py

# Check database stats (creates initial database)
uv run python main.py --stats

# Download data immediately (WARNING: Large download)
uv run python main.py --download-now

# Start daily scheduler (runs at 2:00 AM daily)
uv run python main.py --schedule

# Query the database interactively
uv run python query_examples.py --interactive

# Discover current FCC download URLs
uv run python discover_urls.py

# Inspect and manage database schema
uv run python schema_inspector.py --all

# Smart download with retry logic
uv run python smart_download.py --download

# Wait for FCC servers to become available
uv run python check_fcc_status.py --wait-for-ok
```

## Important Notes

### FCC URL Updates
- FCC updates download URLs weekly
- If downloads fail with 404 errors, run `discover_urls.py` to find current URLs
- Update the `file_urls` dictionary in `main.py` with new URLs

### Database Structure
The SQLite database (`fcc_uls.db`) contains:
- `licenses` table: License information
- `entities` table: License holder information  
- `download_history` table: Download attempt tracking

### Performance Considerations
- Initial download can take 30+ minutes
- Database will grow to several GB
- Schedule during off-peak hours
- Ensure sufficient disk space

### Scheduling Options
1. **Built-in scheduler**: `uv run python main.py --schedule`
2. **Cron**: Add `run_download.sh` to crontab
3. **Systemd** (Linux): Use provided service/timer files
4. **Launchd** (macOS): Use provided plist file

## Troubleshooting
1. Network issues: Check `test_connectivity.py` output
2. URL changes: Run `discover_urls.py` and update `main.py`
3. Database errors: Check permissions and disk space
4. Scheduling issues: Verify cron syntax and file permissions

## Data Usage
This tool downloads public FCC data. Users must comply with FCC data usage policies.

## Maintenance
- Weekly: Check for URL updates
- Monthly: Review log files and disk usage
- As needed: Update database schema for FCC format changes
