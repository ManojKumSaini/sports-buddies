import requests
import json
import os

def fetch_data(url):
    try:
        response = requests.get(url, headers={"Accept": "application/vnd.github.v3+json"})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching from {url}: {e}")
        return None

def get_github_full_profile(username):
    base_url = f"https://api.github.com/users/{username}"

    # Step 1: Get basic user info
    user_data = fetch_data(base_url)
    if not user_data:
        return

    # Step 2: Get list of public repos
    repos = fetch_data(user_data.get("repos_url", ""))
    repo_names = [repo["name"] for repo in repos] if repos else []

    # Step 3: Get starred repos count
    starred = fetch_data(f"https://api.github.com/users/{username}/starred")
    starred_count = len(starred) if starred else 0

    # Step 4: Get organizations count and names
    orgs = fetch_data(user_data.get("organizations_url", ""))
    org_names = [org["login"] for org in orgs] if orgs else []

    # Step 5: Combine everything into a custom dictionary
    profile_summary = {
        "username": user_data.get("login"),
        "name": user_data.get("name"),
        "bio": user_data.get("bio"),
        "location": user_data.get("location"),
        "company": user_data.get("company"),
        "email": user_data.get("email"),
        "twitter": user_data.get("twitter_username"),
        "public_repos": user_data.get("public_repos"),
        "repo_names": repo_names,
        "followers": user_data.get("followers"),
        "following": user_data.get("following"),
        "starred_repos_count": starred_count,
        "organizations": org_names,
        "created_at": user_data.get("created_at"),
        "updated_at": user_data.get("updated_at"),
        "hireable": user_data.get("hireable"),
        "avatar_url": user_data.get("avatar_url"),
        "html_url": user_data.get("html_url")
    }

    # Step 6: Save to user_data/ folder in the parent directory
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    filename = os.path.join(user_data_dir, f"github_profile_{username}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(profile_summary, f, indent=4)

    print(f"\n✅ Profile data saved to '{filename}'.")

if __name__ == "__main__":
    username = input("Enter GitHub username: ").strip()
    get_github_full_profile(username)
