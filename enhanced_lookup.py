#!/usr/bin/env python3
"""
Enhanced FCC ULS Lookup Tool

A command-line tool to lookup FCC call signs, licensee names, and frequencies
in the FCC ULS Land Mobile database.
"""

import sys
import sqlite3
from typing import Dict, List, Any, Optional

class FccLookup:
    def __init__(self, db_path: str = 'fcc_uls.db'):
        """Initialize the lookup tool with database connection."""
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"❌ Error connecting to database: {e}")
            sys.exit(1)
    
    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def sanitize_input(self, value: str) -> str:
        """Clean and validate input."""
        return value.upper().strip()
    
    def status_to_text(self, status: str) -> str:
        """Convert status code to readable text."""
        status_map = {
            'A': 'Active',
            'E': 'Expired', 
            'T': 'Terminated',
            'C': 'Cancelled',
            'L': 'License',
            'P': 'Pending',
            'R': 'Received',
            'Q': 'Accepted for Filing',
            'X': 'Dismissed',
            'G': 'Granted'
        }
        return status_map.get(str(status).upper(), f"Unknown ({status})")
    
    def format_coordinates(self, lat_deg: int, lat_min: int, lat_sec: float, lat_dir: str,
                          long_deg: int, long_min: int, long_sec: float, long_dir: str) -> str:
        """Format coordinates in a readable format."""
        if not all([lat_deg, lat_min, long_deg, long_min]):
            return "Not available"
        
        lat_sec = lat_sec or 0.0
        long_sec = long_sec or 0.0
        lat_dir = lat_dir or "N"
        long_dir = long_dir or "W"
        
        return f"{lat_deg}° {lat_min}' {lat_sec:.1f}\" {lat_dir}, {long_deg}° {long_min}' {long_sec:.1f}\" {long_dir}"
    
    def format_decimal_coords(self, lat_deg: int, lat_min: int, lat_sec: float, lat_dir: str,
                             long_deg: int, long_min: int, long_sec: float, long_dir: str) -> str:
        """Convert coordinates to decimal degrees."""
        try:
            if not all([lat_deg, lat_min, long_deg, long_min]):
                return "Not available"
            
            lat_sec = lat_sec or 0.0
            long_sec = long_sec or 0.0
            lat_dir = lat_dir or "N"
            long_dir = long_dir or "W"
            
            lat_decimal = lat_deg + lat_min/60 + lat_sec/3600
            long_decimal = long_deg + long_min/60 + long_sec/3600
            
            if lat_dir == 'S':
                lat_decimal = -lat_decimal
            if long_dir == 'W':
                long_decimal = -long_decimal
                
            return f"{lat_decimal:.6f}, {long_decimal:.6f}"
        except (TypeError, ZeroDivisionError):
            return "Not available"
    
    def display_callsign_info(self, callsign: str, show_header: bool = True) -> bool:
        """Display comprehensive information for a call sign."""
        if show_header:
            print(f"\n{'='*60}")
            print(f"🔍 FCC ULS LOOKUP: {callsign}")
            print(f"{'='*60}")
        
        # Get license information - prioritize records with complete data
        license_query = """
            SELECT call_sign, license_status, radio_service_type, grant_date, 
                   expired_date, unique_system_identifier, uls_file_number
            FROM licenses 
            WHERE call_sign = ?
            ORDER BY 
                CASE 
                    WHEN license_status IS NOT NULL AND license_status != '' 
                         AND grant_date IS NOT NULL AND grant_date != '' THEN 1
                    WHEN license_status IS NOT NULL AND license_status != '' THEN 2
                    ELSE 3
                END,
                expired_date DESC
            LIMIT 1
        """
        
        cursor = self.conn.cursor()
        cursor.execute(license_query, (callsign,))
        license_info = cursor.fetchone()
        
        if not license_info:
            if show_header:
                print(f"❌ No license found for callsign: {callsign}")
                # Try to search for similar callsigns
                self.suggest_similar_callsigns(callsign)
            return False
        
        # LICENSE INFORMATION
        print(f"\n📋 LICENSE INFORMATION")
        print(f"{'─'*40}")
        print(f"Call Sign:        {license_info['call_sign']}")
        print(f"Status:           ✅ {self.status_to_text(license_info['license_status'])}")
        print(f"Service Type:     {license_info['radio_service_type'] or 'Not specified'}")
        print(f"Grant Date:       {license_info['grant_date'].strip() if license_info['grant_date'] and license_info['grant_date'].strip() else 'Not available'}")
        print(f"Expiration:       {license_info['expired_date'].strip() if license_info['expired_date'] and license_info['expired_date'].strip() else 'Not available'}")
        
        # Get licensee information from entities (entity_type = 'L' for licensee)
        licensee_query = """
            SELECT entity_name, first_name, last_name, street_address, city, state, 
                   zip_code, phone, email, entity_type
            FROM entities 
            WHERE (call_sign = ? OR uls_file_number = ?) AND entity_type = 'L'
            LIMIT 1
        """
        
        cursor.execute(licensee_query, (callsign, license_info['uls_file_number']))
        licensee_info = cursor.fetchone()
        
        # Get contact information from entities (entity_type = 'CL' for contact/certifier)
        contact_query = """
            SELECT entity_name, first_name, last_name, street_address, city, state, 
                   zip_code, phone, email, entity_type
            FROM entities 
            WHERE (call_sign = ? OR uls_file_number = ?) AND entity_type = 'CL'
            LIMIT 1
        """
        
        cursor.execute(contact_query, (callsign, license_info['uls_file_number']))
        contact_info = cursor.fetchone()
        
        if licensee_info:
            print(f"\n👤 LICENSEE INFORMATION")
            print(f"{'─'*40}")
            
            # Format licensee name
            if licensee_info['entity_name']:
                print(f"Licensee:         {licensee_info['entity_name']}")
            elif licensee_info['first_name'] or licensee_info['last_name']:
                name_parts = [licensee_info['first_name'], licensee_info['last_name']]
                full_name = ' '.join(filter(None, name_parts))
                print(f"Licensee:         {full_name}")
            
            # Format address
            if licensee_info['street_address']:
                print(f"Address:          {licensee_info['street_address']}")
                location_parts = [licensee_info['city'], licensee_info['state'], licensee_info['zip_code']]
                location = ', '.join(filter(None, location_parts))
                if location:
                    print(f"                  {location}")
            
            if licensee_info['phone']:
                print(f"Phone:            {licensee_info['phone']}")
            if licensee_info['email']:
                print(f"Email:            {licensee_info['email']}")
        
        if contact_info:
            print(f"\n📞 CONTACT INFORMATION")
            print(f"{'─'*40}")
            
            # Format contact name
            if contact_info['entity_name']:
                print(f"Contact Entity:   {contact_info['entity_name']}")
            elif contact_info['first_name'] or contact_info['last_name']:
                name_parts = [contact_info['first_name'], contact_info['last_name']]
                full_name = ' '.join(filter(None, name_parts))
                print(f"Contact Person:   {full_name}")
            
            # Format address (only if different from licensee)
            if contact_info['street_address'] and (not licensee_info or contact_info['street_address'] != licensee_info['street_address']):
                print(f"Contact Address:  {contact_info['street_address']}")
                location_parts = [contact_info['city'], contact_info['state'], contact_info['zip_code']]
                location = ', '.join(filter(None, location_parts))
                if location:
                    print(f"                  {location}")
            
            if contact_info['phone'] and (not licensee_info or contact_info['phone'] != licensee_info['phone']):
                print(f"Contact Phone:    {contact_info['phone']}")
            if contact_info['email'] and (not licensee_info or contact_info['email'] != licensee_info['email']):
                print(f"Contact Email:    {contact_info['email']}")
        
        # FREQUENCY ASSIGNMENTS
        freq_query = """
            SELECT frequency_assigned, frequency_upper_band, emission_designator,
                   power_output, power_erp, status_code
            FROM frequencies 
            WHERE call_sign = ?
            ORDER BY frequency_assigned
        """
        
        cursor.execute(freq_query, (callsign,))
        frequencies = cursor.fetchall()
        
        if frequencies:
            print(f"\n📡 FREQUENCY ASSIGNMENTS")
            print(f"{'─'*40}")
            print(f"{'Frequency (MHz)':<15} {'Power (W)':<12} {'Emission':<12} {'Status'}")
            print(f"{'-'*15} {'-'*12} {'-'*12} {'-'*8}")
            
            for freq in frequencies:
                freq_mhz = freq['frequency_assigned']
                power = freq['power_erp'] or freq['power_output'] or 0
                emission = freq['emission_designator'] or 'Unknown'
                status = freq['status_code'] or 'A'
                
                if freq_mhz is None:
                    freq_str = "Not specified"
                else:
                    freq_str = f"{freq_mhz:.4f}"
                
                status_icon = '✅' if status == 'A' else '❌'
                print(f"{freq_str:<15} {power:<12.1f} {emission:<12} {status_icon}")
        
        # LOCATION INFORMATION
        location_query = """
            SELECT location_number, location_city, location_state, location_county,
                   location_address, lat_degrees, lat_minutes, lat_seconds, lat_direction,
                   long_degrees, long_minutes, long_seconds, long_direction,
                   ground_elevation, height_of_support_structure, overall_height_of_structure
            FROM locations 
            WHERE call_sign = ?
            ORDER BY location_number
        """
        
        cursor.execute(location_query, (callsign,))
        locations = cursor.fetchall()
        
        if locations:
            print(f"\n📍 LOCATIONS")
            print(f"{'─'*40}")
            
            for i, loc in enumerate(locations, 1):
                # Check if location has any meaningful data
                has_data = any([
                    loc['location_address'],
                    loc['location_city'],
                    loc['location_state'],
                    loc['lat_degrees'],
                    loc['long_degrees'],
                    loc['ground_elevation'],
                    loc['height_of_support_structure'],
                    loc['overall_height_of_structure']
                ])
                
                if not has_data:
                    continue
                
                meaningful_locations = [l for l in locations if any([
                    l['location_address'], l['location_city'], l['location_state'],
                    l['lat_degrees'], l['long_degrees'], l['ground_elevation'],
                    l['height_of_support_structure'], l['overall_height_of_structure']
                ])]
                
                if len(meaningful_locations) > 1:
                    print(f"\n🏢 Location {i}:")
                
                if loc['location_address']:
                    print(f"Address:          {loc['location_address']}")
                
                location_parts = [loc['location_city'], loc['location_state']]
                if loc['location_county']:
                    location_parts.insert(-1, f"{loc['location_county']} County")
                location_str = ', '.join(filter(None, location_parts))
                if location_str:
                    print(f"Location:         {location_str}")
                
                # Coordinates
                coords = self.format_coordinates(
                    loc['lat_degrees'], loc['lat_minutes'], loc['lat_seconds'], loc['lat_direction'],
                    loc['long_degrees'], loc['long_minutes'], loc['long_seconds'], loc['long_direction']
                )
                if coords != "Not available":
                    print(f"Coordinates:      {coords}")
                    decimal_coords = self.format_decimal_coords(
                        loc['lat_degrees'], loc['lat_minutes'], loc['lat_seconds'], loc['lat_direction'],
                        loc['long_degrees'], loc['long_minutes'], loc['long_seconds'], loc['long_direction']
                    )
                    print(f"Decimal Coords:   {decimal_coords}")
                
                if loc['ground_elevation']:
                    print(f"Ground Elevation: {loc['ground_elevation']} meters")
                if loc['height_of_support_structure']:
                    print(f"Support Height:   {loc['height_of_support_structure']} meters")
                if loc['overall_height_of_structure']:
                    print(f"Overall Height:   {loc['overall_height_of_structure']} meters")
        
        return True
    
    def suggest_similar_callsigns(self, callsign: str):
        """Suggest similar callsigns."""
        cursor = self.conn.cursor()
        
        # Try partial matches
        cursor.execute("""
            SELECT DISTINCT call_sign FROM licenses 
            WHERE call_sign LIKE ? 
            LIMIT 5
        """, (f"%{callsign[:4]}%",))
        similar = cursor.fetchall()
        
        if similar:
            print(f"\n💡 Similar callsigns found:")
            for row in similar:
                if row['call_sign']:
                    print(f"   • {row['call_sign']}")
    
    def search_by_licensee(self, name: str, limit: int = 150, state_filter: str = None):
        """Search for licenses by actual licensee name using case-insensitive string match with wildcard at end."""
        name = name.upper()
        state_display = f" in {state_filter.upper()}" if state_filter else ""
        print(f"\n{'='*60}")
        print(f"🔍 LICENSEE SEARCH: {name}{state_display}")
        print(f"{'='*60}")

        cursor = self.conn.cursor()

        # Build query to search actual licensees (entity_type = 'L') with wildcard at end
        base_query = """
            SELECT e.call_sign, e.entity_name, e.first_name, e.last_name, 
                   e.city, e.state, 
                   MAX(CASE WHEN l.license_status IS NOT NULL THEN l.license_status ELSE 'Unknown' END) as license_status,
                   GROUP_CONCAT(DISTINCT l.radio_service_type) as radio_service_types
            FROM entities e
            LEFT JOIN licenses l ON e.call_sign = l.call_sign
            WHERE e.entity_type = 'L' 
            AND (UPPER(e.entity_name) LIKE ? OR 
                 UPPER(e.first_name || ' ' || e.last_name) LIKE ?)
            AND e.call_sign IS NOT NULL AND e.call_sign != ''
        """

        # Add wildcard at the end of search term
        search_term = f"{name}%"
        params = [search_term, search_term]

        if state_filter:
            base_query += " AND e.state = ?"
            params.append(state_filter.upper())

        # Group by callsign to eliminate duplicates
        query = base_query + """
            GROUP BY e.call_sign, e.entity_name, e.first_name, e.last_name, e.city, e.state
            ORDER BY e.entity_name, e.call_sign 
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if not results:
            print(f"❌ No licensees found matching: {name}{state_display}")
            return
        
        print(f"\n📋 FOUND {len(results)} MATCHING LICENSEES")
        print(f"{'─'*60}")
        print(f"{'Call Sign':<12} {'Status':<12} {'Licensee Name':<25} {'Location'}")
        print(f"{'-'*12} {'-'*12} {'-'*25} {'-'*15}")
        
        for result in results:
            callsign = result['call_sign'] or 'N/A'
            status = self.status_to_text(result['license_status']) if result['license_status'] else 'Unknown'
            
            # Format licensee name
            if result['entity_name']:
                name_str = result['entity_name'][:24]
            elif result['first_name'] or result['last_name']:
                name_parts = [result['first_name'], result['last_name']]
                name_str = ' '.join(filter(None, name_parts))[:24]
            else:
                name_str = 'Unknown'
            
            # Format location
            location_parts = [result['city'], result['state']]
            location_str = ', '.join(filter(None, location_parts))[:14]
            
            print(f"{callsign:<12} {status:<12} {name_str:<25} {location_str}")
        
        # Offer detailed lookup
        if len(results) <= 5:
            print(f"\n💡 For detailed information on any callsign, use:")
            for result in results:
                if result['call_sign']:
                    print(f"   uv run python enhanced_lookup.py {result['call_sign']}")
    
    def search_by_frequency(self, frequency: float, tolerance: float = 0.001, limit: int = 150, state_filter: str = None):
        """Search for licenses by frequency."""
        state_display = f" in {state_filter.upper()}" if state_filter else ""
        print(f"\n{'='*60}")
        print(f"🔍 FREQUENCY SEARCH: {frequency:.4f} MHz (±{tolerance:.3f} MHz){state_display}")
        print(f"{'='*60}")

        cursor = self.conn.cursor()

        # Build query with grouping to eliminate duplicates per callsign/frequency
        base_query = """
            SELECT f.call_sign, f.frequency_assigned,
                   GROUP_CONCAT(DISTINCT CASE WHEN f.power_erp IS NOT NULL THEN f.power_erp || 'W (ERP)' END) as erp_powers,
                   GROUP_CONCAT(DISTINCT CASE WHEN f.power_output IS NOT NULL THEN f.power_output || 'W (Out)' END) as output_powers,
                   GROUP_CONCAT(DISTINCT f.emission_designator) as emissions,
                   l.license_status, e.entity_name, e.city, e.state
            FROM frequencies f
            LEFT JOIN licenses l ON f.call_sign = l.call_sign
            LEFT JOIN entities e ON f.call_sign = e.call_sign AND e.entity_type = 'L'
            WHERE f.frequency_assigned BETWEEN ? AND ?
            AND f.call_sign IS NOT NULL AND f.call_sign != ''
        """

        params = [frequency - tolerance, frequency + tolerance]

        if state_filter:
            base_query += " AND e.state = ?"
            params.append(state_filter.upper())

        # Group by callsign and frequency to eliminate duplicates
        query = base_query + """
            GROUP BY f.call_sign, f.frequency_assigned
            ORDER BY f.frequency_assigned, f.call_sign 
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if not results:
            print(f"❌ No frequencies found near {frequency:.4f} MHz{state_display}")
            return
        
        print(f"\n📡 FOUND {len(results)} MATCHING FREQUENCIES")
        print(f"{'─'*60}")
        print(f"{'Call Sign':<12} {'Frequency':<12} {'Powers':<15} {'Emissions':<15} {'Licensee'}")
        print(f"{'-'*12} {'-'*12} {'-'*15} {'-'*15} {'-'*20}")

        for result in results:
            callsign = result['call_sign'] or 'N/A'
            freq = f"{result['frequency_assigned']:.4f}" if result['frequency_assigned'] else 'N/A'
            
            # Handle aggregated power values
            erp_powers = result['erp_powers'] or ''
            output_powers = result['output_powers'] or ''
            powers_combined = []
            
            # Process ERP powers
            if erp_powers:
                erp_list = [p.strip() for p in erp_powers.split(',') if p.strip() and 'W (ERP)' in p.strip()]
                powers_combined.extend(erp_list)
            
            # Process Output powers  
            if output_powers:
                out_list = [p.strip() for p in output_powers.split(',') if p.strip() and 'W (Out)' in p.strip()]
                powers_combined.extend(out_list)
                
            power_str = ', '.join(set(powers_combined))[:14] if powers_combined else 'N/A'
            
            # Handle aggregated emissions
            emissions = result['emissions'] or 'N/A'
            emission_str = emissions[:14] if emissions else 'N/A'
            
            # Format licensee name
            licensee = (result['entity_name'] or 'Unknown')[:19]
            
            print(f"{callsign:<12} {freq:<12} {power_str:<15} {emission_str:<15} {licensee}")        # Offer detailed lookup
        if len(results) <= 5:
            print(f"\n💡 For detailed information on any callsign, use:")
            for result in results:
                if result['call_sign']:
                    print(f"   uv run python enhanced_lookup.py {result['call_sign']}")

