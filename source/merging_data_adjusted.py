import os
import json
from datetime import datetime

# this is the adjusted merging file to extract health data

def transform_to_event_data(merged_data):
    metadata = {
        "ip_address": "127.0.0.1",
        "user_agent": "CustomScript/1.0",
        "location": {
            "country": "Unknown",
            "city": "Unknown"
        }
    }

    payload = {}

    if 'spotify' in merged_data:
        payload['spotify'] = merged_data['spotify']
    if 'github' in merged_data:
        payload['github'] = merged_data['github']
    if 'linkedin' in merged_data:
        payload['linkedin'] = merged_data['linkedin']
    if 'steam' in merged_data:
        payload['steam'] = merged_data['steam']
    if 'health' in merged_data:
        payload['health'] = merged_data['health']

    # Only add fitbit if present (avoid typo + error)
    if 'fitbit' in merged_data:
        payload['fitbit'] = merged_data['fitbit']

    payload["timestamp"] = datetime.now().isoformat()

    return {
        "event_type": "user_data_event",
        "metadata": metadata,
        "payload": payload,
        "status": "synced"
    }

def load_json_files(folder_path):
    ALLOWED_PREFIXES = ['spotify', 'linkedin', 'fitbit', 'github', 'facebook', 'strava', 'steam', 'health']
    merged_data = {'name': None, 'email': None}
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            prefix = filename.split('_')[0].lower()
            if prefix not in ALLOWED_PREFIXES:
                continue
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                    # Store data directly
                    merged_data[prefix] = data

                    # Only extract name/email if data is a dict
                    if isinstance(data, dict):
                        if not merged_data['name']:
                            merged_data['name'] = data.get('name')
                        if not merged_data['email']:
                            email = data.get('email') or data.get('contact', {}).get('email')
                            if email:
                                merged_data['email'] = email

            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
    
    print("✅ Merged data keys:", merged_data.keys())
    return merged_data

# Main execution
if __name__ == '__main__':
    folder = './user_data'  # Path to your input JSON files
    merged_data = load_json_files(folder)
    event_data = transform_to_event_data(merged_data)

    output_folder = './data'
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, 'event_output.json')
    with open(output_path, 'w') as f:
        json.dump(event_data, f, indent=2)

    print(f"✅ Transformed event data saved to '{output_path}'")
