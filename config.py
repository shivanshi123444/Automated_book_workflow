    # src/config.py
import os
from dotenv import load_dotenv

    # While .env is loaded, no API keys are expected for this free version.
load_dotenv()

    

    # Paths
RAW_CONTENT_DIR = "data/raw_content"
PROCESSED_CHAPTERS_DIR = "data/processed_chapters"
SCREENSHOTS_DIR = "data/screenshots"
CHROMADB_DATA_DIR = "data/chromadb_data"

    # Ensure directories exist (redundant if mkdir -p was used, but harmless)
for _dir in [RAW_CONTENT_DIR, PROCESSED_CHAPTERS_DIR, SCREENSHOTS_DIR, CHROMADB_DATA_DIR]:
        os.makedirs(_dir, exist_ok=True)
    