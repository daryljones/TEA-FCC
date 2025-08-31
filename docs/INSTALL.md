# Installation and Usage Guide

## Quick Installation

1. **Install uv** (recommended Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd TEA-FCC
   uv sync
   ```

3. **First run**:
   ```bash
   uv run python main.py --download-now
   ```
   
   This will:
   - Download ~1GB of FCC data
   - Process 27+ million records  
   - Create `fcc_uls.db` database
   - Take 5-15 minutes

## Daily Usage

### Lookup Callsigns
```bash
# Look up any callsign
uv run python callsign_lookup.py KA21141
uv run python callsign_lookup.py WQO214
```

### Update Database
```bash
# Manual update
uv run python main.py --download-now

# Check statistics
uv run python main.py --stats
```

### Schedule Automatic Updates

#### Linux (systemd)
```bash
sudo cp fcc-uls-downloader.service /etc/systemd/system/
sudo cp fcc-uls-downloader.timer /etc/systemd/system/
sudo systemctl enable fcc-uls-downloader.timer
sudo systemctl start fcc-uls-downloader.timer
```

#### macOS (launchd)
```bash
cp com.local.fcc-uls-downloader.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.local.fcc-uls-downloader.plist
```

#### Cron (any Unix system)
```bash
# Add to crontab - runs daily at 2 AM
0 2 * * * cd /path/to/TEA-FCC && uv run python main.py --download-now
```

## Troubleshooting

### Download Issues
```bash
# Check if FCC servers are responding
uv run python main.py --dataset-info

# Manual download if automatic fails
uv run python manual_download_helper.py
```

### Database Issues
```bash
# Rebuild database from scratch
rm fcc_uls.db
uv run python main.py --download-now
```

### Dependencies
```bash
# Alternative to uv - use pip
pip install requests tqdm schedule

# Make sure curl is installed
curl --version
```

## File Locations

- **Database**: `fcc_uls.db` (created in project directory)
- **Downloads**: `downloads/` directory (temporary, can be deleted)
- **Logs**: Console output (can redirect to file)

## System Requirements

- Python 3.11+
- curl (for downloads)
- 3GB free disk space
- Internet connection for downloads
