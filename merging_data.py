import os
import json

ALLOWED_PREFIXES = ['spotify', 'linkedin', 'fitbit', 'github', 'facebook', 'strava']

def extract_name_email(prefix, data):
    """Custom logic to extract name and email from nested structures"""
    if prefix == 'linkedin':
        profile = data.get('profile', {})
        first = profile.get('firstName', '')
        last = profile.get('lastName', '')
        name = f"{first} {last}".strip() if first or last else None
        email = profile.get('emailAddress')
        return name, email
    elif prefix == 'fitbit':
        profile = data.get('profile', {})
        return profile.get('name'), profile.get('email')
    # Extend for other apps if needed
    return data.get('name'), data.get('email')


def load_json_files(folder_path):
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

                    # Try to extract name and email
                    name, email = extract_name_email(prefix, data)
                    if not merged_data['name'] and name:
                        merged_data['name'] = name
                    if not merged_data['email'] and email:
                        merged_data['email'] = email

                    merged_data[prefix] = data
            except Exception as e:
                print(f"⚠️ Error processing {filename}: {e}")
    return merged_data


if __name__ == '__main__':
    folder = './user_data'
    os.makedirs(folder, exist_ok=True)  # Safe fallback
    result = load_json_files(folder)
    with open('event_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("✅ Merged output saved to 'event_data.json'")