def show_help():
    """Show usage help."""
    print("""
🔍 Enhanced FCC ULS Lookup Tool

USAGE:
  python enhanced_lookup.py <QUERY> [OPTIONS]

QUERY TYPES:
  Call Sign:        python enhanced_lookup.py KA21141
  Entity/Contact:   python enhanced_lookup.py --name "ARLEY, TOWN OF"
  Frequency (MHz):  python enhanced_lookup.py --freq 465.0
  Frequency Range:  python enhanced_lookup.py --freq 465.0 --tolerance 0.5

OPTIONS:
  --name <name>         Search by licensee name
  --freq <frequency>    Search by frequency in MHz
  --tolerance <mhz>     Frequency search tolerance (default: 0.001 MHz)
  --state <state>       Filter results by state (2-letter code, e.g., CA, TX)
  --limit <number>      Maximum results to show (default: 150)
  --help, -h           Show this help

EXAMPLES:
  # Look up specific callsign
  python enhanced_lookup.py WQO214
  
  # Search for entities/contacts containing "MARRIOTT"
  python enhanced_lookup.py --name "MARRIOTT"
  
  # Search for entities/contacts in California only
  python enhanced_lookup.py --name "MARRIOTT" --state CA
  
  # Find all licenses on 465 MHz (±0.001 MHz)
  python enhanced_lookup.py --freq 465.0
  
  # Find licenses near 150 MHz in Texas only
  python enhanced_lookup.py --freq 150.0 --tolerance 1.0 --state TX
""")

