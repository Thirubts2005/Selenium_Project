# Configuration settings for IMDB scraper
import os
from datetime import datetime

# Base URLs
IMDB_BASE_URL = "https://www.imdb.com"
IMDB_SEARCH_URL = "https://www.imdb.com/search/title/"

# Headers for requests
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

# File paths
OUTPUT_DIR = "output"
IMAGES_DIR = "images"
LOGS_DIR = "logs"

# Create directories if they don't exist
for directory in [OUTPUT_DIR, IMAGES_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Excel file settings
EXCEL_FILE = os.path.join(OUTPUT_DIR, f"movies_2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
CSV_FILE = os.path.join(OUTPUT_DIR, f"movies_2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
LOG_FILE = os.path.join(LOGS_DIR, "scraper.log")

# Scraping settings
MAX_RETRIES = 3
REQUEST_TIMEOUT = 15  # Increased timeout
PAGE_DELAY = 2  # Increased delay
MAX_PAGES = 20  # Reduced pages for testing

# Movie details to extract
MOVIE_FIELDS = [
    "title",
    "year",
    "rating",
    "genres",
    "directors",
    "cast",
    "runtime",
    "plot",
    "imdb_id",
    "poster_url",
    "release_date"
]