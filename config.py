"""
Configuration settings for FCC ULS Downloader
"""

import os
from pathlib import Path

# Base directory for the application
BASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_PATH = BASE_DIR / "fcc_uls.db"

# Download configuration
DOWNLOAD_DIR = BASE_DIR / "downloads"
KEEP_DOWNLOADS = True  # Keep downloaded files after processing
MAX_DOWNLOAD_AGE_DAYS = 30  # Delete downloads older than this

# FCC ULS URLs
FCC_URLS = {
    "LM": "https://wireless2.fcc.gov/UlsApp/UlsSearch/downloadZipFile?serviceType=LM",  # Land Mobile
    "EN": "https://wireless2.fcc.gov/UlsApp/UlsSearch/downloadZipFile?serviceType=EN",  # Entity
}

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "fcc_uls_downloader.log"
MAX_LOG_SIZE_MB = 50
LOG_BACKUP_COUNT = 5

# Schedule configuration
DOWNLOAD_TIME = "02:00"  # Daily download time (24-hour format)
RETRY_ATTEMPTS = 3
RETRY_DELAY_MINUTES = 30

# Database cleanup
ENABLE_CLEANUP = True
CLEANUP_OLDER_THAN_DAYS = 365  # Remove records older than this

# File cleanup configuration
ENABLE_FILE_CLEANUP = True
FILE_CLEANUP_DAYS = 7  # Remove downloaded files older than this many days
CLEANUP_ON_SUCCESS = True  # Automatically cleanup after successful downloads
