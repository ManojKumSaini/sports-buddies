from flask import Flask, redirect, request, session, jsonify
import requests, urllib.parse, os, base64
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret")

CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI")

AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"

@app.route('/')
def index():
    scope = 'activity heartrate sleep profile'
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    return f'<a href="{auth_url}">Connect to Fitbit</a>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed: No code provided.'

    basic_auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    response = requests.post(
        TOKEN_URL,
        headers={
            'Authorization': f'Basic {basic_auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
        }
    )

    if response.status_code != 200:
        return f"Failed to fetch token: {response.status_code} - {response.text}"

    session['access_token'] = response.json().get('access_token')
    return redirect('/fitbit_data')

def get_fitbit_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else None

@app.route('/fitbit_data')
def fitbit_data():
    headers = get_fitbit_headers()
    if not headers:
        return redirect('/')

    result = {
        'profile': {},
        'daily_activity': {},
        'workouts': [],
        'activity_history': [],
    }

    # --- 1. Profile ---
    profile_res = requests.get("https://api.fitbit.com/1/user/-/profile.json", headers=headers)
    if profile_res.ok:
        user = profile_res.json().get('user', {})
        result['profile'] = {
            'name': user.get('fullName'),
            'email': user.get('email'),
            'age': user.get('age'),
            'gender': user.get('gender'),
            'member_since': user.get('memberSince'),
            'encoded_id': user.get('encodedId')
        }

    # --- 2. Today's Daily Activity ---
    today = datetime.now().strftime('%Y-%m-%d')
    today_url = f"https://api.fitbit.com/1/user/-/activities/date/{today}.json"
    today_res = requests.get(today_url, headers=headers)
    if today_res.ok:
        summary = today_res.json().get('summary', {})
        result['daily_activity'] = {
            'steps': summary.get('steps'),
            'calories_out': summary.get('caloriesOut'),
            'distances': summary.get('distances'),
            'sedentary_minutes': summary.get('sedentaryMinutes'),
            'lightly_active_minutes': summary.get('lightlyActiveMinutes'),
            'fairly_active_minutes': summary.get('fairlyActiveMinutes'),
            'very_active_minutes': summary.get('veryActiveMinutes'),
        }

    # --- 3. Workout History ---
    workouts_url = "https://api.fitbit.com/1/user/-/activities/list.json"
    params = {'afterDate': '2024-06-01', 'sort': 'desc', 'limit': 20, 'offset': 0}
    workouts_res = requests.get(workouts_url, headers=headers, params=params)
    if workouts_res.ok:
        activities = workouts_res.json().get('activities', [])
        result['workouts'] = [{
            'activity_name': act.get('activityName'),
            'start_time': act.get('startTime'),
            'duration_min': round(act.get('duration', 0) / 60000, 2),
            'distance_km': round(act.get('distance', 0), 2),
            'calories': act.get('calories'),
            'speed_kmph': round((act.get('distance', 0) / (act.get('duration', 1) / 3600000)), 2),
            'log_id': act.get('logId'),
        } for act in activities]

    # --- 4. Last 20 Days Activity History ---
    history = []
    for i in range(20):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        url = f"https://api.fitbit.com/1/user/-/activities/date/{date}.json"
        res = requests.get(url, headers=headers)
        if res.ok:
            summary = res.json().get('summary', {})
            history.append({
                'date': date,
                'steps': summary.get('steps'),
                'calories_out': summary.get('caloriesOut'),
                'distances': summary.get('distances'),
                'sedentary_minutes': summary.get('sedentaryMinutes'),
                'lightly_active_minutes': summary.get('lightlyActiveMinutes'),
                'fairly_active_minutes': summary.get('fairlyActiveMinutes'),
                'very_active_minutes': summary.get('veryActiveMinutes'),
            })
    result['activity_history'] = history

    # --- Save result to file ---
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    encoded_id = result['profile'].get('encoded_id', 'unknown_user')
    filename = os.path.join(user_data_dir, f"fitbit_profile_{encoded_id}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print(f"✅ Fitbit profile saved to '{filename}'")

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