def main():
    """Main entry point for the enhanced lookup tool."""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        return
    
    lookup = FccLookup()
    
    # Parse arguments
    args = sys.argv[1:]
    name_search = None
    freq_search = None
    tolerance = 0.001
    limit = 150
    state_filter = None
    
    i = 0
    while i < len(args):
        if args[i] == '--name' and i + 1 < len(args):
            name_search = args[i + 1]
            i += 2
        elif args[i] == '--freq' and i + 1 < len(args):
            try:
                freq_search = float(args[i + 1])
            except ValueError:
                print(f"❌ Invalid frequency: {args[i + 1]}")
                return
            i += 2
        elif args[i] == '--tolerance' and i + 1 < len(args):
            try:
                tolerance = float(args[i + 1])
            except ValueError:
                print(f"❌ Invalid tolerance: {args[i + 1]}")
                return
            i += 2
        elif args[i] == '--limit' and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                print(f"❌ Invalid limit: {args[i + 1]}")
                return
            i += 2
        elif args[i] == '--state' and i + 1 < len(args):
            state_filter = args[i + 1].upper()
            if len(state_filter) != 2:
                print(f"❌ Invalid state code: {args[i + 1]} (use 2-letter code like CA, TX)")
                return
            i += 2
        else:
            # Assume it's a callsign
            callsign = lookup.sanitize_input(args[i])
            lookup.display_callsign_info(callsign)
            return
    
    # Perform searches
    if name_search:
        lookup.search_by_licensee(name_search, limit, state_filter)
    elif freq_search:
        lookup.search_by_frequency(freq_search, tolerance, limit, state_filter)
    else:
        show_help()

if __name__ == '__main__':
    main()
