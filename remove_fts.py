#!/usr/bin/env python3
"""
Remove Full-Text Search (FTS5) table and related code cleanup.
This script will drop the entities_fts virtual table to clean up the database.
"""

import sqlite3
import sys
import os

def remove_fts_table(db_path: str) -> None:
    """Remove FTS5 virtual table from the database."""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print("Removing FTS5 virtual table...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if FTS table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='entities_fts'
        """)
        
        if cursor.fetchone():
            print("Found entities_fts table, dropping it...")
            cursor.execute("DROP TABLE entities_fts")
            conn.commit()
            print("✅ Successfully removed entities_fts table")
        else:
            print("ℹ️ No entities_fts table found, nothing to remove")
        
        # Show remaining table count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        print(f"Database now has {table_count} tables")
        
    except sqlite3.Error as e:
        print(f"❌ Error removing FTS table: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    db_path = "fcc_uls.db"
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"Database: {db_path}")
    remove_fts_table(db_path)

if __name__ == "__main__":
    main()
