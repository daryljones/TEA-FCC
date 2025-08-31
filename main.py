#!/usr/bin/env python3
"""
FCC ULS Land Mobile Database Downloader

This script downloads the FCC ULS (Universal Licensing System) land mobile database
and stores it in a local SQLite database. It can be scheduled to run daily.
"""

import os
import sqlite3
import zipfile
import csv
import requests
import schedule
import time
import logging
import subprocess
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from tqdm import tqdm

# FCC connectivity fixes
from requests.adapters import HTTPAdapter
import urllib3
import ssl

# Increase CSV field size limit for large FCC data files
csv.field_size_limit(sys.maxsize)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fcc_uls_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HTTP11Adapter(HTTPAdapter):
    """
    Custom adapter to force HTTP/1.1 and handle FCC server issues.
    
    The FCC servers have HTTP/2 protocol issues that cause timeouts
    and connection errors. This adapter forces HTTP/1.1 connections.
    """
    
    def init_poolmanager(self, *args, **kwargs):
        # Create SSL context that forces HTTP/1.1
        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(['http/1.1'])
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


class FCCULSDownloader:
    """Downloads and processes FCC ULS Land Mobile database files."""
    
    def __init__(self, db_path: str = "fcc_uls.db", download_dir: str = "downloads"):
        self.db_path = Path(db_path)
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # FCC ULS download URLs - Using complete datasets from data.fcc.gov
        self.base_url = "https://data.fcc.gov/download/pub/uls/complete/"
        
        # Complete database URLs for Land Mobile Private (LMpriv) services
        # These are complete datasets updated weekly, much more comprehensive than daily files
        self.file_urls = {
            # Land Mobile Private Service complete datasets
            "LM_PRIVATE_LICENSES": "https://data.fcc.gov/download/pub/uls/complete/l_LMpriv.zip",      # ~378 MB
            "LM_PRIVATE_APPLICATIONS": "https://data.fcc.gov/download/pub/uls/complete/a_LMpriv.zip",  # ~637 MB
        }
        
        # Initialize database
        self.init_database()
    
    def _create_fcc_session(self):
        """
        Create a requests session configured to work with FCC servers.
        
        Returns:
            requests.Session: Configured session for FCC requests
        """
        session = requests.Session()
        
        # data.fcc.gov works fine with regular requests, but we'll keep browser headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        })
        
        return session

    def download_file_with_curl(self, url: str, filename: str, retry_count: int = 3) -> Optional[Path]:
        """
        Download a file using curl (more reliable than Python requests for FCC servers).
        
        Args:
            url: URL to download from
            filename: Local filename to save as
            retry_count: Number of retry attempts
            
        Returns:
            Path to downloaded file if successful, None otherwise
        """
        file_path = self.download_dir / filename
        
        # Ensure download directory exists
        self.download_dir.mkdir(exist_ok=True)
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt * 60  # Exponential backoff: 2, 4, 8 minutes
                    logger.info(f"Waiting {wait_time} seconds before retry attempt {attempt + 1}")
                    time.sleep(wait_time)
                
                logger.info(f"Downloading {filename} from {url} using curl (attempt {attempt + 1}/{retry_count})")
                
                # Check if curl is available
                if not shutil.which('curl'):
                    logger.error("curl command not found. Please install curl or use manual download method.")
                    return None
                
                # Prepare curl command with progress bar and resume capability
                curl_cmd = [
                    'curl',
                    '-L',  # Follow redirects
                    '-C', '-',  # Resume partial downloads
                    '--progress-bar',  # Show progress bar
                    '--max-time', '600',  # 10 minute timeout
                    '--retry', '3',  # Retry on transient errors
                    '--retry-delay', '5',  # Wait 5 seconds between retries
                    '--user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    '--output', str(file_path),
                    url
                ]
                
                # Run curl command
                logger.info(f"Running: {' '.join(curl_cmd[:8])} ... {url}")
                result = subprocess.run(curl_cmd, capture_output=False, text=True)
                
                if result.returncode == 0:
                    # Verify file was downloaded properly
                    if file_path.exists() and file_path.stat().st_size > 0:
                        file_size = file_path.stat().st_size
                        logger.info(f"Downloaded {filename} successfully ({file_size:,} bytes)")
                        return file_path
                    else:
                        raise Exception("Downloaded file is empty or missing")
                else:
                    raise Exception(f"curl failed with exit code {result.returncode}")
                    
            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {filename}: {e}")
                if attempt == retry_count - 1:
                    logger.error(f"All {retry_count} download attempts failed for {filename}")
                    return None
                    
        return None

    def get_dataset_info(self) -> dict:
        """Get information about the complete datasets."""
        dataset_info = {}
        
        logger.info("Checking dataset information...")
        
        session = self._create_fcc_session()
        
        for name, url in self.file_urls.items():
            try:
                response = session.head(url, timeout=15)
                if response.status_code == 200:
                    size = int(response.headers.get('content-length', 0))
                    size_mb = size / (1024 * 1024)
                    last_modified = response.headers.get('last-modified', 'unknown')
                    
                    dataset_info[name] = {
                        'size_mb': size_mb,
                        'last_modified': last_modified,
                        'url': url
                    }
                    
                    logger.info(f"  {name}: {size_mb:.1f} MB (Modified: {last_modified})")
                else:
                    logger.warning(f"  {name}: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"  {name}: Error - {e}")
        
        return dataset_info

    def init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create main license table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS licenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT UNIQUE,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        license_status TEXT,
                        radio_service_type TEXT,
                        grant_date TEXT,
                        expired_date TEXT,
                        cancellation_date TEXT,
                        eligibility_rule_num TEXT,
                        applicant_type_code TEXT,
                        alien TEXT,
                        alien_government TEXT,
                        alien_corporation TEXT,
                        alien_officer TEXT,
                        alien_control TEXT,
                        revoked TEXT,
                        convicted TEXT,
                        adjudged TEXT,
                        involved_reserved TEXT,
                        common_carrier TEXT,
                        non_common_carrier TEXT,
                        private_comm TEXT,
                        fixed TEXT,
                        mobile TEXT,
                        radiolocation TEXT,
                        satellite TEXT,
                        developmental_or_sta TEXT,
                        interconnected_service TEXT,
                        certifier_first_name TEXT,
                        certifier_mi TEXT,
                        certifier_last_name TEXT,
                        certifier_suffix TEXT,
                        certifier_title TEXT,
                        gender TEXT,
                        african_american TEXT,
                        native_american TEXT,
                        hawaiian TEXT,
                        asian TEXT,
                        white TEXT,
                        ethnicity TEXT,
                        effective_date TEXT,
                        last_action_date TEXT,
                        auction_id TEXT,
                        reg_stat_broad_serv TEXT,
                        band_manager TEXT,
                        type_serv_broad_serv TEXT,
                        alien_ruling TEXT,
                        licensee_name_change TEXT,
                        whitespace_ind TEXT,
                        additional_cert_choice TEXT,
                        additional_cert_answer TEXT,
                        discontinuation_ind TEXT,
                        regulatory_compliance_ind TEXT,
                        eligibility_cert_900 TEXT,
                        transition_plan_cert_900 TEXT,
                        return_spectrum_cert_900 TEXT,
                        payment_cert_900 TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create entity table for license holders
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT UNIQUE,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        entity_type TEXT,
                        licensee_id TEXT,
                        entity_name TEXT,
                        first_name TEXT,
                        mi TEXT,
                        last_name TEXT,
                        suffix TEXT,
                        phone TEXT,
                        fax TEXT,
                        email TEXT,
                        street_address TEXT,
                        city TEXT,
                        state TEXT,
                        zip_code TEXT,
                        po_box TEXT,
                        attention_line TEXT,
                        sgin TEXT,
                        frn TEXT,
                        applicant_type_code TEXT,
                        applicant_type_other TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        lic_category_code TEXT,
                        linked_license_id TEXT,
                        linked_callsign TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier)
                    )
                ''')
                
                # Create download history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS download_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_type TEXT,
                        file_size INTEGER,
                        records_processed INTEGER,
                        success BOOLEAN,
                        error_message TEXT
                    )
                ''')
                
                # Create frequencies table for technical data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS frequencies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        frequency_assigned REAL,
                        frequency_upper_band REAL,
                        frequency_carrier REAL,
                        frequency_offset REAL,
                        emission_designator TEXT,
                        power_output REAL,
                        power_erp REAL,
                        tolerance REAL,
                        frequency_number INTEGER,
                        frequency_seq_id INTEGER,
                        status_code TEXT,
                        status_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier),
                        UNIQUE(unique_system_identifier, frequency_number, frequency_seq_id)
                    )
                ''')
                
                # Create locations table for geographic data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        location_action_performed TEXT,
                        location_type_code TEXT,
                        location_class_code TEXT,
                        location_number INTEGER,
                        site_status TEXT,
                        corresponding_fixed_location INTEGER,
                        location_address TEXT,
                        location_city TEXT,
                        location_county TEXT,
                        location_state TEXT,
                        radius_of_operation REAL,
                        area_of_operation_code TEXT,
                        clearance_indicator TEXT,
                        ground_elevation REAL,
                        lat_degrees INTEGER,
                        lat_minutes INTEGER,
                        lat_seconds REAL,
                        lat_direction TEXT,
                        long_degrees INTEGER,
                        long_minutes INTEGER,
                        long_seconds REAL,
                        long_direction TEXT,
                        max_lat_degrees INTEGER,
                        max_lat_minutes INTEGER,
                        max_lat_seconds REAL,
                        max_lat_direction TEXT,
                        max_long_degrees INTEGER,
                        max_long_minutes INTEGER,
                        max_long_seconds REAL,
                        max_long_direction TEXT,
                        nepa TEXT,
                        quiet_zone_notification_date TEXT,
                        tower_registration_number TEXT,
                        height_of_support_structure REAL,
                        overall_height_of_structure REAL,
                        structure_type TEXT,
                        airport_id TEXT,
                        location_name TEXT,
                        units_hand_held TEXT,
                        units_mobile TEXT,
                        units_temp_fixed TEXT,
                        units_aircraft TEXT,
                        units_itinerant TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        earth_station_agreement TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier),
                        UNIQUE(unique_system_identifier, location_number)
                    )
                ''')
                
                # Create antenna table for antenna specifications
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS antennas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        antenna_action_performed TEXT,
                        antenna_number INTEGER,
                        location_number INTEGER,
                        receiver_number INTEGER,
                        antenna_type_code TEXT,
                        height_to_tip REAL,
                        height_to_center_raat REAL,
                        antenna_make TEXT,
                        antenna_model TEXT,
                        tilt_toward REAL,
                        tilt_angle REAL,
                        polarization_code TEXT,
                        beamwidth_horiz REAL,
                        beamwidth_vert REAL,
                        gain REAL,
                        azimuth REAL,
                        height_above_avg_terrain REAL,
                        diversity_height REAL,
                        diversity_gain REAL,
                        diversity_beam REAL,
                        reflector_height REAL,
                        reflector_width REAL,
                        reflector_separation REAL,
                        repeater_height REAL,
                        repeater_width REAL,
                        repeater_separation REAL,
                        commanded_azimuth REAL,
                        commanded_elevation REAL,
                        twist REAL,
                        settle_time REAL,
                        comment_text TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier),
                        UNIQUE(unique_system_identifier, antenna_number, location_number)
                    )
                ''')
                
                # Create application purpose table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS application_purpose (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        purpose_code TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier),
                        UNIQUE(unique_system_identifier, purpose_code)
                    )
                ''')
                
                # Create unique indexes for INSERT OR REPLACE to work properly
                try:
                    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_entities_unique ON entities(unique_system_identifier)')
                    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_frequencies_unique ON frequencies(unique_system_identifier, frequency_number, frequency_seq_id)')
                    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_locations_unique ON locations(unique_system_identifier, location_number)')
                    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_antennas_unique ON antennas(unique_system_identifier, antenna_number, location_number)')
                    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_application_purpose_unique ON application_purpose(unique_system_identifier, purpose_code)')
                except sqlite3.Error as e:
                    logger.warning(f"Error creating unique indexes: {e}")
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def download_file(self, url: str, filename: str, retry_count: int = 3) -> Optional[Path]:
        """Download a file from the given URL with retry logic."""
        file_path = Path(self.download_dir) / filename
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt * 60  # Exponential backoff: 2, 4, 8 minutes
                    logger.info(f"Waiting {wait_time} seconds before retry attempt {attempt + 1}")
                    time.sleep(wait_time)
                
                logger.info(f"Downloading {filename} from {url} (attempt {attempt + 1}/{retry_count})")
                
                # Use FCC-compatible session
                session = self._create_fcc_session()
                
                response = session.get(url, stream=True, timeout=300)
                
                # Check for FCC error messages
                if response.status_code == 200:
                    # Check if response contains FCC error message
                    if response.headers.get('content-type', '').startswith('text/html'):
                        # Read first chunk to check for error messages
                        first_chunk = response.raw.read(1024)
                        response.raw._fp.fp._sock.recv = lambda x: first_chunk + response.raw._fp.fp._sock.recv(x)
                        
                        if b"unexpected error occurred" in first_chunk.lower() or b"please check back later" in first_chunk.lower():
                            raise requests.RequestException("FCC server returned error page")
                
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                
                with open(file_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                
                # Verify file was downloaded properly
                if file_path.exists() and file_path.stat().st_size > 0:
                    logger.info(f"Downloaded {filename} successfully ({file_path.stat().st_size} bytes)")
                    return file_path
                else:
                    raise Exception("Downloaded file is empty or missing")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {filename}: {e}")
                if "unexpected error occurred" in str(e).lower():
                    logger.warning("FCC server is experiencing issues - will retry with longer delay")
                if attempt == retry_count - 1:
                    logger.error(f"All {retry_count} download attempts failed for {filename}")
                    return None
            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {filename}: {e}")
                if attempt == retry_count - 1:
                    logger.error(f"All {retry_count} download attempts failed for {filename}")
                    return None
        
        return None
    
    def extract_zip_file(self, zip_path: Path) -> Optional[Path]:
        """Extract ZIP file and return the extraction directory."""
        extract_dir = self.download_dir / f"extracted_{zip_path.stem}"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Extracted {zip_path} to {extract_dir}")
            return extract_dir
            
        except Exception as e:
            logger.error(f"Error extracting {zip_path}: {e}")
            return None
    
    def process_csv_file(self, csv_path: Path, table_name: str) -> int:
        """Process a CSV file and insert data into the database."""
        records_processed = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
                reader = csv.reader(csvfile, delimiter='|')
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    if table_name == 'licenses':
                        # Process license data (LM.dat or HD.dat)
                        # Determine if this is license data or application data based on file path
                        is_license_data = 'licenses' in str(csv_path).lower()
                        
                        for row in reader:
                            if len(row) >= 59:  # Basic validation - need 59 fields (including record type)
                                try:
                                    unique_system_identifier = row[1]
                                    grant_date = row[7] if len(row) > 7 else None
                                    expired_date = row[8] if len(row) > 8 else None
                                    
                                    # Determine data quality and decide whether to process
                                    should_process = True
                                    
                                    if not is_license_data:
                                        # For application data, check if we already have better license data
                                        cursor.execute('''
                                            SELECT license_status, grant_date, expired_date FROM licenses 
                                            WHERE unique_system_identifier = ?
                                        ''', (unique_system_identifier,))
                                        existing = cursor.fetchone()
                                        
                                        if existing:
                                            existing_status, existing_grant, existing_expired = existing
                                            
                                            # If existing record is a granted license with dates, prefer it over application
                                            if (existing_status and existing_status.upper() in ['ACTIVE', 'GRANTED', 'LICENSED'] and
                                                existing_grant and existing_grant.strip() and
                                                existing_expired and existing_expired.strip()):
                                                # Only skip if application has no dates or is clearly inferior
                                                if (not grant_date or not grant_date.strip()) and (not expired_date or not expired_date.strip()):
                                                    should_process = False
                                    
                                    if should_process:
                                        # Skip the first field (record type "HD") and use the next 58 fields
                                        cursor.execute('''
                                            INSERT OR REPLACE INTO licenses (
                                                unique_system_identifier, uls_file_number, ebf_number,
                                                call_sign, license_status, radio_service_type,
                                                grant_date, expired_date, cancellation_date,
                                                eligibility_rule_num, applicant_type_code, alien,
                                                alien_government, alien_corporation, alien_officer,
                                                alien_control, revoked, convicted, adjudged,
                                                involved_reserved, common_carrier, non_common_carrier,
                                            private_comm, fixed, mobile, radiolocation,
                                            satellite, developmental_or_sta, interconnected_service,
                                            certifier_first_name, certifier_mi, certifier_last_name,
                                            certifier_suffix, certifier_title, gender,
                                            african_american, native_american, hawaiian,
                                            asian, white, ethnicity, effective_date,
                                            last_action_date, auction_id, reg_stat_broad_serv,
                                            band_manager, type_serv_broad_serv, alien_ruling,
                                            licensee_name_change, whitespace_ind, additional_cert_choice,
                                            additional_cert_answer, discontinuation_ind,
                                            regulatory_compliance_ind, eligibility_cert_900,
                                            transition_plan_cert_900, return_spectrum_cert_900,
                                            payment_cert_900
                                        ) VALUES (''' + ','.join(['?'] * 58) + ')', row[1:59])
                                        records_processed += 1
                                except sqlite3.Error as e:
                                    logger.warning(f"Error inserting license record: {e}")
                    
                    elif table_name == 'entities':
                        # Process entity data (EN.dat)
                        for row in reader:
                            if len(row) >= 30:  # Basic validation - need 30 fields (including record type)
                                try:
                                    # Skip records with empty call signs to avoid overwriting valid license entities
                                    call_sign = row[4].strip() if len(row) > 4 else ''
                                    if not call_sign:
                                        continue
                                    
                                    # Check if this record would overwrite an existing license entity with a different call sign
                                    unique_system_identifier = row[1].strip() if len(row) > 1 else ''
                                    if unique_system_identifier:
                                        cursor.execute('SELECT call_sign FROM entities WHERE unique_system_identifier = ?', (unique_system_identifier,))
                                        existing = cursor.fetchone()
                                        if existing and existing[0] and existing[0] != call_sign:
                                            # Skip this record to preserve the existing license entity
                                            continue
                                    
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO entities (
                                            unique_system_identifier, uls_file_number, ebf_number,
                                            call_sign, entity_type, licensee_id, entity_name,
                                            first_name, mi, last_name, suffix, phone,
                                            fax, email, street_address, city, state,
                                            zip_code, po_box, attention_line, sgin,
                                            frn, applicant_type_code, applicant_type_other,
                                            status_code, status_date, lic_category_code,
                                            linked_license_id, linked_callsign
                                        ) VALUES (''' + ','.join(['?'] * 29) + ')', row[1:30])  # Skip first field (record type 'EN')
                                    records_processed += 1
                                except sqlite3.Error as e:
                                    logger.warning(f"Error inserting entity record: {e}")
                    
                    elif table_name == 'frequencies':
                        # Process frequency data (FR.dat)
                        # Determine if this is license data or application data based on file path
                        is_license_data = 'licenses' in str(csv_path).lower()
                        
                        def safe_float(value):
                            try:
                                return float(value) if value and value.strip() else None
                            except ValueError:
                                return None
                        
                        def safe_int(value):
                            try:
                                return int(value) if value and value.strip() else None
                            except ValueError:
                                return None
                        
                        def safe_str(value):
                            return value.strip() if value and value.strip() else None
                        
                        for row in reader:
                            if len(row) >= 18:  # Basic validation - need 18 fields (including record type)
                                try:
                                    # Map fields based on data source
                                    if is_license_data:
                                        # Licenses FR.dat structure:
                                        # 0:FR, 1:unique_sys_id, 2:uls_file_num, 3:ebf_num, 4:call_sign, 
                                        # 5:status_code, 6:freq_num, 7:freq_seq_id, 8:emission, 9:empty,
                                        # 10:frequency_assigned, 11-14:empty, 15:power_output, 16:power_erp
                                        
                                        processed_data = [
                                            safe_str(row[1]),   # unique_system_identifier
                                            safe_str(row[2]),   # uls_file_number 
                                            safe_str(row[3]),   # ebf_number
                                            safe_str(row[4]),   # call_sign
                                            safe_float(row[10]), # frequency_assigned
                                            None,               # frequency_upper_band
                                            None,               # frequency_carrier  
                                            None,               # frequency_offset
                                            safe_str(row[8]),   # emission_designator
                                            safe_float(row[15]) if len(row) > 15 else None, # power_output
                                            safe_float(row[16]) if len(row) > 16 else None, # power_erp
                                            None,               # tolerance
                                            safe_int(row[6]),   # frequency_number
                                            safe_int(row[7]),   # frequency_seq_id
                                            safe_str(row[5]),   # status_code
                                            safe_str(row[17]) if len(row) > 17 else None   # status_date
                                        ]
                                    else:
                                        # Applications FR.dat structure:
                                        # 0:FR, 1:unique_sys_id, 2:application_id?, 3:empty, 4:application_type?, 
                                        # 5:freq_num?, 6:freq_seq_id?, 7:emission?, 8:empty, 9:frequency_assigned?
                                        # Note: Applications data may not have call_sign, so we'll set it to None
                                        
                                        processed_data = [
                                            safe_str(row[1]),   # unique_system_identifier
                                            None,               # uls_file_number (not available)
                                            safe_str(row[2]),   # ebf_number (using application_id)
                                            None,               # call_sign (not available in applications)
                                            safe_float(row[10]) if len(row) > 10 else None, # frequency_assigned
                                            None,               # frequency_upper_band
                                            None,               # frequency_carrier  
                                            None,               # frequency_offset
                                            safe_str(row[8]) if len(row) > 8 else None, # emission_designator
                                            None,               # power_output (not in same position)
                                            None,               # power_erp (not in same position)
                                            None,               # tolerance
                                            safe_int(row[6]) if len(row) > 6 else None, # frequency_number
                                            safe_int(row[7]) if len(row) > 7 else None, # frequency_seq_id
                                            None,               # status_code
                                            None                # status_date
                                        ]
                                    
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO frequencies (
                                            unique_system_identifier, uls_file_number, ebf_number,
                                            call_sign, frequency_assigned, frequency_upper_band,
                                            frequency_carrier, frequency_offset, emission_designator,
                                            power_output, power_erp, tolerance, frequency_number,
                                            frequency_seq_id, status_code, status_date
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', processed_data)
                                    records_processed += 1
                                except sqlite3.Error as e:
                                    logger.warning(f"Error inserting frequency record: {e}")
                    
                    elif table_name == 'locations':
                        # Process location data (LO.dat)
                        for row in reader:
                            if len(row) >= 51:  # Basic validation - need 51 fields (including record type)
                                try:
                                    # Convert numeric fields for coordinates and elevations
                                    # Field positions (0-based after skipping LO):
                                    # 8: location_number (int), 10: corresponding_fixed_location (int)
                                    # 15: radius_of_operation (float), 17: ground_elevation (float)
                                    # 18: lat_degrees (int), 19: lat_minutes (int), 20: lat_seconds (float), 21: lat_direction (text)
                                    # 22: long_degrees (int), 23: long_minutes (int), 24: long_seconds (float), 25: long_direction (text)
                                    # 26-33: max coordinates, 37-38: structure heights (float)
                                    processed_row = []
                                    for i, value in enumerate(row[1:51]):  # Skip first field (record type "LO")
                                        # Integer fields: location_number, corresponding_fixed_location, lat_degrees, lat_minutes, long_degrees, long_minutes, max coordinates
                                        if i in [8, 10, 18, 19, 22, 23, 26, 27, 30, 31]:  
                                            try:
                                                processed_row.append(int(value) if value.strip() else None)
                                            except ValueError:
                                                processed_row.append(None)
                                        # Float fields: radius_of_operation, ground_elevation, lat_seconds, long_seconds, max_seconds, structure heights
                                        elif i in [15, 17, 20, 24, 28, 32, 37, 38]:  
                                            try:
                                                processed_row.append(float(value) if value.strip() else None)
                                            except ValueError:
                                                processed_row.append(None)
                                        # Text fields (including direction fields at positions 21, 25, 29, 33)
                                        else:
                                            processed_row.append(value if value.strip() else None)
                                    
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO locations (
                                            unique_system_identifier, uls_file_number, ebf_number, call_sign,
                                            location_action_performed, location_type_code, location_class_code,
                                            location_number, site_status, corresponding_fixed_location,
                                            location_address, location_city, location_county, location_state,
                                            radius_of_operation, area_of_operation_code, clearance_indicator,
                                            ground_elevation, lat_degrees, lat_minutes, lat_seconds, lat_direction,
                                            long_degrees, long_minutes, long_seconds, long_direction,
                                            max_lat_degrees, max_lat_minutes, max_lat_seconds, max_lat_direction,
                                            max_long_degrees, max_long_minutes, max_long_seconds, max_long_direction,
                                            nepa, quiet_zone_notification_date, tower_registration_number,
                                            height_of_support_structure, overall_height_of_structure, structure_type,
                                            airport_id, location_name, units_hand_held, units_mobile,
                                            units_temp_fixed, units_aircraft, units_itinerant, status_code, status_date,
                                            earth_station_agreement
                                        ) VALUES (''' + ','.join(['?'] * 50) + ')', processed_row[:50])
                                    records_processed += 1
                                except sqlite3.Error as e:
                                    logger.warning(f"Error inserting location record: {e}")
                    
                    elif table_name == 'antennas':
                        # Process antenna data (AN.dat)
                        for row in reader:
                            if len(row) >= 38:  # Basic validation - need 38 fields (including record type)
                                try:
                                    # Convert numeric fields
                                    numeric_fields = list(range(11, 35))  # Most antenna measurements are numeric
                                    processed_row = []
                                    for i, value in enumerate(row[1:38]):  # Skip first field (record type "AN")
                                        if i in numeric_fields:
                                            try:
                                                processed_row.append(float(value) if value.strip() else None)
                                            except ValueError:
                                                processed_row.append(None)
                                        elif i in [6, 7, 8]:  # integer fields
                                            try:
                                                processed_row.append(int(value) if value.strip() else None)
                                            except ValueError:
                                                processed_row.append(None)
                                        else:
                                            processed_row.append(value if value.strip() else None)
                                    
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO antennas (
                                            unique_system_identifier, uls_file_number, ebf_number, call_sign,
                                            antenna_action_performed, antenna_number, location_number, receiver_number,
                                            antenna_type_code, height_to_tip, height_to_center_raat, antenna_make,
                                            antenna_model, tilt_toward, tilt_angle, polarization_code,
                                            beamwidth_horiz, beamwidth_vert, gain, azimuth, height_above_avg_terrain,
                                            diversity_height, diversity_gain, diversity_beam, reflector_height,
                                            reflector_width, reflector_separation, repeater_height, repeater_width,
                                            repeater_separation, commanded_azimuth, commanded_elevation, twist,
                                            settle_time, comment_text, status_code, status_date
                                        ) VALUES (''' + ','.join(['?'] * 37) + ')', processed_row[:37])
                                    records_processed += 1
                                except sqlite3.Error as e:
                                    logger.warning(f"Error inserting antenna record: {e}")
                    
                    elif table_name == 'application_purpose':
                        # Process application purpose data (AP.dat)
                        for row in reader:
                            if len(row) >= 8:  # Basic validation - need 8 fields (including record type)
                                try:
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO application_purpose (
                                            unique_system_identifier, uls_file_number, ebf_number,
                                            call_sign, purpose_code, status_code, status_date
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                                    ''', row[1:8])  # Skip first field (record type)
                                    records_processed += 1
                                except sqlite3.Error as e:
                                    logger.warning(f"Error inserting application purpose record: {e}")
                    
                    conn.commit()
            
            logger.info(f"Processed {records_processed} records from {csv_path}")
            return records_processed
            
        except Exception as e:
            logger.error(f"Error processing CSV file {csv_path}: {e}")
            return 0
    
    def download_and_process(self) -> bool:
        """Download and process all FCC ULS files using curl."""
        success = True
        total_records = 0
        
        try:
            logger.info("Starting download using curl (reliable method)...")
            
            # Download Land Mobile licenses using curl
            lm_licenses_zip = self.download_file_with_curl(
                self.file_urls["LM_PRIVATE_LICENSES"],
                f"LM_licenses_{datetime.now().strftime('%Y%m%d')}.zip"
            )
            
            if lm_licenses_zip:
                extract_dir = self.extract_zip_file(lm_licenses_zip)
                if extract_dir:
                    # Process all .dat files
                    file_mappings = {
                        'HD': 'licenses',  # Header Data - main license information
                        'EN': 'entities',
                        'FR': 'frequencies',
                        'LO': 'locations',
                        'AN': 'antennas',
                        'AP': 'application_purpose'
                    }
                    
                    for dat_file in extract_dir.glob("*.dat"):
                        file_prefix = dat_file.name.upper()[:2]
                        if file_prefix in file_mappings:
                            table_name = file_mappings[file_prefix]
                            records = self.process_csv_file(dat_file, table_name)
                            total_records += records
                            logger.info(f"Processed {records} records from {dat_file.name} into {table_name} table")
            
            # Download Land Mobile applications using curl
            lm_apps_zip = self.download_file_with_curl(
                self.file_urls["LM_PRIVATE_APPLICATIONS"],
                f"LM_applications_{datetime.now().strftime('%Y%m%d')}.zip"
            )
            
            if lm_apps_zip:
                extract_dir = self.extract_zip_file(lm_apps_zip)
                if extract_dir:
                    # Process all .dat files
                    file_mappings = {
                        'HD': 'licenses',  # Header Data - main license information
                        'EN': 'entities',
                        'FR': 'frequencies',
                        'LO': 'locations',
                        'AN': 'antennas',
                        'AP': 'application_purpose'
                    }
                    
                    for dat_file in extract_dir.glob("*.dat"):
                        file_prefix = dat_file.name.upper()[:2]
                        if file_prefix in file_mappings:
                            table_name = file_mappings[file_prefix]
                            records = self.process_csv_file(dat_file, table_name)
                            total_records += records
                            logger.info(f"Processed {records} records from {dat_file.name} into {table_name} table")
            
            # Check if we got any data
            if total_records == 0 and (lm_licenses_zip or lm_apps_zip):
                logger.warning("Downloads completed but no records were processed. This may indicate a file format change.")
            
            # Record download history
            file_size = 0
            if lm_licenses_zip:
                file_size += lm_licenses_zip.stat().st_size
            if lm_apps_zip:
                file_size += lm_apps_zip.stat().st_size
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO download_history 
                    (file_type, file_size, records_processed, success, error_message)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('LM', file_size, total_records, success, None))
                conn.commit()
            
            logger.info(f"Download and processing completed. Total records: {total_records}")
            
        except Exception as e:
            success = False
            error_msg = str(e)
            logger.error(f"Error in download_and_process: {error_msg}")
            
            # Record failed download
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO download_history 
                    (file_type, records_processed, success, error_message)
                    VALUES (?, ?, ?, ?)
                ''', ('LM', 0, success, error_msg))
                conn.commit()
        
        return success
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM licenses")
                license_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM entities")
                entity_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM frequencies")
                frequency_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM locations")
                location_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM antennas")
                antenna_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM application_purpose")
                purpose_count = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT download_date, records_processed, success 
                    FROM download_history 
                    ORDER BY download_date DESC 
                    LIMIT 1
                """)
                last_download = cursor.fetchone()
                
                return {
                    'license_count': license_count,
                    'entity_count': entity_count,
                    'frequency_count': frequency_count,
                    'location_count': location_count,
                    'antenna_count': antenna_count,
                    'purpose_count': purpose_count,
                    'last_download': last_download[0] if last_download else None,
                    'last_records_processed': last_download[1] if last_download else 0,
                    'last_download_success': last_download[2] if last_download else None
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

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



def daily_download():
    """Function to be called by the scheduler."""
    logger.info("Starting scheduled daily download")
    downloader = FCCULSDownloader()
    success = downloader.download_and_process()
    
    if success:
        stats = downloader.get_stats()
        logger.info(f"Daily download completed successfully. Stats: {stats}")
    else:
        logger.error("Daily download failed")


def main():
    """Main function - can be run directly or scheduled."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FCC ULS Land Mobile Database Downloader")
    parser.add_argument("--schedule", action="store_true", 
                       help="Run as scheduled service (daily at 2 AM)")
    parser.add_argument("--download-now", action="store_true",
                       help="Download and process data immediately")
    parser.add_argument("--skip-download", action="store_true",
                       help="Process existing downloaded files without downloading new ones")
    parser.add_argument("--stats", action="store_true",
                       help="Show database statistics")
    parser.add_argument("--dataset-info", action="store_true",
                       help="Show FCC dataset information (sizes, last modified)")
    
    args = parser.parse_args()
    
    downloader = FCCULSDownloader()
    
    if args.dataset_info:
        dataset_info = downloader.get_dataset_info()
        print("\n=== FCC Dataset Information ===")
        if dataset_info:
            for name, info in dataset_info.items():
                print(f"\n{name}:")
                print(f"  Size: {info['size_mb']:.1f} MB")
                print(f"  Last Modified: {info['last_modified']}")
                print(f"  URL: {info['url']}")
        else:
            print("Could not retrieve dataset information")
    
    elif args.stats:
        stats = downloader.get_stats()
        print("\n=== FCC ULS Database Statistics ===")
        print(f"Total Licenses: {stats.get('license_count', 0):,}")
        print(f"Total Entities: {stats.get('entity_count', 0):,}")
        print(f"Total Frequencies: {stats.get('frequency_count', 0):,}")
        print(f"Total Locations: {stats.get('location_count', 0):,}")
        print(f"Total Antennas: {stats.get('antenna_count', 0):,}")
        print(f"Total Application Purposes: {stats.get('purpose_count', 0):,}")
        print(f"Last Download: {stats.get('last_download', 'Never')}")
        print(f"Last Records Processed: {stats.get('last_records_processed', 0):,}")
        print(f"Last Download Success: {stats.get('last_download_success', 'Unknown')}")
        
    elif args.skip_download:
        logger.info("Processing existing downloaded files without downloading")
        print("\n🔄 Processing existing downloaded files...")
        
        # Find existing downloaded files
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            print("❌ No downloads directory found. Run --download-now first.")
            return
        
        # Look for extracted directories
        extract_dirs = list(downloads_dir.glob("extracted_*"))
        if not extract_dirs:
            print("❌ No extracted files found. Run --download-now first.")
            return
        
        print(f"📁 Found {len(extract_dirs)} extracted directories")
        
        total_records = 0
        
        # Process all extracted directories
        for extract_dir in extract_dirs:
            print(f"📂 Processing {extract_dir.name}...")
            
            file_mappings = {
                'HD': 'licenses',
                'EN': 'entities', 
                'FR': 'frequencies',
                'LO': 'locations',
                'AN': 'antennas',
                'AP': 'application_purpose'
            }
            
            for dat_file in extract_dir.glob("*.dat"):
                file_prefix = dat_file.name.upper()[:2]
                if file_prefix in file_mappings:
                    table_name = file_mappings[file_prefix]
                    records = downloader.process_csv_file(dat_file, table_name)
                    total_records += records
                    logger.info(f"Processed {records} records from {dat_file.name} into {table_name} table")
        
        print(f"✅ Processing completed! Processed {total_records:,} records.")
        print(f"💾 Database ready at: {downloader.db_path}")
        
    elif args.download_now:
        logger.info("Starting immediate download")
        print("\n🚀 Starting automatic download using curl (reliable method)...")
        print("📦 This will download ~1GB of FCC data and may take 5-15 minutes.")
        print("💡 If needed, you can still use manual download: uv run python manual_download_helper.py")
        print("\nDownloading...\n")
        
        success = downloader.download_and_process()
        if success:
            stats = downloader.get_stats()
            print(f"✅ Download completed successfully! Processed {stats.get('last_records_processed', 0):,} records.")
            print(f"💾 Database ready at: {downloader.db_path}")
        else:
            print("❌ Download failed. Check logs for details.")
            print("\n💡 Fallback: Use manual download method:")
            print("   uv run python manual_download_helper.py")
            
    elif args.schedule:
        logger.info("Starting scheduled service - will download daily at 2:00 AM")
        schedule.every().day.at("02:00").do(daily_download)
        
        print("FCC ULS Downloader scheduled to run daily at 2:00 AM")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            print("Scheduler stopped.")
    
    else:
        print("No action specified. Use --help for options.")
        print("Available options:")
        print("  --download-now  : Download and process data immediately")
        print("  --skip-download : Process existing downloaded files without downloading new ones")
        print("  --stats         : Show database statistics")
        print("  --dataset-info  : Show FCC dataset information")
        print("  --schedule      : Run as scheduled service (daily at 2 AM)")


if __name__ == "__main__":
    main()
