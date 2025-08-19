#!/usr/bin/env python3
"""
FCC ULS Callsign Lookup Tool

A command-line tool to lookup comprehensive information for FCC call signs
including license details, licensee info, frequencies, and locations.
"""

import sys
import sqlite3
from typing import Dict, List, Any, Optional

class CallsignLookup:
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
    
    def sanitize_callsign(self, callsign: str) -> str:
        """Clean and validate callsign format."""
        return callsign.upper().strip()
    
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
        lat_dir = lat_dir or "N"  # Default direction if None
        long_dir = long_dir or "W"  # Default direction if None
        
        return f"{lat_deg}° {lat_min}' {lat_sec:.1f}\" {lat_dir}, {long_deg}° {long_min}' {long_sec:.1f}\" {long_dir}"
    
    def format_decimal_coords(self, lat_deg: int, lat_min: int, lat_sec: float, lat_dir: str,
                             long_deg: int, long_min: int, long_sec: float, long_dir: str) -> str:
        """Convert coordinates to decimal degrees."""
        try:
            if not all([lat_deg, lat_min, long_deg, long_min]):
                return "Not available"
            
            lat_sec = lat_sec or 0.0
            long_sec = long_sec or 0.0
            lat_dir = lat_dir or "N"  # Default direction if None
            long_dir = long_dir or "W"  # Default direction if None
            
            lat_decimal = lat_deg + lat_min/60 + lat_sec/3600
            long_decimal = long_deg + long_min/60 + long_sec/3600
            
            if lat_dir == 'S':
                lat_decimal = -lat_decimal
            if long_dir == 'W':
                long_decimal = -long_decimal
                
            return f"{lat_decimal:.6f}, {long_decimal:.6f}"
        except (TypeError, ZeroDivisionError):
            return "Not available"
    
    def lookup_callsign(self, callsign: str) -> None:
        """Lookup comprehensive information for a call sign."""
        callsign = self.sanitize_callsign(callsign)
        
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
            print(f"❌ No license found for callsign: {callsign}")
            # Try to search in entities table for partial matches
            entity_query = """
                SELECT DISTINCT call_sign FROM entities 
                WHERE call_sign LIKE ? 
                LIMIT 5
            """
            cursor.execute(entity_query, (f"%{callsign}%",))
            similar = cursor.fetchall()
            
            if similar:
                print(f"\n💡 Similar callsigns found:")
                for row in similar:
                    if row['call_sign']:
                        print(f"   • {row['call_sign']}")
            return
        
        # LICENSE INFORMATION
        print(f"\n📋 LICENSE INFORMATION")
        print(f"{'─'*40}")
        print(f"Call Sign:        {license_info['call_sign']}")
        print(f"Status:           ✅ {self.status_to_text(license_info['license_status'])}")
        print(f"Service Type:     {license_info['radio_service_type'] or 'Not specified'}")
        print(f"Grant Date:       {license_info['grant_date'].strip() if license_info['grant_date'] and license_info['grant_date'].strip() else 'Not available'}")
        print(f"Expiration:       {license_info['expired_date'].strip() if license_info['expired_date'] and license_info['expired_date'].strip() else 'Not available'}")
        
        # Get licensee information from entities
        entity_query = """
            SELECT entity_name, first_name, last_name, street_address, city, state, 
                   zip_code, phone, email, entity_type
            FROM entities 
            WHERE call_sign = ? OR uls_file_number = ?
            LIMIT 1
        """
        
        cursor.execute(entity_query, (callsign, license_info['uls_file_number']))
        entity_info = cursor.fetchone()
        
        if entity_info:
            print(f"\n👤 LICENSEE INFORMATION")
            print(f"{'─'*40}")
            
            # Format licensee name
            if entity_info['entity_name']:
                print(f"Name:             {entity_info['entity_name']}")
            elif entity_info['first_name'] or entity_info['last_name']:
                name_parts = [entity_info['first_name'], entity_info['last_name']]
                full_name = ' '.join(filter(None, name_parts))
                print(f"Name:             {full_name}")
            
            # Format address
            if entity_info['street_address']:
                print(f"Address:          {entity_info['street_address']}")
                location_parts = [entity_info['city'], entity_info['state'], entity_info['zip_code']]
                location = ', '.join(filter(None, location_parts))
                if location:
                    print(f"                  {location}")
            
            if entity_info['phone']:
                print(f"Phone:            {entity_info['phone']}")
            if entity_info['email']:
                print(f"Email:            {entity_info['email']}")
        
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
                
                # Handle None frequency values
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
                    continue  # Skip empty locations
                
                if len([l for l in locations if any([
                    l['location_address'], l['location_city'], l['location_state'],
                    l['lat_degrees'], l['long_degrees'], l['ground_elevation'],
                    l['height_of_support_structure'], l['overall_height_of_structure']
                ])]) > 1:
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

def main():
    """Main entry point for the command line tool."""
    if len(sys.argv) != 2:
        print("Usage: python callsign_lookup.py <CALLSIGN>")
        print("Example: python callsign_lookup.py KA21141")
        sys.exit(1)
    
    callsign = sys.argv[1]
    lookup = CallsignLookup()
    lookup.lookup_callsign(callsign)

if __name__ == '__main__':
    main()
