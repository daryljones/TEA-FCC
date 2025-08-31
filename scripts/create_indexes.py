#!/usr/bin/env python3
"""
Create Database Indexes for FCC ULS Database

This script creates performance indexes to optimize queries
used by the enhanced lookup tool.
"""

import sqlite3
import time
import sys

def create_indexes(db_path='fcc_uls.db'):
    """Create performance indexes on the FCC ULS database."""
    
    print("🔧 Creating database indexes for improved performance...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute index creation SQL
        with open('sql/create_indexes.sql', 'r') as f:
            sql_commands = f.read()
        
        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        total_commands = len(commands)
        print(f"📊 Creating {total_commands} indexes...")
        
        start_time = time.time()
        
        for i, command in enumerate(commands, 1):
            try:
                print(f"  [{i:2d}/{total_commands}] Creating index...", end='', flush=True)
                index_start = time.time()
                
                cursor.execute(command)
                
                index_time = time.time() - index_start
                print(f" ✅ ({index_time:.2f}s)")
                
            except sqlite3.Error as e:
                print(f" ❌ Error: {e}")
        
        # Commit all changes
        conn.commit()
        
        total_time = time.time() - start_time
        print(f"\n🎉 Index creation completed in {total_time:.2f} seconds")
        
        # Analyze the database for query optimization
        print("📈 Analyzing database for query optimization...")
        cursor.execute("ANALYZE")
        conn.commit()
        
        # Show index statistics
        print("\n📋 Index Summary:")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        indexes = cursor.fetchall()
        
        print(f"   Total custom indexes: {len(indexes)}")
        
        # Group by table
        table_counts = {}
        for name, sql in indexes:
            if 'licenses' in name:
                table_counts['licenses'] = table_counts.get('licenses', 0) + 1
            elif 'entities' in name:
                table_counts['entities'] = table_counts.get('entities', 0) + 1
            elif 'frequencies' in name:
                table_counts['frequencies'] = table_counts.get('frequencies', 0) + 1
            elif 'locations' in name:
                table_counts['locations'] = table_counts.get('locations', 0) + 1
        
        for table, count in sorted(table_counts.items()):
            print(f"   {table}: {count} indexes")
        
        conn.close()
        
        print("\n💡 Performance Tips:")
        print("   • Callsign lookups should now be much faster")
        print("   • Name searches will benefit from entity_name index")
        print("   • Frequency searches are optimized with frequency_assigned index")
        print("   • Geographic queries use city/state indexes")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: create_indexes.sql file not found")
        return False
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_database_exists(db_path='fcc_uls.db'):
    """Check if the database exists and has data."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if main tables exist and have data
        tables = ['licenses', 'entities', 'frequencies', 'locations']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count == 0:
                print(f"⚠️  Warning: {table} table is empty")
                return False
        
        conn.close()
        return True
        
    except sqlite3.Error:
        print(f"❌ Error: Database {db_path} not found or corrupted")
        print("   Run 'uv run python main.py' to download and create the database first")
        return False

def main():
    """Main entry point."""
    print("🚀 FCC ULS Database Index Creator")
    print("=" * 50)
    
    # Check if database exists
    if not check_database_exists():
        sys.exit(1)
    
    # Create indexes
    if create_indexes():
        print("\n✅ Database indexes created successfully!")
        print("\n🔍 Test the performance improvement:")
        print("   uv run python enhanced_lookup.py --name 'MARRIOTT'")
        print("   uv run python enhanced_lookup.py --freq 465.0")
        print("   uv run python enhanced_lookup.py KA21141")
    else:
        print("\n❌ Failed to create indexes")
        sys.exit(1)

if __name__ == '__main__':
    main()
