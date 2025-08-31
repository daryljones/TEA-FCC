#!/usr/bin/env python3
"""
Add automatic cleanup functionality to main.py.
This patch adds cleanup of old downloads after successful processing.
"""

def add_cleanup_to_main():
    """Add cleanup functionality to main.py."""
    
    cleanup_code = '''
    def cleanup_old_downloads(self, days_to_keep=7):
        """Clean up old downloaded files to conserve disk space."""
        try:
            from datetime import datetime, timedelta
            import shutil
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            downloads_dir = Path(self.download_dir)
            
            if not downloads_dir.exists():
                return
            
            items_removed = 0
            space_freed = 0
            
            # Remove old ZIP files
            for zip_file in downloads_dir.glob("*.zip"):
                if zip_file.stat().st_mtime < cutoff_date.timestamp():
                    space_freed += zip_file.stat().st_size
                    zip_file.unlink()
                    items_removed += 1
                    logger.info(f"Cleaned up old download: {zip_file.name}")
            
            # Remove old extracted directories
            for extract_dir in downloads_dir.glob("extracted_*"):
                if extract_dir.is_dir() and extract_dir.stat().st_mtime < cutoff_date.timestamp():
                    # Calculate directory size before removing
                    dir_size = sum(f.stat().st_size for f in extract_dir.rglob('*') if f.is_file())
                    space_freed += dir_size
                    shutil.rmtree(extract_dir)
                    items_removed += 1
                    logger.info(f"Cleaned up old extracted directory: {extract_dir.name}")
            
            if items_removed > 0:
                logger.info(f"Cleanup completed: removed {items_removed} items, freed {space_freed / (1024*1024):.1f} MB")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
'''
    
    # Read main.py
    with open('../main.py', 'r') as f:
        content = f.read()
    
    # Find the FCCULSDownloader class and add the cleanup method
    class_start = content.find('class FCCULSDownloader:')
    if class_start == -1:
        print("❌ Could not find FCCULSDownloader class")
        return False
    
    # Find the end of the class (next class or end of file)
    next_class = content.find('\nclass ', class_start + 1)
    if next_class == -1:
        next_class = len(content)
    
    # Insert the cleanup method before the end of the class
    insertion_point = content.rfind('\n    def ', class_start, next_class)
    if insertion_point == -1:
        print("❌ Could not find insertion point")
        return False
    
    # Move to end of the found method
    method_end = content.find('\n\n', insertion_point + 1)
    if method_end == -1:
        method_end = content.find('\nclass', insertion_point + 1)
        if method_end == -1:
            method_end = len(content)
    
    # Insert the cleanup method
    new_content = content[:method_end] + '\n' + cleanup_code + content[method_end:]
    
    # Also add cleanup call after successful processing
    # Find the success point in download_and_process or process_data
    success_pattern = 'logger.info("Processing completed successfully")'
    success_pos = new_content.find(success_pattern)
    
    if success_pos != -1:
        # Add cleanup call after the success log
        line_end = new_content.find('\n', success_pos)
        cleanup_call = '\n        # Clean up old downloads to conserve disk space\n        self.cleanup_old_downloads(days_to_keep=7)'
        new_content = new_content[:line_end] + cleanup_call + new_content[line_end:]
    
    # Write the updated content
    with open('../main.py', 'w') as f:
        f.write(new_content)
    
    return True

if __name__ == "__main__":
    if add_cleanup_to_main():
        print("✅ Added automatic cleanup functionality to main.py")
        print("📋 Cleanup will:")
        print("   • Remove ZIP files older than 7 days")
        print("   • Remove extracted directories older than 7 days") 
        print("   • Run automatically after successful downloads")
        print("   • Log cleanup actions")
    else:
        print("❌ Failed to add cleanup functionality")
