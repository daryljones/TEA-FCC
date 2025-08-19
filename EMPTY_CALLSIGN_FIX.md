# Empty Callsign Rows Fix

## Problem
After implementing the GROUP BY fix for duplicate callsigns, some search results were showing rows with no callsign when searching for terms like "SAN MATEO PRE-HOSPITAL". These were entities that existed in the database but didn't have valid callsigns associated with them.

## Root Cause
The GROUP BY query was including entities that had NULL or empty callsigns. This happened because:

1. Some entities in the `entities` table don't have corresponding records in the `licenses` table
2. Some entities have callsign fields that are NULL or empty strings
3. The GROUP BY was aggregating these invalid records along with valid ones

**SQL Query Investigation:**
```sql
SELECT e.call_sign, e.entity_name, COUNT(*) as license_count 
FROM entities e 
LEFT JOIN licenses l ON e.unique_system_identifier = l.unique_system_identifier 
WHERE e.entity_type = 'L' AND UPPER(e.entity_name) LIKE 'SAN MATEO PRE-HOSPITAL%' 
GROUP BY e.call_sign, e.entity_name 
ORDER BY e.entity_name LIMIT 10;
```

**Results showed:**
```
|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES|17                    <- Empty callsign
WQND954|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES|1              <- Valid callsign
|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES PROVIDERS|53          <- Empty callsign
WQGS319|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES PROVIDERS|1    <- Valid callsign
```

## Solution
Added explicit filtering to exclude entities with NULL or empty callsigns in the webapp query.

### Web App Fix (webapp/app.py)
**Before:**
```sql
SELECT e.call_sign, e.entity_name, e.first_name, e.last_name,
       e.city, e.state, 
       MIN(l.grant_date) as earliest_grant_date, 
       MAX(l.expired_date) as latest_expired_date
FROM entities e
JOIN licenses l ON e.unique_system_identifier = l.unique_system_identifier
WHERE e.entity_type = 'L'
AND (
    UPPER(e.entity_name) LIKE ? OR 
    UPPER(e.first_name || ' ' || e.last_name) LIKE ?
)
```

**After:**
```sql
SELECT e.call_sign, e.entity_name, e.first_name, e.last_name,
       e.city, e.state, 
       MIN(l.grant_date) as earliest_grant_date, 
       MAX(l.expired_date) as latest_expired_date
FROM entities e
JOIN licenses l ON e.unique_system_identifier = l.unique_system_identifier
WHERE e.entity_type = 'L'
AND e.call_sign IS NOT NULL AND e.call_sign != ''    <- Added this filter
AND (
    UPPER(e.entity_name) LIKE ? OR 
    UPPER(e.first_name || ' ' || e.last_name) LIKE ?
)
```

### CLI Tool Status
The enhanced_lookup.py already had the proper filter:
```sql
AND e.call_sign IS NOT NULL AND e.call_sign != ''
```
So no changes were needed for the CLI tool.

## Testing Results

**Test Query (After Fix):**
```sql
SELECT e.call_sign, e.entity_name, e.city, e.state
FROM entities e 
JOIN licenses l ON e.unique_system_identifier = l.unique_system_identifier 
WHERE e.entity_type = 'L' 
AND e.call_sign IS NOT NULL AND e.call_sign != '' 
AND UPPER(e.entity_name) LIKE 'SAN MATEO PRE-HOSPITAL%' 
GROUP BY e.call_sign, e.entity_name, e.first_name, e.last_name, e.city, e.state 
ORDER BY e.entity_name LIMIT 10;
```

**Results (After Fix):**
```
WQND954|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES|FOSTER CITY|CA
WQGS319|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES PROVIDERS|FOSTER CITY|CA  
WQGU325|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES PROVIDERS|FOSTER CITY|CA
WQHJ488|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES PROVIDERS|FOSTER CITY|CA
WSCS493|SAN MATEO PRE-HOSPITAL EMERGENCY SERVICES PROVIDERS|SAN MATEO|CA
WII973|San Mateo Pre-Hospital Emergency Services|Foster City|CA
WQPC662|San Mateo Pre-Hospital Emergency Services|Foster City|CA
WQPC663|San Mateo Pre-Hospital Emergency Services|Foster City|CA
WQNV472|San Mateo Pre-Hospital Emergency Services Providers|Foster City|CA
```

All rows now have valid callsigns - no more empty callsign entries.

## Why This Issue Occurred
1. **Database Design**: The FCC database contains entities that may not have active licenses
2. **Data Quality**: Some entity records have NULL or empty callsign fields
3. **Query Evolution**: When we switched from simple `DISTINCT` to `GROUP BY`, we inadvertently included these invalid records

## Benefits of Fix
- ✅ **Clean Results**: No more confusing empty callsign rows
- ✅ **Data Integrity**: Only shows entities with valid, searchable callsigns
- ✅ **User Experience**: Search results are meaningful and actionable
- ✅ **Consistency**: Both CLI and web app now have same filtering logic

## Files Modified
- `webapp/app.py` - Added callsign validation filter to licensee search query
- `EMPTY_CALLSIGN_FIX.md` - This documentation

## Related Fixes
This fix builds upon:
1. **Frequency Search Duplicates** - GROUP BY aggregation approach
2. **Licensee Search Duplicates** - GROUP BY for entity consolidation  
3. **Empty Callsign Filter** - Data quality improvement

The licensee search functionality is now robust and returns clean, actionable results.
