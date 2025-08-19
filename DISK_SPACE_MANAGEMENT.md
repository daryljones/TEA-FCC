# FCC Downloads Disk Space Management

## Overview

The FCC ULS downloader can consume significant disk space over time as it downloads and extracts large datasets. This document explains the automated and manual cleanup options available to manage disk space.

## Current Disk Usage

Each complete download cycle creates:
- **ZIP files**: ~1GB (licenses ~378MB + applications ~637MB)
- **Extracted data**: ~6.4GB (extracted .dat files)
- **Total per download**: ~7.4GB

## Automatic Cleanup

### Built-in Cleanup (Added)
The main downloader now includes automatic cleanup functionality:

- **Triggers**: Runs automatically after successful downloads
- **Retention**: Keeps files for 7 days by default
- **What's cleaned**: Old ZIP files and extracted directories
- **Configuration**: Controlled by `config.py` settings

### Configuration Options
In `config.py`:
```python
ENABLE_FILE_CLEANUP = True        # Enable/disable automatic cleanup
FILE_CLEANUP_DAYS = 7            # Days to keep files (default: 7)
CLEANUP_ON_SUCCESS = True        # Auto-cleanup after successful downloads
```

## Manual Cleanup Tools

### 1. Cleanup Script
Use the dedicated cleanup script for manual control:

```bash
# List all download files and their sizes
uv run python cleanup_downloads.py --list

# Dry run - see what would be removed (7 days retention)
uv run python cleanup_downloads.py --days 7

# Actually remove old files
uv run python cleanup_downloads.py --days 7 --execute

# More aggressive cleanup (keep only 1 day)
uv run python cleanup_downloads.py --days 1 --execute
```

### 2. Manual File Removal
For immediate space recovery:

```bash
# Remove all old extracted directories
rm -rf downloads/extracted_LM_*_old_date

# Remove old ZIP files
rm downloads/LM_*_old_date.zip

# Keep only current working files
```

## Disk Space Monitoring

### Check Current Usage
```bash
# Total downloads directory size
du -sh downloads/

# Breakdown by file/directory
du -sh downloads/*

# List files with sizes
uv run python cleanup_downloads.py --list
```

### Database Size
The SQLite database itself is relatively small compared to download files:
```bash
# Check database size
ls -lh fcc_uls.db
```

## Recommended Strategies

### For Regular Use
- **Keep automatic cleanup enabled** (7-day retention)
- **Monitor disk space weekly**
- **Adjust retention period** based on available disk space

### For Limited Disk Space
- **Reduce retention to 1-3 days**
- **Run manual cleanup more frequently**
- **Consider external storage** for archival

### For Development/Testing
- **Manual cleanup after each test**
- **Use shorter retention periods**
- **Clean up immediately after successful database rebuild**

## Example Cleanup Commands

```bash
# Check what files exist
uv run python cleanup_downloads.py --list

# Conservative cleanup (keep 7 days)
uv run python cleanup_downloads.py --days 7 --execute

# Aggressive cleanup (keep only current)
uv run python cleanup_downloads.py --days 1 --execute

# Emergency cleanup - manual removal
rm -rf downloads/extracted_LM_*_20250817
rm downloads/LM_*_20250817.zip
```

## File Structure After Cleanup

Typical structure with automatic cleanup:
```
downloads/
├── LM_applications_20250818.zip    # Current applications
├── LM_licenses_20250818.zip        # Current licenses  
├── extracted_LM_applications_20250818/  # Current extracted apps
└── extracted_LM_licenses_20250818/      # Current extracted licenses
```

## Troubleshooting

### If Cleanup Fails
1. **Check permissions**: Ensure write access to downloads directory
2. **Check disk space**: Ensure enough space for cleanup operations
3. **Manual removal**: Use `rm` commands as fallback

### If Space Still Limited
1. **Move database**: Keep database on different drive
2. **Symlink downloads**: Point downloads to external storage
3. **Reduce retention**: Use 1-day retention for minimal space

## Summary

- ✅ **Automatic cleanup enabled** by default (7-day retention)
- ✅ **Manual cleanup tools** available for fine control
- ✅ **Configurable retention periods** 
- ✅ **Monitoring tools** for disk usage tracking
- ✅ **Multiple cleanup strategies** for different use cases

The system now intelligently manages disk space while ensuring reliable access to current FCC data.
