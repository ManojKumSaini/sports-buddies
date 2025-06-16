import fitz  # PyMuPDF
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

# === Load PDF ===
pdf_path = "Profile.pdf"  # Replace with your actual file path
doc = fitz.open(pdf_path)
pdf_text = "\n".join([page.get_text() for page in doc])
lines = pdf_text.strip().split('\n')

# === Extract contact details ===
email = ""
linkedin_url = ""
portfolio_url = ""

for line in lines:
    line_lower = line.lower().strip()
    if "@" in line and "mailto" not in line_lower:
        email = line.strip()
    elif "linkedin.com" in line_lower and not linkedin_url:
        linkedin_url = "https://" + line.strip().replace("https://", "")
    elif "datascienceportfol.io" in line_lower and not portfolio_url:
        portfolio_url = "https://" + line.strip().replace("https://", "")

# === Improved name and title detection (from top of resume) ===
name = ""
title = ""
for line in lines:
    clean_line = line.strip()
    if clean_line and not any(substr in clean_line.lower() for substr in ["www", "http", "linkedin", "portfolio", "@"]):
        if not name:
            name = clean_line
        elif not title:
            title = clean_line
            break  # Got both
print(f"[DEBUG] Name: {name}, Title: {title}")

# === Helper: Generic section extractor ===
def extract_section(text, keyword):
    """Extract lines under a heading."""
    pattern = rf"{keyword}\n(.+?)(?=\n[A-Z][a-z]+|\n\n|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return [line.strip() for line in match.group(1).strip().split("\n") if line.strip()] if match else []

# === Helper: Certification extractor (structured) ===
def extract_certifications(text):
    cert_pattern = r"Certifications\s*(.*?)\n(?:\n|Experience|Education|Skills|Projects|Languages|Organizations)"
    match = re.search(cert_pattern, text, re.DOTALL | re.IGNORECASE)
    if not match:
        return []

    section_text = match.group(1).strip()
    lines = [line.strip() for line in section_text.split("\n") if line.strip()]

    certifications = []
    i = 0
    while i < len(lines):
        cert_name = lines[i]
        issuer = lines[i+1] if i + 1 < len(lines) else ""
        date = lines[i+2] if i + 2 < len(lines) else ""
        if re.search(r"\d{4}", date):
            certifications.append({
                "name": cert_name,
                "issuer": issuer,
                "date": date
            })
            i += 3
        else:
            certifications.append({
                "name": cert_name,
                "issuer": issuer,
                "date": ""
            })
            i += 2
    return certifications

# === Helper: Experience extractor ===
def parse_experience_block(text):
    """Extract experience blocks from LinkedIn PDF format."""
    experience = []
    pattern = r"([A-Za-z &\-,\.]+)\n([A-Za-z0-9 &\-,\.]+)\n([A-Za-z]+\s\d{4})\s-\s(Present|[A-Za-z]+\s\d{4})\s*\((\d+.*?)?\)\n([^\n]*)"
    matches = re.findall(pattern, text)
    for match in matches:
        title, company, start_str, end_str, _, location = match
        try:
            start_date = datetime.strptime(start_str, "%B %Y")
            end_date = datetime.today() if end_str == "Present" else datetime.strptime(end_str, "%B %Y")
            duration = relativedelta(end_date, start_date)
            months = duration.years * 12 + duration.months
            experience.append({
                "position": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "start_date": start_str,
                "end_date": end_str,
                "duration_months": months
            })
        except ValueError:
            continue
    return experience

# === Extract additional sections ===
summary_match = re.search(r"Summary\n(.+?)\nExperience", pdf_text, re.DOTALL | re.IGNORECASE)
summary = summary_match.group(1).strip().replace("\n", " ") if summary_match else ""

skills = extract_section(pdf_text, "Top Skills")
certifications = extract_certifications(pdf_text)
experience = parse_experience_block(pdf_text)
total_months = sum(item['duration_months'] for item in experience)

# === Final JSON object ===
profile_json = {
    "name": name,
    "title": title,
    "location": None,
    "contact": {
        "email": email,
        "linkedin": linkedin_url,
        "portfolio": portfolio_url
    },
    "skills": skills,
    "certifications": certifications,
    "summary": summary,
    "experience": experience,
    "total_experience_years": round(total_months / 12, 1) if total_months else 0
}

# === Save to JSON file ===
with open("linkedin_profile.json", "w", encoding="utf-8") as f:
    json.dump(profile_json, f, indent=2, ensure_ascii=False)

print("✅ Profile extracted and saved to 'linkedin_profile.json'")
