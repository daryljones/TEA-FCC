#!/usr/bin/env python3
"""
Fix the file_path variable error in main.py
"""

import re

def fix_file_path_error():
    """Fix the undefined file_path variable in main.py."""
    
    # Read the current main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Replace the problematic line
    original = "is_license_data = 'licenses' in file_path.lower()"
    fixed = "is_license_data = 'licenses' in str(csv_path).lower()"
    
    if original in content:
        content = content.replace(original, fixed)
        
        # Write back the fixed content
        with open('main.py', 'w') as f:
            f.write(content)
        
        print("✅ Fixed file_path error in main.py")
        return True
    else:
        print("❌ Original text not found in main.py")
        return False

if __name__ == "__main__":
    fix_file_path_error()
