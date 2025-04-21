import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project structure
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    directory.mkdir(exist_ok=True)

# Scraping configurations
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 30  # seconds
RETRY_COUNT = 3
RESPECT_ROBOTS_TXT = True

# Rate limiting
REQUESTS_PER_MINUTE = 20
DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE  # seconds

# Database settings
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", f"sqlite:///{BASE_DIR}/data/scraped_data.db")

# API keys (if needed)
API_KEY = os.getenv("API_KEY", "")

# Proxy settings
USE_PROXY = os.getenv("USE_PROXY", "False").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")