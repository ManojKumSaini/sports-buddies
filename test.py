from jinja2 import Environment, FileSystemLoader
import os

# Setup Pfade
template_dir = "templates"
output_file = "rendered_vibe.html"

# Kontext-Daten (Dummywerte)
context = {
    "var_main_picture": "icons/active_walker.png",
    "var_name": "Alex Muster",
    "var_age": "29",
    "var_street": "Sonnenstraße 42",
    "var_city": "Berlin",

    "var_vibe_picture": "icons/active_walker.png",
    "var_text1": "entspannt",
    "var_text2": "kreativ",
    "var_text3": "nachbarschaftlich",

    "var_type1": "Freizeit",
    "var_image1": "icons/active_walker.png",
    "var_image2": "icons/active_walker.png",

    "var_musik1": "icons/active_walker.png",
    "var_sport1": "icons/active_walker.png",
    "var_sport2": "icons/active_walker.png",
    "var_sport3": "icons/active_walker.png",

    "var_sleeping": "icons/active_walker.png",
    "var_working": "icons/active_walker.png"
}

# Jinja2-Setup
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template("template.html")

# Rendern
output = template.render(context)

# Speichern
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output)

print(f"✅ Template erfolgreich gerendert als {output_file}")
