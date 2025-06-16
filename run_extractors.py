import sys
import os

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_extractors.spotify_extractor import extract_spotify_user_data

if __name__ == "__main__":
    print("🔄 Starting Spotify data extraction...")
    extract_spotify_user_data()
