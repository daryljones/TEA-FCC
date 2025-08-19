#!/usr/bin/env python3
"""
FCC ULS Database Query Examples

This script demonstrates how to query the FCC ULS database to extract
useful information about licenses, frequencies, locations, antennas, etc.
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Any


class FCCQueryHelper:
    """Helper class for querying the FCC ULS database."""
    
    def __init__(self, db_path: str = "fcc_uls.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get comprehensive database statistics."""
        print("\n=== DATABASE STATISTICS ===")
        
        tables = ['licenses', 'entities', 'frequencies', 'locations', 'antennas', 'application_purpose']
        stats = {}
        
        for table in tables:
            query = f"SELECT COUNT(*) as count FROM {table}"
            result = self.execute_query(query)
            count = result[0]['count'] if result else 0
            stats[table] = count
            print(f"{table.title():20s}: {count:,}")
        
        # Additional statistics
        query = "SELECT COUNT(DISTINCT call_sign) as count FROM licenses WHERE license_status = 'A'"
        result = self.execute_query(query)
        active_callsigns = result[0]['count'] if result else 0
        print(f"{'Active Call Signs':20s}: {active_callsigns:,}")
        
        query = "SELECT COUNT(DISTINCT radio_service_type) as count FROM licenses"
        result = self.execute_query(query)
        service_types = result[0]['count'] if result else 0
        print(f"{'Service Types':20s}: {service_types:,}")
        
        return stats


def main():
    """Main function with example usage."""
    if len(sys.argv) < 2:
        print("FCC ULS Database Query Examples")
        print("\nUsage:")
        print("  python query_examples.py stats")
        print("\nExamples:")
        print("  python query_examples.py stats")
        return
    
    try:
        helper = FCCQueryHelper()
        command = sys.argv[1].lower()
        
        if command == "stats":
            helper.get_database_stats()
        else:
            print("Invalid command. Use 'stats' for now.")
    
    except FileNotFoundError:
        print("Database not found. Please run the downloader first to create the database.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
