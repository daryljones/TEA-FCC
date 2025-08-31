#!/usr/bin/env python3
"""
FCC ULS Web Lookup Tool
A Flask web application for searching the FCC ULS Land Mobile database.
"""

import sqlite3
import os
from flask import Flask, render_template, request, jsonify
from typing import List, Dict, Any, Optional

app = Flask(__name__)

# Database path - adjust relative to the webapp directory
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'fcc_uls.db')

class FCCLookup:
    """Database lookup functionality for FCC ULS data."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        return sqlite3.connect(self.db_path)
    
    def lookup_callsign(self, callsign: str) -> Dict[str, Any]:
        """Look up information for a specific callsign."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get license information
            cursor.execute("""
                SELECT l.unique_system_identifier, l.call_sign, l.radio_service_type, 
                       l.grant_date, l.expired_date, l.cancellation_date, l.eligibility_rule_num,
                       COALESCE(e.applicant_type_code, l.applicant_type_code) as applicant_type_code, 
                       l.alien, l.alien_government, l.alien_corporation, 
                       l.alien_officer, l.alien_control, l.revoked, l.convicted, l.adjudged,
                       l.common_carrier, l.non_common_carrier, l.private_comm, l.fixed,
                       l.mobile, l.radiolocation, l.satellite, l.developmental_or_sta,
                       l.interconnected_service, l.certifier_first_name, l.certifier_last_name,
                       l.certifier_suffix, l.certifier_title, l.gender, l.african_american,
                       l.native_american, l.hawaiian, l.asian, l.white, l.ethnicity, l.license_status
                FROM entities e
                LEFT JOIN licenses l ON e.call_sign = l.call_sign
                WHERE e.call_sign = ? AND e.entity_type IN ('L', 'CL')
                ORDER BY 
                    CASE 
                        WHEN l.license_status IS NOT NULL AND l.license_status != '' 
                             AND l.grant_date IS NOT NULL AND l.grant_date != '' THEN 1
                        WHEN l.license_status IS NOT NULL AND l.license_status != '' THEN 2
                        ELSE 3
                    END,
                    l.expired_date DESC
                LIMIT 1
            """, (callsign.upper(),))
            
            license_info = cursor.fetchone()
            if not license_info:
                return {"error": "Callsign not found"}
            
            # Get licensee information (entity_type = 'L' or 'CL')
            cursor.execute("""
                SELECT entity_name, first_name, last_name, city, state, 
                       zip_code, phone, fax, email, applicant_type_code, entity_type
                FROM entities 
                WHERE call_sign = ? AND entity_type IN ('L', 'CL')
                ORDER BY entity_type
            """, (callsign.upper(),))
            
            licensee_info = cursor.fetchone()
            
            # Get contact information (entity_type = 'CL')
            cursor.execute("""
                SELECT entity_name, entity_type, first_name, mi, last_name,
                       suffix, phone, fax, email, street_address, city, state, zip_code,
                       po_box, attention_line, frn, applicant_type_code
                FROM entities 
                WHERE call_sign = ? AND entity_type = 'CL'
            """, (callsign.upper(),))
            
            contact_info = cursor.fetchone()
            
            # Get frequency information
            cursor.execute("""
                SELECT frequency_number, frequency_seq_id, frequency_assigned,
                       frequency_upper_band, frequency_carrier, frequency_offset,
                       emission_designator, power_output, power_erp, tolerance,
                       status_code
                FROM frequencies 
                WHERE call_sign = ?
                ORDER BY frequency_number, frequency_seq_id, frequency_assigned
            """, (callsign.upper(),))
            
            frequencies = cursor.fetchall()
            
            # Get location information
            cursor.execute("""
                SELECT location_number, location_type_code, location_class_code,
                       location_address, location_city, location_county, location_state,
                       radius_of_operation, area_of_operation_code, clearance_indicator,
                       ground_elevation, lat_degrees, lat_minutes, lat_seconds, lat_direction,
                       long_degrees, long_minutes, long_seconds, long_direction,
                       max_lat_degrees, max_lat_minutes, max_lat_seconds, max_lat_direction,
                       max_long_degrees, max_long_minutes, max_long_seconds, max_long_direction,
                       nepa, quiet_zone_notification_date, tower_registration_number,
                       height_of_support_structure, overall_height_of_structure,
                       structure_type, airport_id, location_name, units_hand_held,
                       units_mobile, units_temp_fixed, units_aircraft, units_itinerant
                FROM locations 
                WHERE call_sign = ?
                ORDER BY location_number
            """, (callsign.upper(),))
            
            locations = cursor.fetchall()
            
            return {
                "license": license_info,
                "licensee": licensee_info,
                "contact": contact_info,
                "frequencies": frequencies,
                "locations": locations
            }
    
    def search_by_licensee(self, name: str, state: Optional[str] = None, limit: int = 150) -> List[Dict[str, Any]]:
        """Search by licensee name using simple case-insensitive string match with wildcard at end. Only shows licensed records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Simple case-insensitive search with wildcard at the end
            name_upper = name.upper().strip()
            
            # Build query with GROUP BY to eliminate duplicates per callsign
            # Only include records with actual call signs (licensed records)
            query = """
                SELECT e.call_sign, e.entity_name, e.first_name, e.last_name,
                       e.city, e.state, 
                       MIN(l.grant_date) as earliest_grant_date, 
                       MAX(l.expired_date) as latest_expired_date
                FROM entities e
                INNER JOIN licenses l ON e.call_sign = l.call_sign
                WHERE e.entity_type IN ('L', 'CL')
                AND e.call_sign IS NOT NULL AND e.call_sign != ''
                AND l.call_sign IS NOT NULL AND l.call_sign != ''
                AND (
                    UPPER(e.entity_name) LIKE ? OR 
                    UPPER(e.first_name || ' ' || e.last_name) LIKE ?
                )
            """
            
            # Add wildcard at the end of search term
            search_term = f"{name_upper}%"
            params = [search_term, search_term]
            
            # Add state filter if specified
            if state:
                query += " AND e.state = ?"
                params.append(state.upper())
            
            # Group by callsign to eliminate duplicates, then order and limit
            query += """
                GROUP BY e.call_sign, e.entity_name, e.first_name, e.last_name, e.city, e.state
                ORDER BY e.entity_name, e.last_name 
                LIMIT ?
            """
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Enhance results with frequency and location summaries
            enhanced_results = []
            for result in results:
                call_sign = result[0]
                
                # Get frequency summary
                cursor.execute("""
                    SELECT COUNT(*) as freq_count,
                           MIN(frequency_assigned) as min_freq,
                           MAX(frequency_assigned) as max_freq,
                           GROUP_CONCAT(DISTINCT printf('%.4f', frequency_assigned) ORDER BY frequency_assigned) as freq_list
                    FROM frequencies 
                    WHERE call_sign = ? AND frequency_assigned IS NOT NULL
                """, (call_sign,))
                freq_summary = cursor.fetchone()
                
                # Get location summary
                cursor.execute("""
                    SELECT COUNT(*) as loc_count,
                           GROUP_CONCAT(DISTINCT location_city || ', ' || location_state ORDER BY location_city) as locations
                    FROM locations 
                    WHERE call_sign = ? AND location_city IS NOT NULL AND location_city != ''
                """, (call_sign,))
                loc_summary = cursor.fetchone()
                
                # Combine all data
                enhanced_result = {
                    'call_sign': call_sign,
                    'entity_name': result[1],
                    'first_name': result[2],
                    'last_name': result[3],
                    'city': result[4],
                    'state': result[5],
                    'earliest_grant_date': result[6],
                    'latest_expired_date': result[7],
                    'frequency_count': freq_summary[0] if freq_summary else 0,
                    'min_frequency': freq_summary[1] if freq_summary else None,
                    'max_frequency': freq_summary[2] if freq_summary else None,
                    'frequency_list': freq_summary[3] if freq_summary else '',
                    'location_count': loc_summary[0] if loc_summary else 0,
                    'locations': loc_summary[1] if loc_summary else ''
                }
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
    
    def search_by_frequency(self, frequency: float, tolerance: float = 0.001, 
                          state: Optional[str] = None, limit: int = 150) -> List[Dict[str, Any]]:
        """Search by frequency, only showing licensed records (no applications)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            freq_min = frequency - tolerance
            freq_max = frequency + tolerance
            
            # Query for licensed records only (with both call signs and active licenses)
            query = """
                SELECT l.call_sign, 
                       COALESCE(e.entity_name, 'Unknown Licensee') as entity_name, 
                       COALESCE(e.first_name, '') as first_name, 
                       COALESCE(e.last_name, '') as last_name,
                       COALESCE(e.city, '') as city, 
                       COALESCE(e.state, '') as state, 
                       f.frequency_assigned,
                       MAX(COALESCE(f.power_erp, f.power_output, 0)) as max_power,
                       GROUP_CONCAT(DISTINCT f.emission_designator) as emissions,
                       'licensed' as record_type
                FROM frequencies f
                INNER JOIN licenses l ON f.call_sign = l.call_sign
                LEFT JOIN entities e ON f.call_sign = e.call_sign AND e.entity_type IN ('L', 'CL')
                WHERE f.call_sign IS NOT NULL 
                AND l.call_sign IS NOT NULL
                AND f.frequency_assigned BETWEEN ? AND ?
            """
            params = [freq_min, freq_max]
            
            if state and state.upper() != '':
                query += " AND (e.state = ? OR e.state IS NULL)"
                params.append(state.upper())
            
            query += """
                GROUP BY f.call_sign, f.frequency_assigned
                ORDER BY f.frequency_assigned, COALESCE(e.entity_name, f.call_sign)
                LIMIT ?
            """
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return results

