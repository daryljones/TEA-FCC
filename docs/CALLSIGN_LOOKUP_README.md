# FCC ULS Callsign Lookup Tool

A command-line tool to quickly lookup comprehensive information for FCC call signs from the ULS land mobile database.

## Features

🔍 **Quick Lookup**: Get all essential information for any call sign in seconds  
📋 **License Details**: Status, service type, grant/expiration dates  
👤 **Licensee Info**: Name, address, phone, email  
📡 **Frequencies**: All assigned frequencies with power levels and emission types  
📍 **Locations**: Precise coordinates, elevations, and site addresses  
📶 **Antennas**: Equipment specifications (with --detailed flag)  
✅ **Status Indicators**: Clear visual indicators for active/expired licenses  

## Quick Start

```bash
# Basic lookup
python callsign_lookup.py WQXJ123

# Detailed lookup with antenna information
python callsign_lookup.py --detailed WQXJ123

# Use custom database file
python callsign_lookup.py --db /path/to/fcc_uls.db WQXJ123
```

## Installation

Make sure you have the FCC ULS database populated first:

```bash
# Download and populate the database
uv run python main.py --download-now

# Run a lookup
uv run python callsign_lookup.py WQXJ123
```

## Output Example

```
============================================================
🔍 FCC ULS LOOKUP: WQXJ123
============================================================

📋 LICENSE INFORMATION
────────────────────────────────────────
Call Sign:        WQXJ123
Status:           ✅ Active
Service Type:     IG - Industrial/Business Pool
Grant Date:       2020-03-15
Expiration:       2030-03-15

👤 LICENSEE INFORMATION
────────────────────────────────────────
Name:             Example Communications LLC
Address:          123 Main Street
                  Anytown, CA 90210
Phone:            555-123-4567
Email:            contact@example.com

📡 FREQUENCY ASSIGNMENTS
────────────────────────────────────────
Frequency (MHz) Power (W)    Emission     Status
--------------- ------------ ------------ --------
461.1250        25.0         11K0F3E      ✅
466.1250        25.0         11K0F3E      ✅

📍 LOCATION INFORMATION
────────────────────────────────────────
Address:          123 Tower Road
Location:         Anytown, CA (Los Angeles County)
Coordinates:      34°3'22.5"N, 118°14'31.2"W
                  34.056250, -118.242000 (decimal)
Ground Elevation: 125.5 meters (412 feet)
Structure Height: 30.0 meters (98 feet)

📊 SUMMARY
────────────────────────────────────────
Frequencies:      2 assigned
Locations:        1 on file
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `callsign` | **Required** - FCC call sign to lookup |
| `--detailed`, `-d` | Show detailed antenna and technical information |
| `--db DB` | Specify custom database file path |
| `--help`, `-h` | Show help message and exit |

## Use Cases

- **Frequency Coordination**: Check what frequencies are assigned to nearby stations
- **License Verification**: Verify license status and expiration dates  
- **Contact Information**: Find licensee contact details for coordination
- **Site Planning**: Get precise coordinates and antenna heights for coverage analysis
- **Interference Investigation**: Check technical parameters of potentially interfering stations
- **Regulatory Compliance**: Verify license status before operations

## Data Sources

The tool queries the following database tables:
- `licenses` - License status and regulatory information
- `entities` - Licensee contact and address information  
- `frequencies` - Frequency assignments with power and emission data
- `locations` - Site coordinates, elevations, and addresses
- `antennas` - Equipment specifications (detailed mode only)

## Error Handling

The tool provides clear error messages for common issues:
- ❌ Call sign not found in database
- ❌ Database file not found or corrupted
- ⚠️ License expired or expiring soon
- 🕐 License terminated or cancelled

## Tips

1. **Keep Database Current**: Run `python main.py --download-now` regularly to get the latest data
2. **Use Detailed Mode**: Add `--detailed` for antenna specifications and technical details
3. **Batch Lookups**: Create shell scripts to lookup multiple call signs
4. **Coordinate Conversion**: The tool shows both DMS and decimal degree coordinates
5. **Height Conversions**: All heights shown in both meters and feet

## Requirements

- Python 3.7+
- SQLite3 (included with Python)
- Populated FCC ULS database (created by main.py)

## Performance

- Typical lookup time: < 100ms
- Database indexes optimize call sign queries
- Memory usage: < 10MB
- Works with databases containing millions of records
