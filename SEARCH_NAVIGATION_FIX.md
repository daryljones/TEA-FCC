# Search Results Navigation Improvement

## Problem
When users clicked on callsign links from licensee or frequency search results, they would go to the detailed callsign view but lose their search results with no way to navigate back to the specific search they came from.

## Solution Implemented

### 1. **Context-Aware Links**
Modified the search result links to include search context as URL parameters:

**Before:**
```javascript
<a href="/callsign/${callsign}">View Details</a>
```

**After (Licensee Search):**
```javascript
const returnParams = new URLSearchParams({
    search_type: 'licensee',
    name: data.search_params.name || '',
    state: data.search_params.state || '',
    limit: data.search_params.limit || 150
});
const returnUrl = `/?${returnParams.toString()}#licensee-results`;
const detailUrl = `/callsign/${callsign}?return=${encodeURIComponent(returnUrl)}`;
```

**After (Frequency Search):**
```javascript
const returnParams = new URLSearchParams({
    search_type: 'frequency',
    frequency: data.search_params.frequency || '',
    tolerance: data.search_params.tolerance || 0.001,
    state: data.search_params.state || '',
    limit: data.search_params.limit || 150
});
```

### 2. **Search State Restoration**
Added JavaScript function to automatically restore search state when users return:

```javascript
function restoreSearchState() {
    const urlParams = new URLSearchParams(window.location.search);
    const searchType = urlParams.get('search_type');
    
    if (searchType === 'licensee') {
        // Switch to licensee tab, restore form values, auto-execute search
    } else if (searchType === 'frequency') {
        // Switch to frequency tab, restore form values, auto-execute search
    }
}
```

### 3. **Flask Route Enhancement**
Updated the callsign detail route to accept and pass return URL:

```python
@app.route('/callsign/<callsign>')
def callsign_detail(callsign: str):
    return_url = request.args.get('return', '/')
    return render_template('callsign_detail.html', 
                         callsign=callsign, 
                         data=result, 
                         return_url=return_url)
```

### 4. **Dynamic Back Button**
Updated the callsign detail template to use context-aware navigation:

**Before:**
```html
<a href="/" class="btn btn-outline-secondary">
    <i class="fas fa-arrow-left"></i> Back to Search
</a>
```

**After:**
```html
<a href="{{ return_url }}" class="btn btn-outline-secondary">
    <i class="fas fa-arrow-left"></i> Back to Search Results
</a>
```

## User Experience Flow

### Licensee Search Example:
1. User searches for "San Bruno" licensees
2. Results display with enhanced callsign links
3. User clicks "View Details" for WIM449
4. URL becomes: `/callsign/WIM449?return=%2F%3Fsearch_type%3Dlicensee%26name%3DSan%2520Bruno%26state%3D%26limit%3D150%23licensee-results`
5. Detail page shows "Back to Search Results" button
6. User clicks back button
7. Returns to home page with licensee tab active
8. Search form is pre-filled with "San Bruno"
9. Search automatically re-executes
10. Results scroll to `#licensee-results` section

### Frequency Search Example:
1. User searches for 488.4625 MHz
2. Results display with enhanced callsign links  
3. User clicks callsign link
4. URL includes frequency search context
5. Back button returns and restores frequency search with same parameters

## Benefits
- ✅ **Seamless Navigation**: Users can easily return to their search results
- ✅ **Context Preservation**: All search parameters are maintained
- ✅ **Automatic Restoration**: Search re-executes automatically when returning
- ✅ **Tab Management**: Correct tab is activated when returning
- ✅ **Scroll Position**: Returns to the results section with anchor links
- ✅ **Fallback Behavior**: Still works if no return context (defaults to home page)

## Files Modified
- `webapp/templates/index.html` - Enhanced result links and added restoration logic
- `webapp/app.py` - Modified callsign route to handle return URL parameter
- `webapp/templates/callsign_detail.html` - Updated back button to use dynamic URL

The navigation flow now provides a much more user-friendly experience, allowing users to seamlessly browse between search results and detailed views without losing their context.
