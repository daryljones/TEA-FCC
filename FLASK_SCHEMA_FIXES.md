# Flask Web Application Database Schema Fixes

## Issue Summary
The Flask web application was failing when searching for WIM449 due to column name mismatches between the code and the actual database schema.

## Problems Found and Fixed

### 1. Licenses Table Column Issues
**Problem**: Code referenced `radio_service_code` but actual column is `radio_service_type`
**Fix**: Updated SQL query to use correct column name

**Problem**: Code referenced demographic columns that don't match actual schema
**Fix**: Updated to use correct column names:
- `gender` instead of `female`
- `african_american` instead of `black_or_african_american`
- `native_american` instead of `american_indian`
- `hawaiian` instead of `native_hawaiian`
- `ethnicity` instead of `ethnicity_unknown`
- `license_status` instead of `status_code`

### 2. Entities Table Column Issues
**Problem**: Code referenced `dba_name` column that doesn't exist
**Fix**: Removed `dba_name` from SELECT queries

**Problem**: Code referenced `applicant_type_code_admin` but actual column is `applicant_type_code`
**Fix**: Updated column name in queries

### 3. Frequencies Table Column Issues
**Problem**: Code referenced `location_number` and `antenna_number` columns that don't exist
**Fix**: Updated to use actual columns:
- `frequency_number` instead of `location_number`
- `frequency_seq_id` instead of `antenna_number`
- Added `status_code` column

### 4. Template Index Updates
**Problem**: Template indices no longer matched query results after column changes
**Fix**: Updated all template references to use correct array indices

## Files Modified

### `/webapp/app.py`
- Updated `lookup_callsign()` method SQL queries for all tables
- Fixed column names in licenses, entities, frequencies tables
- Maintained proper error handling

### `/webapp/templates/callsign_detail.html`
- Updated license information display indices
- Updated licensee information display indices (removed dba_name reference)
- Updated contact information display indices
- Updated frequency table headers and indices
- Updated location information display indices

## Testing Results
✅ **WIM449 lookup now works correctly**
- Call Sign: WIM449
- Radio Service: PW
- Licensee: San Bruno, City of
- Contact: TEA
- Frequencies: 6 found
- Locations: 5 found

✅ **Web interface displays correctly**
- License information shows proper data
- Licensee and contact information display correctly
- Frequency table shows all 6 frequencies
- Location details show all 5 locations

✅ **API endpoints working**
- `/api/callsign/WIM449` returns proper JSON response
- Error handling works for non-existent callsigns

## Database Schema Reference

### Actual Column Names Used:
**Licenses**: `radio_service_type`, `license_status`, `gender`, `african_american`, `native_american`, `hawaiian`, `asian`, `white`, `ethnicity`

**Entities**: `entity_name`, `entity_type`, `first_name`, `mi`, `last_name`, `suffix`, `phone`, `fax`, `email`, `street_address`, `city`, `state`, `zip_code`, `po_box`, `attention_line`, `frn`, `applicant_type_code`

**Frequencies**: `frequency_number`, `frequency_seq_id`, `frequency_assigned`, `frequency_upper_band`, `frequency_carrier`, `frequency_offset`, `emission_designator`, `power_output`, `power_erp`, `tolerance`, `status_code`

**Locations**: All original columns maintained as they matched the schema correctly

## Notes
- The schema appears to have been updated from the original design
- All changes maintain backward compatibility with existing CLI tools
- Web application now matches the actual database structure
- Error handling preserved throughout all changes
