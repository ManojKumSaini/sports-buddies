from jinja2 import Environment, FileSystemLoader

# ---- Dynamic Data (you can later fetch from a DB or form) ----
context = {
    "name": "John Doe",
    "age": 27,
    "street": "Kurfürstendamm",
    "zip": "10709",
    "city": "Berlin",
    "profile_title": "chill guy",
    "profile_description": "A calm and balanced personality who enjoys slow mornings, walks in the park, and lo-fi playlists.",
    "music_types": ["tiee type", "gener type"],
    "gaming_type": "Gaming type",
    "sports_types": ["Running type", "walking type", "endurance type"],
    "sleep_type": "endurance type",
    "working_type": "endurance type",
    "suggestions": ["Prenzlauer Berg", "Kreuzberg", "Friedrichshain"]
}

# ---- Jinja2 Environment Setup ----
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("template_v3.html")

# ---- Render and Save ----
output = template.render(
    var_name=context["name"],
    var_age=context["age"],
    var_street=context["street"],
    var_zip=context["zip"],
    var_city=context["city"],
    var_profile_title=context["profile_title"],
    var_profile_description=context["profile_description"],
    var_music_1=context["music_types"][0],
    var_music_2=context["music_types"][1],
    var_gaming_type=context["gaming_type"],
    var_sport_1=context["sports_types"][0],
    var_sport_2=context["sports_types"][1],
    var_sport_3=context["sports_types"][2],
    var_sleep_type=context["sleep_type"],
    var_work_type=context["working_type"],
    var_footer_1=context["suggestions"][0],
    var_footer_2=context["suggestions"][1],
    var_footer_3=context["suggestions"][2]
)

with open("rendered_vibe.html", "w", encoding="utf-8") as f:
    f.write(output)

print("✅ Profile rendered successfully: rendered_vibe.html")