# Initialize the lookup service
fcc_lookup = FCCLookup(DB_PATH)

@app.route('/')
def index():
    """Main search page."""
    return render_template('index.html')

@app.route('/api/callsign/<callsign>')
def api_callsign_lookup(callsign: str):
    """API endpoint for callsign lookup."""
    try:
        result = fcc_lookup.lookup_callsign(callsign)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/licensee')
def api_licensee_search():
    """API endpoint for licensee name search."""
    try:
        name = request.args.get('name', '')
        state = request.args.get('state', '')
        limit = int(request.args.get('limit', 150))
        
        if not name:
            return jsonify({"error": "Name parameter is required"}), 400
        
        results = fcc_lookup.search_by_licensee(
            name, 
            state if state else None, 
            limit
        )
        
        return jsonify({
            "results": results,
            "count": len(results),
            "search_params": {
                "name": name,
                "state": state,
                "limit": limit
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/frequency')
def api_frequency_search():
    """API endpoint for frequency search."""
    try:
        frequency = float(request.args.get('frequency', 0))
        tolerance = float(request.args.get('tolerance', 0.001))
        state = request.args.get('state', '')
        limit = int(request.args.get('limit', 150))
        
        if frequency <= 0:
            return jsonify({"error": "Valid frequency parameter is required"}), 400
        
        results = fcc_lookup.search_by_frequency(
            frequency, 
            tolerance, 
            state if state else None, 
            limit
        )
        
        return jsonify({
            "results": results,
            "count": len(results),
            "search_params": {
                "frequency": frequency,
                "tolerance": tolerance,
                "state": state,
                "limit": limit
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/callsign/<callsign>')
def callsign_detail(callsign: str):
    """Detailed callsign view."""
    try:
        result = fcc_lookup.lookup_callsign(callsign)
        if "error" in result:
            return render_template('error.html', error=result["error"])
        
        # Get return URL from query parameter
        return_url = request.args.get('return', '/')
        
        return render_template('callsign_detail.html', 
                             callsign=callsign, 
                             data=result, 
                             return_url=return_url)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run the main.py script first to download and create the database.")
        exit(1)
    
    print(f"Starting FCC ULS Web Lookup Tool...")
    print(f"Database: {DB_PATH}")
    print(f"📡 Local access: http://localhost:5001")
    print(f"🌐 Network access: http://<YOUR_IP_ADDRESS>:5001")
    print(f"   (Replace <YOUR_IP_ADDRESS> with your actual IP for remote access)")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
