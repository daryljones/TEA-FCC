#!/usr/bin/env python3
"""
FCC Server Status Checker

This utility checks if the FCC ULS servers are currently accessible
and not showing error messages like "An unexpected error occurred".
"""

import requests
import sys
from datetime import datetime
import argparse

def check_fcc_status(verbose=False):
    """Check FCC server status and return True if accessible."""
    urls_to_check = [
        ("FCC ULS Main Page", "https://www.fcc.gov/uls/transactions/daily-weekly"),
        ("FCC ULS Search", "https://wireless2.fcc.gov/UlsApp/UlsSearch/searchLicense.jsp"),
        ("FCC Main Site", "https://www.fcc.gov")
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    results = {}
    overall_status = True
    
    print(f"FCC Server Status Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    for name, url in urls_to_check:
        try:
            if verbose:
                print(f"Checking {name}...")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for error messages
                error_phrases = [
                    "unexpected error occurred",
                    "please check back later",
                    "service temporarily unavailable",
                    "maintenance mode",
                    "server error",
                    "503 service unavailable",
                    "502 bad gateway",
                    "500 internal server error"
                ]
                
                found_errors = []
                for phrase in error_phrases:
                    if phrase in content:
                        found_errors.append(phrase)
                
                if found_errors:
                    status = "❌ ERROR"
                    message = f"Error messages found: {', '.join(found_errors)}"
                    overall_status = False
                else:
                    status = "✅ OK"
                    message = "Accessible and responsive"
                
                results[name] = {
                    'status': status,
                    'message': message,
                    'response_time': response.elapsed.total_seconds()
                }
                
            else:
                status = "❌ ERROR"
                message = f"HTTP {response.status_code}"
                results[name] = {
                    'status': status,
                    'message': message,
                    'response_time': response.elapsed.total_seconds()
                }
                overall_status = False
                
        except requests.exceptions.Timeout:
            status = "❌ TIMEOUT"
            message = "Request timed out after 30 seconds"
            results[name] = {
                'status': status,
                'message': message,
                'response_time': None
            }
            overall_status = False
            
        except requests.exceptions.RequestException as e:
            status = "❌ ERROR"
            message = f"Connection error: {str(e)[:100]}"
            results[name] = {
                'status': status,
                'message': message,
                'response_time': None
            }
            overall_status = False
            
        except Exception as e:
            status = "❌ ERROR"
            message = f"Unexpected error: {str(e)[:100]}"
            results[name] = {
                'status': status,
                'message': message,
                'response_time': None
            }
            overall_status = False
    
    # Display results
    for name, result in results.items():
        status = result['status']
        message = result['message']
        response_time = result.get('response_time')
        
        if response_time:
            print(f"{status} {name:<25} ({response_time:.2f}s)")
        else:
            print(f"{status} {name:<25}")
        
        if verbose or "ERROR" in status or "TIMEOUT" in status:
            print(f"    {message}")
    
    print("\n" + "=" * 60)
    
    if overall_status:
        print("✅ FCC servers appear to be operational")
        print("   Downloads should work normally")
        return True
    else:
        print("❌ FCC servers are experiencing issues")
        print("   Consider waiting before attempting downloads")
        print("   Check https://www.fcc.gov for service announcements")
        return False

def check_specific_download_urls():
    """Check if specific download URLs are accessible."""
    print("\nChecking Download URLs...")
    print("-" * 30)
    
    # These are example URLs - they change weekly
    test_urls = [
        "https://www.fcc.gov/file/39434/download",  # Example LM Licenses
        "https://www.fcc.gov/file/39433/download",  # Example LM Applications
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    for url in test_urls:
        try:
            response = requests.head(url, headers=headers, timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                size = response.headers.get('content-length', 'Unknown')
                content_type = response.headers.get('content-type', 'Unknown')
                print(f"✅ {url}")
                print(f"   Size: {size} bytes, Type: {content_type}")
            else:
                print(f"❌ {url} (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"❌ {url} (Error: {str(e)[:50]}...)")
    
    print("\nNote: Download URLs change weekly. If these fail,")
    print("run 'uv run python discover_urls.py' to find current URLs.")

def main():
    parser = argparse.ArgumentParser(description="Check FCC server status")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Show detailed information")
    parser.add_argument("--download-urls", action="store_true",
                       help="Also check specific download URLs")
    parser.add_argument("--wait-for-ok", action="store_true",
                       help="Keep checking until servers are OK")
    
    args = parser.parse_args()
    
    if args.wait_for_ok:
        import time
        print("Waiting for FCC servers to become available...")
        attempt = 1
        
        while True:
            print(f"\nAttempt {attempt}:")
            if check_fcc_status(args.verbose):
                print("✅ FCC servers are now available!")
                break
            else:
                print("⏳ Servers still experiencing issues. Waiting 5 minutes...")
                time.sleep(300)  # Wait 5 minutes
                attempt += 1
    else:
        status_ok = check_fcc_status(args.verbose)
        
        if args.download_urls:
            check_specific_download_urls()
        
        sys.exit(0 if status_ok else 1)

if __name__ == "__main__":
    main()
