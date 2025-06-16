import json
from datetime import datetime

# Beispiel-Daten
event_data = {
    "event_type": "user_data_event",
    "metadata": {
        "ip_address": "192.168.1.10",
        "user_agent": "Mozilla/5.0",
        "location": {
            "country": "Germany",
            "city": "Berlin"
        }
    },
    "payload": {
        "instagram": {
            "username": "insta_user123",
            "followers": 1240,
            "following": 530,
            "posts": 87,
            "last_post": "2025-06-08T14:32:00"
        },
        "health": {
            "steps_today": 8543,
            "heart_rate_avg": 72,
            "sleep_hours": 6.5,
            "calories_burned": 540
        },
        "steam": {
            "steam_id": "76561198000000000",
            "total_playtime_hours": 1280,
            "most_played_game": "Counter-Strike 2",
            "achievements": {
                "global": 430,
                "last_unlocked": "2025-06-08T20:15:00"
            }
        },
        "spotify": {
            "username": "musiclover88",
            "recent_tracks": [
                {"title": "Blinding Lights", "artist": "The Weeknd", "played_at": "2025-06-08T23:10:00"},
                {"title": "Levitating", "artist": "Dua Lipa", "played_at": "2025-06-08T22:55:00"}
            ],
            "top_genre": "Pop",
            "minutes_listened_this_week": 430
        },
        "timestamp": str(datetime.now())
    },
    "status": "synced"
}

# Speichern ohne with
f = open("data/event_data.json", "w", encoding="utf-8")
f.write(json.dumps(event_data, indent=4, ensure_ascii=False))
f.close()
