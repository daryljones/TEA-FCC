# Enhanced FCC ULS Lookup Tool

The enhanced lookup tool (`enhanced_lookup.py`) provides comprehensive search capabilities for the FCC ULS Land Mobile database, supporting queries by callsign, licensee name, and frequency.

## Terminology Clarification

- **LICENSEE**: The actual license holder (entity_type='L' in the database)
- **CONTACT**: The contact person or certifier (entity_type='CL' in the database)

When searching by name, the tool searches actual licensee names, not contact names. Both licensee and contact information are displayed in the results.

## Features

- **Callsign Lookup**: Detailed information for specific call signs
- **Licensee Search**: Find licenses by licensee name (actual license holder)
- **Frequency Search**: Locate all licenses using specific frequencies
- **State Filtering**: Filter results by state
- **Rich Output**: Formatted display with license details, locations, and frequency assignments

## Usage Examples

### Callsign Lookup
```bash
# Look up specific callsign (shows full details)
uv run python enhanced_lookup.py KA21141
uv run python enhanced_lookup.py WQO214
```

### Licensee Name Search
```bash
# Search for licensees containing "MARRIOTT"
uv run python enhanced_lookup.py --name "MARRIOTT"

# Search for city governments
uv run python enhanced_lookup.py --name "CITY OF"

# Search for specific organization in California only
uv run python enhanced_lookup.py --name "MARRIOTT" --state CA

# Search for Texas cities
uv run python enhanced_lookup.py --name "CITY OF" --state TX
```

### Frequency Search
```bash
# Find all licenses on 465.0 MHz (±0.001 MHz default tolerance)
uv run python enhanced_lookup.py --freq 465.0

# Search with custom tolerance (±1.0 MHz)
uv run python enhanced_lookup.py --freq 150.0 --tolerance 1.0

# Find licenses on 450 MHz with ±5 MHz tolerance in Texas
uv run python enhanced_lookup.py --freq 450.0 --tolerance 5.0 --state TX

# Find California licenses on 465 MHz
uv run python enhanced_lookup.py --freq 465.0 --state CA
```

### Advanced Options
```bash
# Limit number of results to 50
uv run python enhanced_lookup.py --name "WALMART" --limit 50

# Filter by state (Texas only)
uv run python enhanced_lookup.py --name "WALMART" --state TX

# Combined search options with state filter (shows up to 150 by default)
uv run python enhanced_lookup.py --freq 465.0 --tolerance 0.5 --state CA
```

## Command Reference

### Basic Syntax
```
python enhanced_lookup.py <QUERY> [OPTIONS]
```

### Query Types
- **Call Sign**: `python enhanced_lookup.py KA21141`
- **Entity/Contact Name**: `python enhanced_lookup.py --name "COMPANY NAME"`
- **Frequency**: `python enhanced_lookup.py --freq 465.0`

### Options
- `--name <name>`: Search by entity/contact name (partial matches supported)
- `--freq <frequency>`: Search by frequency in MHz
- `--tolerance <mhz>`: Frequency search tolerance (default: 0.001 MHz)
- `--state <state>`: Filter results by state (2-letter code, e.g., CA, TX)
- `--limit <number>`: Maximum results to show (default: 150)
- `--help`: Show help information

## Output Format

### Callsign Details
When looking up a specific callsign, you'll see:
- **License Information**: Call sign, status, service type, grant/expiration dates
- **Contact/Entity Information**: Company name or person name, address, phone, email, entity type
- **Frequency Assignments**: All assigned frequencies with power and emission type
- **Locations**: Physical locations with coordinates and antenna details

### Search Results
Search results show a summary table with:
- Call sign
- License status
- Entity/contact name
- Location (city, state)
- Frequency (for frequency searches)
- Power output (for frequency searches)

## Tips

1. **Name searches** are case-insensitive and use wildcard matching (search term + `%`)
2. **Frequency searches** use MHz units (e.g., 465.0 for 465 MHz)
3. **Tolerance** helps find nearby frequencies (useful for band searches)
4. **State filtering** uses 2-letter codes (CA, TX, NY, FL, etc.)
5. **Limit** controls how many results to display (default: 150, helpful for broad searches)
6. Use quotes around multi-word names: `--name "CITY OF ATLANTA"`
7. **Combine filters** for precise searches: `--name "HOTEL" --state CA`
8. **Entity vs Contact**: The "entity_name" field may contain company names or contact persons, not necessarily the legal licensee

## Examples by Use Case

### Finding Hotel Chains by State
```bash
uv run python enhanced_lookup.py --name "MARRIOTT" --state CA
uv run python enhanced_lookup.py --name "HILTON" --state NY
uv run python enhanced_lookup.py --name "HYATT" --state FL
```

### Finding Government Entities by State
```bash
uv run python enhanced_lookup.py --name "COUNTY OF" --state TX
uv run python enhanced_lookup.py --name "CITY OF" --state CA
uv run python enhanced_lookup.py --name "STATE OF" --state NY
```

### Frequency Band Analysis by State
```bash
# California UHF business band
uv run python enhanced_lookup.py --freq 450.0 --tolerance 20.0 --state CA

# Texas VHF high band
uv run python enhanced_lookup.py --freq 150.0 --tolerance 10.0 --state TX

# Florida 800 MHz band
uv run python enhanced_lookup.py --freq 800.0 --tolerance 25.0 --state FL
```

### Regional Corporate Research
```bash
# Find all California Walmart locations (up to 150 results)
uv run python enhanced_lookup.py --name "WALMART" --state CA

# Research Texas utilities
uv run python enhanced_lookup.py --name "ELECTRIC" --state TX --limit 20
uv run python enhanced_lookup.py --name "POWER" --state TX --limit 20
```

## Error Handling

The tool provides helpful error messages and suggestions:
- Invalid callsigns show similar callsign suggestions
- Failed searches indicate no matches found
- Invalid frequencies or parameters show clear error messages

## Performance Notes

- Large searches (high limits, broad tolerances) may take longer
- Database is indexed for efficient callsign and frequency lookups
- Name searches scan the full entities table and may be slower
