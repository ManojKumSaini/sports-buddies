from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
import os
from urllib.parse import urlencode
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
import json

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback")

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

SCOPES = [
    "user-read-private",
    "user-read-email",
    "playlist-read-private",
    "user-read-recently-played",
    "user-top-read",
    "user-read-playback-state",
    "user-read-currently-playing",
    "playlist-read-collaborative"
]

def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "show_dialog": "true"
    }
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"

@app.get("/")
async def root():
    return RedirectResponse("/login")

@app.get("/login")
async def login():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Missing Spotify client credentials")
    return RedirectResponse(get_auth_url())

def concise_user_profile(user_profile):
    return {
        "id": user_profile.get("id"),
        "display_name": user_profile.get("display_name"),
        "country": user_profile.get("country"),
        "product": user_profile.get("product"),
    }

def concise_artist(artist):
    return {
        "id": artist.get("id"),
        "name": artist.get("name"),
        "genres": artist.get("genres"),
        "popularity": artist.get("popularity"),
        "followers": artist.get("followers", {}).get("total"),
        "spotify_url": artist.get("external_urls", {}).get("spotify"),
    }

def concise_track(item):
    track = item["track"]
    return {
        "id": track.get("id"),
        "name": track.get("name"),
        "popularity": track.get("popularity"),
        "duration_ms": track.get("duration_ms"),
        "explicit": track.get("explicit"),
        "spotify_url": track.get("external_urls", {}).get("spotify"),
        "artists": [{"id": a.get("id"), "name": a.get("name")} for a in track.get("artists", [])],
        "album": {
            "id": track.get("album", {}).get("id"),
            "name": track.get("album", {}).get("name"),
            "release_date": track.get("album", {}).get("release_date"),
        },
        "played_at": item.get("played_at"),
    }

def concise_playlist(playlist):
    return {
        "id": playlist.get("id"),
        "name": playlist.get("name"),
        "collaborative": playlist.get("collaborative"),
        "owner": playlist.get("owner", {}).get("display_name"),
        "spotify_url": playlist.get("external_urls", {}).get("spotify"),
    }

@app.get("/callback")
async def callback(code: str = None, error: str = None):
    if error:
        raise HTTPException(status_code=400, detail=f"Spotify authorization failed: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="No code received")
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(SPOTIFY_TOKEN_URL, data=data)
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token from Spotify")
        tokens = token_resp.json()
        
        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")

        headers = {"Authorization": f"Bearer {access_token}"}

        async def fetch(endpoint):
            url = f"{SPOTIFY_API_BASE}/{endpoint}"
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None
            return resp.json()

        user_profile = await fetch("me")
        user_top_artists = await fetch("me/top/artists")
        user_recently_played = await fetch("me/player/recently-played")
        user_playlists_resp = await fetch("me/playlists")

    track_counter = defaultdict(lambda: {"track": None, "count": 0})
    if user_recently_played and "items" in user_recently_played:
        for item in user_recently_played["items"]:
            track_id = item["track"]["id"]
            track_counter[track_id]["track"] = item
            track_counter[track_id]["count"] += 1

    recently_played = []
    for track_id, data in track_counter.items():
        base = concise_track(data["track"])
        base["play_count"] = data["count"]
        recently_played.append(base)

    collaborative_playlists = []
    if user_playlists_resp and "items" in user_playlists_resp:
        for playlist in user_playlists_resp["items"]:
            if playlist.get("collaborative"):
                collaborative_playlists.append(concise_playlist(playlist))

    aggregated_data = {
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "user_profile": concise_user_profile(user_profile) if user_profile else None,
        "top_artists": [concise_artist(a) for a in user_top_artists.get("items", [])] if user_top_artists else [],
        "recently_played": recently_played,
        "collaborative_playlists": collaborative_playlists,
    }

    # Save to JSON file
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
    os.makedirs(user_data_dir, exist_ok=True)
    username = user_profile.get("display_name") or user_profile.get("id", "unknown_user")
    safe_username = "".join(c if c.isalnum() else "_" for c in username)
    file_path = os.path.join(user_data_dir, f"spotify_{safe_username}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(aggregated_data, f, ensure_ascii=False, indent=2)

    return JSONResponse(content=aggregated_data)
