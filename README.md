# FCC ULS Land Mobile Database Downloader

A Python application that automatically downloads, processes, and stores FCC ULS Land Mobile radio data in a local SQLite database with comprehensive callsign lookup capabilities.

## Quick Start

```bash
# Install dependencies
uv sync

# Download and process FCC data (first run)
uv run python main.py --download-now

# Look up any callsign
uv run python scripts/callsign_lookup.py KA21141
```

## Features

- Automated Downloads: Daily scheduled downloads of FCC ULS data
- Large Dataset Processing: Handles 27+ million records efficiently  
- Comprehensive Lookup: License, licensee, frequency, and location data
- Robust Downloads: Uses curl with retry logic for reliability
- Cross-Platform: Linux, macOS, and Windows support
- **Web Interface**: Flask-based web application for browser-based searching
- **Multiple Interfaces**: Command-line tools and web interface available

## Disk Space Management

Downloads can consume significant disk space (~7.5GB per update). The system includes automatic cleanup:

- **Automatic cleanup**: Removes files older than 7 days after successful downloads
- **Manual cleanup**: Use `uv run python scripts/cleanup_downloads.py --help` for options
- **Configuration**: Adjust retention in `config.py` (FILE_CLEANUP_DAYS)

See `docs/DISK_SPACE_MANAGEMENT.md` for detailed cleanup options.

## Web Application

The project includes a Flask-based web interface for easier searching:

```bash
# Start development server
./scripts/run_webapp.sh

# Or start production server
./scripts/run_webapp_production.sh
```

Access the web interface at http://localhost:5001 (development) or http://localhost:8000 (production).

Features:
- **Callsign Lookup**: Detailed license information
- **Licensee Search**: Search by actual licensee name
- **Frequency Search**: Find licenses by frequency with tolerance
- **State Filtering**: Filter results by state
- **Responsive Design**: Works on desktop and mobile

See `webapp/README.md` for detailed web application documentation.
## Command Line Usage

### Main Application
```bash
uv run python main.py [OPTIONS]

Options:
  --download-now    Download and process data immediately
  --schedule       Run as scheduled service (daily at 2 AM)
  --stats          Show database statistics
  --dataset-info   Show FCC dataset information
```

### Callsign Lookup
```bash
uv run python scripts/callsign_lookup.py <CALLSIGN>
```

## Database Schema

- licenses: License header information (call signs, status, dates)
- entities: Licensee information (names, addresses, contacts)
- frequencies: Frequency assignments (MHz, power, emission types)
- locations: Geographic locations (coordinates, elevations)
- antennas: Antenna specifications
- application_purpose: Application purpose codes

See docs/DATABASE_SCHEMA.md for complete documentation.

## Version

v1.0.0 (2025-08-17) - Initial release with full FCC ULS support
