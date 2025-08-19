# FCC ULS Web Lookup Tool

A Flask web application providing a user-friendly interface to search the FCC ULS Land Mobile database.

## Features

- **Callsign Lookup**: Detailed information for specific call signs
- **Licensee Search**: Find licenses by actual licensee name (license holder)
- **Frequency Search**: Locate all licenses using specific frequencies
- **State Filtering**: Filter results by state
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Search**: AJAX-based search with loading indicators
- **Dark Theme**: Modern dark interface optimized for extended use

## Installation

1. Make sure you have the main FCC ULS database created (run `main.py` first):
   ```bash
   cd /Users/daryl/tmp/TEA-FCC
   uv run python main.py
   ```

2. Flask is already included in the project dependencies. To run the web application:
   ```bash
   cd /Users/daryl/tmp/TEA-FCC
   uv run python webapp/app.py
   ```

3. Open your browser and go to: http://localhost:5001

## Remote Access Configuration

The Flask application is configured to bind to all network interfaces (`0.0.0.0`), making it accessible to remote testers on your local network.

### For Remote Testing:
1. **Find your local IP address**:
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Or use this simpler command
   hostname -I
   ```

2. **Access from remote devices**:
   - Development server: `http://YOUR_IP_ADDRESS:5001`
   - Production server: `http://YOUR_IP_ADDRESS:8000`
   - Example: `http://192.168.1.100:5001`

### Security Considerations:
- The application binds to all interfaces for testing convenience
- For production deployment, consider using a reverse proxy (nginx/Apache)
- Ensure your firewall allows connections on the specified ports
- The database is read-only, so no data modification risks exist

## Quick Start

From the project root directory:
```bash
# Ensure database exists
uv run python main.py

# Start the web application
uv run python webapp/app.py
```

The web application will be available at http://localhost:5001

## Usage

### Callsign Lookup
- Enter a callsign (e.g., KA21141) to view complete license details
- Shows licensee information, contact details, frequencies, and locations

### Licensee Search
- Search by actual licensee name (not contact name)
- Optional state filtering
- Configurable result limits

### Frequency Search
- Search by frequency in MHz
- Configurable tolerance (default: 0.001 MHz)
- State filtering available
- Shows power output and ERP information

## API Endpoints

The web app also provides REST API endpoints:

- `GET /api/callsign/<callsign>` - Lookup specific callsign
- `GET /api/search/licensee?name=<name>&state=<state>&limit=<limit>` - Search licensees
- `GET /api/search/frequency?frequency=<freq>&tolerance=<tol>&state=<state>&limit=<limit>` - Search frequencies

## Directory Structure

```
webapp/
├── app.py              # Main Flask application
├── README.md          # This documentation
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── index.html     # Main search page
│   ├── callsign_detail.html  # Detailed callsign view
│   └── error.html     # Error page
└── static/            # Static files (currently unused)

Note: Dependencies are managed in the root pyproject.toml file using uv.
```

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Font Awesome, Vanilla JavaScript
- **Design**: Dark theme with CSS custom properties
- **Database**: SQLite (shared with main application)
- **Search**: AJAX-based real-time search

## Notes

- The web app uses the same SQLite database as the CLI tools
- Database path is automatically resolved relative to the webapp directory
- All search functionality mirrors the enhanced_lookup.py CLI tool
- Terminology correctly distinguishes between licensees and contacts
