#!/usr/bin/env python3
"""
Setup Full-Text Search (FTS5) for faster entity name searching.
This will create a virtual table using SQLite's FTS5 extension for much faster text searches.
"""

import sqlite3
import sys
import time
from typing import List, Tuple

def setup_fts5_table(db_path: str) -> None:
    """Create FTS5 virtual table for entity names and populate it."""
    
    print("Setting up FTS5 virtual table for entity names...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if FTS5 is available
        cursor.execute("SELECT sqlite_version(), sqlite_compileoption_used('ENABLE_FTS5')")
        version, fts5_enabled = cursor.fetchone()
        print(f"SQLite version: {version}")
        print(f"FTS5 enabled: {fts5_enabled}")
        
        if not fts5_enabled:
            print("❌ FTS5 is not available in this SQLite build")
            return
        
        # Drop existing FTS table if it exists
        cursor.execute("DROP TABLE IF EXISTS entities_fts")
        
        # Create FTS5 virtual table
        print("Creating FTS5 virtual table...")
        cursor.execute("""
            CREATE VIRTUAL TABLE entities_fts USING fts5(
                unique_system_identifier,
                entity_name,
                entity_type,
                state,
                first_name,
                last_name,
                content=entities
            )
        """)
        
        # Populate the FTS table
        print("Populating FTS5 table...")
        start_time = time.time()
        
        cursor.execute("""
            INSERT INTO entities_fts(
                unique_system_identifier,
                entity_name, 
                entity_type,
                state,
                first_name,
                last_name
            )
            SELECT 
                unique_system_identifier,
                COALESCE(entity_name, '') as entity_name,
                entity_type,
                COALESCE(state, '') as state,
                COALESCE(first_name, '') as first_name,
                COALESCE(last_name, '') as last_name
            FROM entities
        """)
        
        populate_time = time.time() - start_time
        
        # Get count of records
        cursor.execute("SELECT COUNT(*) FROM entities_fts")
        count = cursor.fetchone()[0]
        
        print(f"✅ Populated {count:,} records in {populate_time:.1f} seconds")
        
        # Create index on the rebuild table for better performance
        print("Optimizing FTS5 table...")
        cursor.execute("INSERT INTO entities_fts(entities_fts) VALUES('optimize')")
        
        conn.commit()
        print("✅ FTS5 setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up FTS5: {e}")
        conn.rollback()
    finally:
        conn.close()

def test_fts5_performance(db_path: str) -> None:
    """Test FTS5 search performance."""
    
    print("\nTesting FTS5 search performance...")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if FTS table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='entities_fts'
    """)
    
    if not cursor.fetchone():
        print("❌ FTS5 table not found. Run setup first.")
        conn.close()
        return
    
    test_searches = [
        "MARRIOTT",
        "WALMART", 
        "POLICE",
        "CITY",
        "FIRE"
    ]
    
    for search_term in test_searches:
        print(f'Testing FTS5 search for "{search_term}"...')
        
        start_time = time.time()
        
        # FTS5 search query
        cursor.execute("""
            SELECT 
                f.unique_system_identifier,
                f.entity_name,
                f.entity_type,
                f.state,
                f.first_name,
                f.last_name
            FROM entities_fts f
            WHERE entities_fts MATCH ?
            ORDER BY bm25(entities_fts)
            LIMIT 50
        """, (search_term,))
        
        results = cursor.fetchall()
        search_time = time.time() - start_time
        
        print(f"  ✅ Found {len(results)} results in {search_time:.3f} seconds")
        if results:
            print(f"  Sample: {results[0][1]} ({results[0][2]}) - {results[0][3]}")
        print()
    
    conn.close()

if __name__ == "__main__":
    db_path = "fcc_uls.db"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_fts5_performance(db_path)
        else:
            db_path = sys.argv[1]
            setup_fts5_table(db_path)
            test_fts5_performance(db_path)
    else:
        setup_fts5_table(db_path)
        test_fts5_performance(db_path)
