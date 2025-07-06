from jinja2 import Environment, FileSystemLoader

# --- Define the vibe explanations mapping ---
vibe_to_hoods_explained = {
    "Party Explorer": {
        "hoods": ["Friedrichshain", "Neukölln", "Mitte"],
        "explanation": [
            "Friedrichshain is the natural habitat for the Party Explorer. With its pulsing nightlife, iconic clubs like Berghain, and raw street energy, it's the epicenter for dance, late nights, and youth culture.",
            "Neukölln offers a grittier, underground party vibe — from smoky bars to rooftops and hidden raves, it's where creative chaos meets beats.",
            "Mitte adds a more polished scene with trendsetting bars, pop-ups, and a constant rotation of events, perfect for social explorers and night owls."
        ]
    },
    "Creative Urban Nomad": {
        "hoods": ["Kreuzberg", "Neukölln", "Moabit"],
        "explanation": [
            "Kreuzberg is Berlin's bohemian heart. Murals, indie venues, and community hubs make it ideal for artistic nomads seeking inspiration and diversity.",
            "Neukölln fits for its multiculturalism and creative grit — think pop-up galleries and late-night jam sessions in smoky cafés.",
            "Moabit is the underdog artist district, still affordable and authentic, with hidden ateliers and a rising scene of makers, thinkers, and DIY dreamers."
        ]
    },
    "Efficiency Minimalist": {
        "hoods": ["Charlottenburg", "Prenzlauer Berg", "Steglitz"],
        "explanation": [
            "Charlottenburg blends order, culture, and stability — perfect for early risers and productivity fans. Its clean streets, wide sidewalks, and calm tempo match the minimalist vibe.",
            "Prenzlauer Berg has a health-conscious, organized feel — yoga at 6, green juice at 8, and off to coworking. A haven for structured creatives and routine lovers.",
            "Steglitz is residential, tidy, and well-connected. Ideal for those who prefer balance, clear routines, and no unnecessary distractions."
        ]
    },
    "Slow Living Spirit": {
        "hoods": ["Zehlendorf", "Köpenick", "Wilmersdorf"],
        "explanation": [
            "Zehlendorf offers leafy lanes, lakeside walks, and serenity. A place to breathe, meditate, and enjoy a slower pace of life.",
            "Köpenick, with its rivers, woods, and Altstadt, is a natural retreat from city pressure — ideal for calm, nature-connected souls.",
            "Wilmersdorf is graceful and residential. Quiet cafés, classic architecture, and relaxed tempo make it perfect for slow thinkers and readers."
        ]
    },
    "Digital Couch Potato": {
        "hoods": ["Lichtenberg", "Marzahn", "Spandau"],
        "explanation": [
            "Lichtenberg is practical and quiet — a no-frills zone where rent is low and the internet is fast. Ideal for gamers and streamers.",
            "Marzahn offers space, stability, and isolation — high-rise blocks perfect for introverts and long gaming sessions.",
            "Spandau is suburban but not sleepy — a laid-back zone for those who love peace, delivery food, and no FOMO."
        ]
    },
    "Balanced Berliner": {
        "hoods": ["Schöneberg", "Tempelhof", "Mitte"],
        "explanation": [
            "Schöneberg blends charm, diversity, and balance — lively but never overwhelming. Queer-friendly, leafy, and cultured.",
            "Tempelhof offers calm and connection — it’s centered, spacious, and socially mixed. Perfect for those who like harmony over hype.",
            "Mitte, again, appears here for its centrality — giving a little of everything without too much of anything."
        ]
    },
    "Mindful Creative": {
        "hoods": ["Wedding", "Weißensee", "Pankow"],
        "explanation": [
            "Wedding is raw, spiritual, and poetic. Old-school Berlin with yoga lofts and activist cafés hidden behind brutalist facades.",
            "Weißensee is peaceful and lakeside — ideal for reflection, journaling, and conscious living.",
            "Pankow blends calm residential energy with intellectual curiosity — think plant-based bistros and piano lessons."
        ]
    },
    "Streetwise Hustler": {
        "hoods": ["Neukölln", "Wedding", "Kreuzberg"],
        "explanation": [
            "Neukölln offers grit, hustle, and survival instinct. Ideal for side-hustlers, underground creatives, and self-made personalities.",
            "Wedding is where the street is the teacher — raw, real, and full of energy. Perfect for doers and grinders.",
            "Kreuzberg ties hustle with vision. Activism meets street smarts in a district that never sleeps and never settles."
        ]
    }
}

# Example top vibe to get the explanations from
top_vibe = "Balanced Berliner"
hoods = vibe_to_hoods_explained[top_vibe]["hoods"]
explanations = vibe_to_hoods_explained[top_vibe]["explanation"]
hood_explanations = list(zip(hoods, explanations))

# === Prepare the context ===
context = {
    "var_name": "Alex Berg",
    "var_age": 29,
    "var_street": "Urbanstraße 52",
    "var_city": "Berlin",
    "var_main_picture": "icons/user_alex.png",
    "var_vibe_picture": "icons/neighborhood_vibe_balanced_berliner.png",
    "top_vibe": top_vibe,
    "var_text1": "Balanced",
    "var_text2": "Curious",
    "var_text3": "Connected",
    "hood_explanations": hood_explanations,
    "genre_1": "icons/jazz.png",
    "genre_2": "icons/indie.png",
    "genre_3": "icons/funk.png",
    "genre_label_1": "Jazz Purist",
    "genre_label_2": "Indie Explorer",
    "genre_label_3": "Funk Lover",
    "listening_1": "icons/late_night.png",
    "listening_2": "icons/weekend_breakfast.png",
    "listening_3": "icons/weekday_sundown.png",
    "listening_label_1": "Late Night",
    "listening_label_2": "Weekend Breakfast",
    "listening_label_3": "Weekday Sundown",
    "gaming_type_icon": "icons/gamer_mid.png",
    "gaming_label": "Occasional Gamer",
    "sleep_type_icon": "icons/sleep_night_owl.png",
    "sleep_label": "Night Owl",
    "work_type_icon": "icons/remote_worker.png",
    "work_label": "Remote Worker",
    "walker_type_icon": "icons/walker_sprinter.png",
    "walker_label": "Sprinter",
    "fitness_strength_icon": "icons/strength.png",
    "fitness_strength_label": "Strong",
    "fitness_flexibility_icon": "icons/flexibility.png",
    "fitness_flexibility_label": "Flexible",
    "fitness_relaxation_icon": "icons/relaxation.png",
    "fitness_relaxation_label": "Relaxed",
    "fitness_endurance_icon": "icons/endurance.png",
    "fitness_endurance_label": "Enduring",
    "scores": {
        "Balanced Berliner": 0.45,
        "Party Explorer": 0.3,
        "Mindful Creative": 0.25
    }
}

# === Render the HTML ===
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template("neighbourhood_final.html")
rendered_html = template.render(context)

# === Output to file ===
with open("Neighbourhood_output.html", "w") as f:
    f.write(rendered_html)

print("✅ HTML profile generated: output.html")