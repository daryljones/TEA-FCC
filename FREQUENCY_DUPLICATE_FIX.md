# Frequency Search Duplicate Records Fix

## Problem
When searching by frequency, duplicate records were being displayed for the same callsign/frequency combination. For example, searching for 488.4625 MHz would show multiple entries for the same callsign like WIM972, each with different power levels or emission designators.

## Root Cause
The SQL query was using `DISTINCT` but selecting individual power and emission fields, which created unique combinations for each power/emission variant. Since the same callsign could have multiple power levels or emission types on the same frequency, each combination appeared as a separate "distinct" record.

**Before (Problematic Query):**
```sql
SELECT DISTINCT f.call_sign, f.frequency_assigned, f.power_erp, f.power_output,
       f.emission_designator, l.license_status, e.entity_name, e.city, e.state
FROM frequencies f...
```

## Solution
Modified both `enhanced_lookup.py` and `webapp/app.py` to use `GROUP BY` with aggregation functions to consolidate multiple power/emission values per callsign/frequency combination.

**After (Fixed Query):**
```sql
SELECT f.call_sign, f.frequency_assigned,
       GROUP_CONCAT(DISTINCT CASE WHEN f.power_erp IS NOT NULL THEN f.power_erp || 'W (ERP)' END) as erp_powers,
       GROUP_CONCAT(DISTINCT CASE WHEN f.power_output IS NOT NULL THEN f.power_output || 'W (Out)' END) as output_powers,
       GROUP_CONCAT(DISTINCT f.emission_designator) as emissions,
       l.license_status, e.entity_name, e.city, e.state
FROM frequencies f...
GROUP BY f.call_sign, f.frequency_assigned
```

## Changes Made

### 1. enhanced_lookup.py
- **Modified:** `search_by_frequency()` method
- **Added:** GROUP BY clause on callsign and frequency
- **Added:** GROUP_CONCAT aggregation for powers and emissions
- **Updated:** Display format to handle aggregated values
- **Result:** Each callsign appears only once per frequency

### 2. webapp/app.py  
- **Modified:** `search_by_frequency()` method
- **Added:** GROUP BY clause on callsign and frequency
- **Added:** MAX() aggregation for power, GROUP_CONCAT for emissions
- **Result:** Eliminates duplicates in web interface

### 3. Display Improvements
- **Before:** Single power/emission per line, multiple duplicates
- **After:** Aggregated powers and emissions, single line per callsign/frequency
- **Format:** "50.0W (ERP), 100.0W (Out)" for powers, "FB8,MO,FB2" for emissions

## Testing Results

**Test:** `python enhanced_lookup.py --freq 488.4625 --limit 5`

**Before Fix:**
```
WIG236       488.4625     250W       FB8        PDV Spectrum Holdin
WIG236       488.4625     250W       FB8        PDV Spectrum Holdin  
WIG236       488.4625     1000W      FB8        PDV Spectrum Holdin
WIG236       488.4625     1000W      FB8        PDV Spectrum Holdin
WIG236       488.4625     50W        MO         PDV Spectrum Holdin
```

**After Fix:**
```
WIG236       488.4625     50.0W (Out), 1  FB8,MO          PDV Spectrum Holdin
WII972       488.4625     60.0W (Out), 3  FB2S,FB2,MO     SOUTH SAN FRANCISCO
WIJ793       488.4625     90.0W (Out), 1  FB8             SHELL CHEMICAL COMP
WIL579       488.4625     25.0W (ERP), 5  FB8,MO          PDV Spectrum Holdin
WIL881       488.4625     75.0W (Out), 1  FB4             PAYNES PARKING DESI
```

## Benefits
- ✅ **Eliminates duplicate records** - Each callsign appears only once per frequency
- ✅ **Shows complete information** - All power levels and emissions aggregated
- ✅ **Improved readability** - Cleaner, more concise output
- ✅ **Consistent behavior** - Same fix applied to both CLI and web interfaces
- ✅ **Better performance** - Fewer records to process and display

## Files Modified
- `enhanced_lookup.py` - CLI frequency search
- `webapp/app.py` - Web interface frequency search  
- `FREQUENCY_DUPLICATE_FIX.md` - This documentation
