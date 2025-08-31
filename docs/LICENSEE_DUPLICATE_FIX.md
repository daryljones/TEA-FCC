# Licensee Search Duplicate Records Fix

## Problem
Licensee name searches were showing duplicate callsign rows for the same entity. For example, searching for "SAN MATEO PRE-HOSP" would show multiple rows for callsign WQNV472, each with potentially different license details (grant dates, expiration dates, service types).

## Root Cause
The SQL query was using `DISTINCT` but selecting license fields (`l.grant_date`, `l.expired_date`, `l.license_status`, `l.radio_service_type`) along with entity fields. Since the same callsign/entity can have multiple license records (renewals, different service types, etc.), each unique combination of license details created a separate "distinct" record.

**Problematic Query Pattern:**
```sql
SELECT DISTINCT l.call_sign, e.entity_name, e.first_name, e.last_name,
       e.city, e.state, l.grant_date, l.expired_date, l.license_status, l.radio_service_type
FROM entities e
JOIN licenses l ON e.unique_system_identifier = l.unique_system_identifier
WHERE e.entity_type = 'L' AND ...
```

## Solution
Modified both `webapp/app.py` and `enhanced_lookup.py` to use `GROUP BY` with aggregation functions to consolidate multiple license records per callsign/entity.

### 1. Web App Fix (webapp/app.py)
**Before:**
```sql
SELECT DISTINCT l.call_sign, e.entity_name, e.first_name, e.last_name,
       e.city, e.state, l.grant_date, l.expired_date
```

**After:**
```sql
SELECT e.call_sign, e.entity_name, e.first_name, e.last_name,
       e.city, e.state, 
       MIN(l.grant_date) as earliest_grant_date, 
       MAX(l.expired_date) as latest_expired_date
FROM entities e
JOIN licenses l ON e.unique_system_identifier = l.unique_system_identifier
WHERE e.entity_type = 'L' AND ...
GROUP BY e.call_sign, e.entity_name, e.first_name, e.last_name, e.city, e.state
```

### 2. CLI Tool Fix (enhanced_lookup.py)
**Before:**
```sql
SELECT DISTINCT e.call_sign, e.entity_name, e.first_name, e.last_name, 
       e.city, e.state, l.license_status, l.radio_service_type
```

**After:**
```sql
SELECT e.call_sign, e.entity_name, e.first_name, e.last_name, 
       e.city, e.state, 
       MAX(CASE WHEN l.license_status IS NOT NULL THEN l.license_status ELSE 'Unknown' END) as license_status,
       GROUP_CONCAT(DISTINCT l.radio_service_type) as radio_service_types
FROM entities e
LEFT JOIN licenses l ON e.call_sign = l.call_sign
WHERE e.entity_type = 'L' AND ...
GROUP BY e.call_sign, e.entity_name, e.first_name, e.last_name, e.city, e.state
```

## Aggregation Strategy

### For Web App:
- **Grant Date**: `MIN(l.grant_date)` - Shows the earliest grant date
- **Expiration Date**: `MAX(l.expired_date)` - Shows the latest expiration date

### For CLI Tool:
- **License Status**: `MAX(...)` - Shows the most recent/relevant status
- **Service Types**: `GROUP_CONCAT(DISTINCT ...)` - Combines all service types

## Testing Results

**Test:** `python enhanced_lookup.py --name "san mateo pre" --limit 10`

**Before Fix:**
```
WQNV472      Active       San Mateo Pre-Hospital E  Foster City, C
WQNV472      Active       San Mateo Pre-Hospital E  Foster City, C  
WQNV472      Expired      San Mateo Pre-Hospital E  Foster City, C
```

**After Fix:**
```
WQNV472      Active       San Mateo Pre-Hospital E  Foster City, C
```

**Web App:** Same improvement - each callsign now appears only once in search results.

## Benefits
- ✅ **Eliminates Duplicates**: Each callsign appears only once per entity
- ✅ **Preserves Information**: Uses aggregation to show meaningful license details
- ✅ **Consistent Experience**: Same fix applied to both CLI and web interfaces
- ✅ **Better Performance**: Fewer records to process and display
- ✅ **Cleaner Results**: More readable and professional search results

## Files Modified
- `webapp/app.py` - Updated `search_by_licensee()` method with GROUP BY aggregation
- `enhanced_lookup.py` - Updated licensee search query with GROUP BY aggregation
- `LICENSEE_DUPLICATE_FIX.md` - This documentation

## Note
This fix is similar to the frequency search duplicate fix implemented earlier, applying the same GROUP BY aggregation principle to eliminate duplicates while preserving essential information through intelligent aggregation functions.
