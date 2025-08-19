# Testing and Development Files Analysis

## Files Identified for Potential Removal

### 1. Testing Scripts
- `test_connectivity.py` - Network connectivity testing
- `test_curl_download.py` - Curl download testing

### 2. Development/Discovery Utilities
- `check_fcc_status.py` - FCC server status checker (may still be useful for monitoring)
- `discover_data_fcc_files.py` - File discovery utility (development-only)
- `discover_urls.py` - URL discovery utility (development-only)
- `manual_download_helper.py` - Manual download helper (superseded by automated downloader)
- `schema_inspector.py` - Database schema inspection (development-only)
- `smart_download.py` - Smart downloader prototype (superseded by main.py)

### 3. Deprecated Files
- `setup_fts_DEPRECATED.py` - Already marked as deprecated
- `remove_fts.py` - One-time utility, no longer needed

### 4. Backup/Generated Files
- `fcc_uls.db.backup_20250818_182023` - Database backup (can be regenerated)
- `create_indexes.sql` - Generated SQL file (can be regenerated from create_indexes.py)

### 5. Service Files (Location-Specific)
- `com.local.fcc-uls-downloader.plist` - macOS service file (may be system-specific)
- `fcc-uls-downloader.service` - Linux systemd service (may be system-specific)
- `fcc-uls-downloader.timer` - Linux systemd timer (may be system-specific)

## Recommendation Categories

### Safe to Remove (Development/Testing Only):
- `discover_data_fcc_files.py`
- `discover_urls.py`
- `manual_download_helper.py`
- `schema_inspector.py`
- `smart_download.py`
- `setup_fts_DEPRECATED.py`
- `remove_fts.py`
- `test_connectivity.py`
- `test_curl_download.py`

### Consider Keeping (Still Useful):
- `check_fcc_status.py` - Useful for monitoring FCC server health
- Service files - Needed for production deployments

### Files to Keep (Core Functionality):
- `main.py` - Core downloader
- `enhanced_lookup.py` - Advanced CLI tool
- `callsign_lookup.py` - Simple CLI tool
- `query_examples.py` - Example queries
- `cleanup_downloads.py` - Disk space management
- `config.py` - Configuration
- `create_indexes.py` - Index management
- All shell scripts (`run_*.sh`)
- All documentation (`.md` files)
- `webapp/` directory - Web interface
