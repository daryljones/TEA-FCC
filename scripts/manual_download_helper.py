#!/usr/bin/env python3
"""
Manual Download Helper for FCC Complete Datasets

Since browser downloads work but Python requests timeout, this script helps you:
1. Get the complete dataset URLs to download manually
2. Process manually downloaded files
"""

import sys
from datetime import datetime
from pathlib import Path

def get_complete_dataset_urls():
    """Get complete FCC dataset URLs for manual download."""
    
    urls = {
        "LM_PRIVATE_LICENSES": "https://data.fcc.gov/download/pub/uls/complete/l_LMpriv.zip",      # ~378 MB
        "LM_PRIVATE_APPLICATIONS": "https://data.fcc.gov/download/pub/uls/complete/a_LMpriv.zip",  # ~637 MB
    }
    
    print("FCC Complete Dataset Manual Download Helper")
    print("=" * 60)
    print("Complete Land Mobile Private datasets")
    print()
    print("📊 Dataset sizes:")
    print("   Licenses (l_LMpriv.zip): ~378 MB")
    print("   Applications (a_LMpriv.zip): ~637 MB")
    print("   Total download: ~1.0 GB")
    print()
    print("💡 These are COMPLETE datasets (not daily increments)")
    print("   Updated weekly, contains all historical data")
    print()
    
    print("📥 URLs to download manually:")
    print()
    
    for name, url in urls.items():
        filename = f"{name.lower()}.zip"
        print(f"{name}:")
        print(f"  🌐 URL: {url}")
        print(f"  💾 Save as: downloads/{filename}")
        print()
    
    print("📋 INSTRUCTIONS:")
    print("1. Create/ensure 'downloads' directory exists")
    print("2. Download each URL above using your browser")
    print("3. Save files with the exact names shown")
    print("4. Run: uv run python manual_download_helper.py process")
    print()
    print("⚠️  Note: These are large files (~1GB total)")
    print("   Ensure you have sufficient disk space and good internet connection")
    print()

def check_manual_files():
    """Check if manually downloaded complete dataset files are ready for processing."""
    
    downloads_dir = Path("downloads")
    
    expected_files = [
        "lm_private_licenses.zip",
        "lm_private_applications.zip"
    ]
    
    print("Manual Download Status Check")
    print("=" * 50)
    
    all_present = True
    
    for filename in expected_files:
        file_path = downloads_dir / filename
        
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✅ {filename}: {size_mb:.1f} MB")
        else:
            print(f"❌ {filename}: Missing")
            all_present = False
    
    print()
    
    if all_present:
        print("🎉 All files present! Ready to process.")
        print("Run: uv run python manual_download_helper.py process")
    else:
        print("⚠️  Some files missing. Download them manually first.")
        print("Run: uv run python manual_download_helper.py")
    
    return all_present

def process_manual_files():
    """Process manually downloaded complete dataset files."""
    
    if not check_manual_files():
        return False
    
    print("\nProcessing manually downloaded complete datasets...")
    
    try:
        # Import and use the existing processor
        from main import FCCULSDownloader
        
        downloader = FCCULSDownloader()
        
        # Process each file
        downloads_dir = Path("downloads")
        
        files_to_process = [
            ("lm_private_licenses.zip", "licenses"),
            ("lm_private_applications.zip", "applications")
        ]
        
        for filename, table_name in files_to_process:
            file_path = downloads_dir / filename
            
            print(f"\nProcessing {filename}...")
            
            # Extract the file
            extract_dir = downloader.extract_zip_file(file_path)
            
            if extract_dir:
                # Process CSV files in the extracted directory
                csv_files = list(extract_dir.glob("*.dat"))
                
                if csv_files:
                    total_records = 0
                    for csv_file in csv_files:
                        records = downloader.process_csv_file(csv_file, table_name)
                        total_records += records
                    
                    print(f"✅ Processed {total_records} records from {filename}")
                else:
                    print(f"❌ No CSV/DAT files found in {filename}")
            else:
                print(f"❌ Failed to extract {filename}")
        
        print(f"\n🎉 Manual processing of complete datasets complete!")
        print("Run: uv run python main.py --stats")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing files: {e}")
        return False
    
    for name, url in urls.items():
        filename = f"{name.lower()}_{day}.zip"  # Include day in filename
        print(f"{name}:")
        print(f"  🌐 URL: {url}")
        print(f"  💾 Save as: downloads/{filename}")
        print()
    
    print("📋 INSTRUCTIONS:")
    print("1. Create/ensure 'downloads' directory exists")
    print("2. Download each URL above using your browser")
    print("3. Save files with the exact names shown (including day suffix)")
    print(f"4. Run: uv run python manual_download_helper.py process {day}")
    print()

def check_manual_files():
    """Check if manually downloaded files are ready for processing."""
    
    current_day = datetime.now().strftime('%a').lower()[:3]
    downloads_dir = Path("downloads")
    
    expected_files = [
        "lp_licenses.zip",
        "lp_applications.zip"
    ]
    
    print("Manual Download Status Check")
    print("=" * 50)
    
    all_present = True
    
    for filename in expected_files:
        file_path = downloads_dir / filename
        
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✅ {filename}: {size_mb:.1f} MB")
        else:
            print(f"❌ {filename}: Missing")
            all_present = False
    
    print()
    
    if all_present:
        print("🎉 All files present! Ready to process.")
        print("Run: uv run python manual_process.py")
    else:
        print("⚠️  Some files missing. Download them manually first.")
        print("Run: uv run python manual_download_helper.py")
    
    return all_present

def process_manual_files():
    """Process manually downloaded files."""
    
    if not check_manual_files():
        return False
    
    print("\nProcessing manually downloaded files...")
    
    try:
        # Import and use the existing processor
        from main import FCCULSDownloader
        
        downloader = FCCULSDownloader()
        
        # Process each file
        downloads_dir = Path("downloads")
        
        files_to_process = [
            ("lp_licenses.zip", "licenses"),
            ("lp_applications.zip", "applications")
        ]
        
        for filename, table_name in files_to_process:
            file_path = downloads_dir / filename
            
            print(f"\nProcessing {filename}...")
            
            # Extract the file
            extract_dir = downloader.extract_zip_file(file_path)
            
            if extract_dir:
                # Process CSV files in the extracted directory
                csv_files = list(extract_dir.glob("*.dat"))
                
                if csv_files:
                    total_records = 0
                    for csv_file in csv_files:
                        records = downloader.process_csv_file(csv_file, table_name)
                        total_records += records
                    
                    print(f"✅ Processed {total_records} records from {filename}")
                else:
                    print(f"❌ No CSV/DAT files found in {filename}")
            else:
                print(f"❌ Failed to extract {filename}")
        
        print(f"\n🎉 Manual processing complete!")
        print("Run: uv run python main.py --stats")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing files: {e}")
        return False

def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            check_manual_files()
        elif command == "process":
            process_manual_files()
        else:
            print("Usage: python manual_download_helper.py [check|process]")
            print()
            print("Examples:")
            print("  python manual_download_helper.py           # Show complete dataset URLs")
            print("  python manual_download_helper.py process   # Process downloaded files")
            print("  python manual_download_helper.py check     # Check download status")
    else:
        # Default: show complete dataset URLs
        get_complete_dataset_urls()

if __name__ == "__main__":
    main()
