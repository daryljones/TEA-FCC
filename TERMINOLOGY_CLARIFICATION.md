# Terminology Clarification - Entity/Contact vs Licensee

## 🔍 Important Clarification About FCC Data

Based on analysis of the FCC ULS database structure, I've updated the enhanced lookup tool to use more accurate terminology regarding the "names" in the database.

## ✅ What Changed

### Previous (Incorrect) Terminology:
- "Licensee Name" 
- "Licensee Search"
- "Licensee Information"

### Updated (Accurate) Terminology:
- "Entity/Contact Name"
- "Entity/Contact Search" 
- "Contact/Entity Information"

## 🎯 Why This Matters

### What the Data Actually Contains
The `entity_name` field in the FCC database contains:
- **Company/Organization names** (e.g., "MARRIOTT", "CITY OF ATLANTA")
- **Contact person names** for the license
- **Business names** or **DBA names**
- **Administrative contacts**

### What It Does NOT Contain
- The actual legal licensee (which may be a parent company)
- The license holder's legal name in all cases
- Consistent licensee identification

## 📊 Examples of Corrected Display

### Name Search Results
```
🔍 ENTITY/CONTACT SEARCH: MARRIOTT
📋 FOUND 150 MATCHING ENTITIES/CONTACTS
Call Sign    Status       Entity/Contact Name       Location
------------ ------------ ------------------------- ---------------
WRDW311      Active       A C Hotel by Marriott     Santa Clara, CA
```

### Callsign Details
```
👤 CONTACT/ENTITY INFORMATION
────────────────────────────────────────
Entity/Company:   ARLEY, TOWN OF
Contact Name:     John Smith
Address:          821 Farley Road
Entity Type:      CL
```

### Frequency Search Results
```
📡 FOUND 25 MATCHING FREQUENCIES
Call Sign    Frequency    Power      Emission   Entity/Contact
------------ ------------ ---------- ---------- --------------------
KA47084      464.9000     30W        MO         VERETT FARMS INC
```

## 🔧 Technical Changes Made

### Code Updates
1. **Function names**: `search_by_licensee()` → more accurate internal handling
2. **Display headers**: "LICENSEE SEARCH" → "ENTITY/CONTACT SEARCH"
3. **Column headers**: "Licensee Name" → "Entity/Contact Name"
4. **Section headers**: "LICENSEE INFORMATION" → "CONTACT/ENTITY INFORMATION"
5. **Field labels**: More specific "Entity/Company" vs "Contact Name"

### Documentation Updates
1. **Help text**: Updated to reflect entity/contact terminology
2. **Examples**: Clarified what type of data is being searched
3. **Tips section**: Added explanation of entity vs contact distinction
4. **User guide**: Updated throughout for accurate terminology

## 💡 Impact on Usage

### No Functional Changes
- All search functionality works exactly the same
- Same command-line options and parameters
- Same search results and data accuracy

### Improved Clarity
- Users understand they're searching contact/entity names
- More accurate expectation of what data represents
- Better alignment with FCC data structure

### Better Data Interpretation
- Users know the "name" may be a contact person, not the licensee
- Helps explain why some results might seem inconsistent
- Clarifies the relationship between entities and licenses

## 🌟 Key Benefits

1. **Accuracy**: Terminology matches the actual FCC data structure
2. **Clarity**: Users understand what they're searching and viewing
3. **Expectations**: Proper context for interpreting search results
4. **Compliance**: More accurate representation of FCC data
5. **Usability**: Better user experience with correct terminology

## ✨ Updated Features

The enhanced lookup tool now correctly identifies that it searches:
- **Entity names** (companies, organizations)
- **Contact names** (administrative contacts, responsible persons)
- **Business names** (doing-business-as names)

Rather than the legal "licensee" which may be a different entity entirely.

This provides users with a more accurate understanding of the FCC data and helps set proper expectations for search results and data interpretation.
