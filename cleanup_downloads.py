#!/usr/bin/env python3
"""
Automatic cleanup script for old FCC downloaded data.
Helps conserve disk space by removing old downloads while keeping the most recent.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import shutil

def get_directory_size(path):
    """Calculate total size of directory in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def format_size(bytes_size):
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def list_download_files():
    """List all download files and directories with their dates and sizes."""
    downloads_dir = Path("downloads")
    
    if not downloads_dir.exists():
        print("❌ Downloads directory not found")
        return []
    
    items = []
    
    # ZIP files
    for zip_file in downloads_dir.glob("*.zip"):
        mod_time = datetime.fromtimestamp(zip_file.stat().st_mtime)
        size = zip_file.stat().st_size
        items.append({
            'path': zip_file,
            'type': 'zip',
            'date': mod_time,
            'size': size,
            'name': zip_file.name
        })
    
    # Extracted directories
    for extract_dir in downloads_dir.glob("extracted_*"):
        if extract_dir.is_dir():
            mod_time = datetime.fromtimestamp(extract_dir.stat().st_mtime)
            size = get_directory_size(extract_dir)
            items.append({
                'path': extract_dir,
                'type': 'directory',
                'date': mod_time,
                'size': size,
                'name': extract_dir.name
            })
    
    return sorted(items, key=lambda x: x['date'], reverse=True)

def cleanup_old_files(days_to_keep=7, dry_run=True):
    """
    Clean up old downloaded files.
    
    Args:
        days_to_keep: Number of days of files to keep (default: 7)
        dry_run: If True, only show what would be deleted (default: True)
    """
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    items = list_download_files()
    
    if not items:
        print("📂 No download files found")
        return
    
    print(f"🧹 FCC Downloads Cleanup")
    print(f"📅 Keeping files newer than: {cutoff_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"⏳ Files older than {days_to_keep} days will be {'REMOVED' if not dry_run else 'MARKED FOR REMOVAL'}")
    print("=" * 70)
    
    total_current_size = sum(item['size'] for item in items)
    total_to_remove = 0
    files_to_remove = []
    files_to_keep = []
    
    for item in items:
        age_days = (datetime.now() - item['date']).days
        status = "KEEP" if item['date'] > cutoff_date else "REMOVE"
        
        if status == "REMOVE":
            files_to_remove.append(item)
            total_to_remove += item['size']
        else:
            files_to_keep.append(item)
        
        print(f"{status:6} | {item['type']:9} | {format_size(item['size']):>8} | {age_days:3}d | {item['name']}")
    
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"   Current total size: {format_size(total_current_size)}")
    print(f"   Files to keep: {len(files_to_keep)} ({format_size(total_current_size - total_to_remove)})")
    print(f"   Files to remove: {len(files_to_remove)} ({format_size(total_to_remove)})")
    print(f"   Space to free: {format_size(total_to_remove)}")
    
    if files_to_remove and not dry_run:
        print(f"\n🗑️  Removing {len(files_to_remove)} old items...")
        
        for item in files_to_remove:
            try:
                if item['type'] == 'directory':
                    shutil.rmtree(item['path'])
                    print(f"   ✅ Removed directory: {item['name']}")
                else:
                    item['path'].unlink()
                    print(f"   ✅ Removed file: {item['name']}")
            except Exception as e:
                print(f"   ❌ Failed to remove {item['name']}: {e}")
        
        print(f"✅ Cleanup complete! Freed {format_size(total_to_remove)}")
    
    elif files_to_remove and dry_run:
        print(f"\n🔍 DRY RUN: Add --execute to actually remove files")
        print(f"   Command: uv run python cleanup_downloads.py --days {days_to_keep} --execute")

def main():
    """Main function with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FCC Downloads Cleanup Tool")
    parser.add_argument("--days", type=int, default=7,
                       help="Number of days of files to keep (default: 7)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually remove files (default: dry run)")
    parser.add_argument("--list", action="store_true",
                       help="List all download files and exit")
    
    args = parser.parse_args()
    
    if args.list:
        items = list_download_files()
        if items:
            print("📂 FCC Download Files:")
            print("=" * 70)
            print("TYPE      | SIZE     | AGE  | NAME")
            print("-" * 70)
            for item in items:
                age_days = (datetime.now() - item['date']).days
                print(f"{item['type']:9} | {format_size(item['size']):>8} | {age_days:3}d | {item['name']}")
            
            total_size = sum(item['size'] for item in items)
            print("=" * 70)
            print(f"Total: {len(items)} items, {format_size(total_size)}")
        else:
            print("📂 No download files found")
    else:
        cleanup_old_files(days_to_keep=args.days, dry_run=not args.execute)

if __name__ == "__main__":
    main()
