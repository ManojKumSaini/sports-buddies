import os
import json
from datetime import datetime

def transform_to_event_data(merged_data):
    # --- Static metadata ---
    city = "Unknown"
    country = "Unknown"
    if 'github' in merged_data:
        location_str = merged_data['github'].get('location', '')
        if location_str and ',' in location_str:
            parts = [part.strip() for part in location_str.split(',')]
            if len(parts) == 2:
                city, country = parts

    metadata = {
        "ip_address": "127.0.0.1",
        "user_agent": "CustomScript/1.0",
         "location": {
            "country": country,
            "city": city
        }
    }


    payload = {}

    # Add Spotify if exists
    if 'spotify' in merged_data:
        payload['spotify'] = merged_data['spotify']

    # Add LinkedIn if exists
    if 'linkedin' in merged_data:
        payload['linkedin'] = merged_data['linkedin']

    # Add Steam if exists
    if 'steam' in merged_data:
        payload['steam'] = merged_data['steam']

    # Add Fitbit if exists (fixed typo from 'filtbit')
    if 'fitbit' in merged_data:
        payload['fitbit'] = merged_data['fitbit']

    if 'github' in merged_data:
        payload['github'] = merged_data['github']


    # Add timestamp
    payload["timestamp"] = datetime.now().isoformat()

    # Final event structure
    return {
        "event_type": "user_data_event",
        "metadata": metadata,
        "payload": payload,
        "status": "synced"
    }

def load_json_files(folder_path):
    ALLOWED_PREFIXES = ['spotify', 'linkedin', 'fitbit', 'github', 'facebook', 'strava', 'steam']
    merged_data = {'name': None, 'email': None}
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            prefix = filename.split('_')[0].lower()
            if prefix not in ALLOWED_PREFIXES:
                continue
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not merged_data['name']:
                        merged_data['name'] = data.get('name')
                    if not merged_data['email']:
                        email = data.get('email') or data.get('contact', {}).get('email')
                        if email:
                            merged_data['email'] = email
                    merged_data[prefix] = data
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return merged_data

if __name__ == '__main__':
    # Note: Assuming this script runs inside the 'source' folder,
    # so we go one directory up to access user_data and data folders
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    user_data_folder = os.path.join(root_dir, "user_data")
    output_folder = os.path.join(root_dir, "data")

    os.makedirs(output_folder, exist_ok=True)

    merged_data = load_json_files(user_data_folder)
    event_data = transform_to_event_data(merged_data)

    output_path = os.path.join(output_folder, 'event_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(event_data, f, indent=2)

    print(f"✅ Transformed event data saved to '{output_path}'")
