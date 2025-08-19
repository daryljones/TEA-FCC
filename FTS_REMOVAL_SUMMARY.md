# FTS Removal Summary

## Changes Made

### 1. Removed Full-Text Search (FTS5) Implementation

**Files Modified:**
- `webapp/app.py` - Replaced FTS5 search with simple case-insensitive LIKE search
- `enhanced_lookup.py` - Updated to use wildcard-at-end approach
- `remove_fts.py` - Created script to drop FTS table from database

**Files Renamed:**
- `setup_fts.py` → `setup_fts_DEPRECATED.py` - Marked as deprecated

**Database Changes:**
- Dropped `entities_fts` virtual table from SQLite database

### 2. New Search Behavior

**Licensee Name Search:**
- **Old:** Used FTS5 full-text search with complex ranking
- **New:** Simple case-insensitive string match with wildcard at the end
- **Pattern:** `UPPER(field) LIKE 'SEARCH_TERM%'`
- **Example:** Searching "san" will find "San Bruno", "Santa Clara", "Sanders", etc.

**Benefits:**
- Simplified codebase - no FTS dependencies
- Reduced database size (no FTS virtual table)
- Predictable search behavior (prefix matching)
- Case-insensitive matching
- No complex FTS setup or maintenance required

### 3. Search Query Changes

**Before (FTS5):**
```sql
SELECT ... FROM entities_fts f
JOIN entities e ON f.unique_system_identifier = e.unique_system_identifier
WHERE entities_fts MATCH ?
ORDER BY bm25(entities_fts), ...
```

**After (Simple LIKE):**
```sql
SELECT ... FROM entities e
JOIN licenses l ON e.unique_system_identifier = l.unique_system_identifier
WHERE (
    UPPER(e.entity_name) LIKE ? OR 
    UPPER(e.first_name || ' ' || e.last_name) LIKE ?
)
ORDER BY e.entity_name, e.last_name
```

### 4. Documentation Updates

- `FILE_OVERVIEW.md` - Updated to reflect deprecated FTS file
- `CLEANUP_SUMMARY.md` - Updated file listing
- `ENHANCED_LOOKUP_GUIDE.md` - Updated search behavior description

### 5. Testing Results

**Search Test:** `python enhanced_lookup.py --name "san" --limit 5`
**Result:** Successfully found 5 licensees with names starting with "san"
- ANDERSON, SANDRA K
- ARBELO, SANTIAGO  
- BRACY, SANDRA
- etc.

**Verification:** Wildcard matching is working correctly and case-insensitive.

## Impact

- **Performance:** May be slightly slower for very large result sets, but simpler and more predictable
- **Maintenance:** Reduced complexity, no FTS table to maintain
- **Database Size:** Smaller database without FTS virtual table
- **Search Behavior:** More predictable prefix-based matching instead of full-text relevance scoring
