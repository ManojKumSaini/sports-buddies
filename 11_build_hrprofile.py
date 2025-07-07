import pandas as pd
import numpy as np
import json
import psycopg2
from datetime import datetime, timedelta
from jinja2 import Template, FileSystemLoader, Environment
import os
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_db_config():
    """Load database configuration from data/config.txt"""
    try:
        with open('data/config.txt', 'r', encoding='utf-8') as f:
            config = {}
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Convert port to int if it's the port field
                    if key == 'port':
                        value = int(value)
                    config[key] = value
            return config
    except FileNotFoundError:
        print("Error: data/config.txt not found")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

# Load DB config from file
DB_CONFIG = load_db_config()

Path("rendered_profiles").mkdir(exist_ok=True)
Path("../images/charts").mkdir(parents=True, exist_ok=True)
Path("templates").mkdir(exist_ok=True)

def get_current_user_id():
    try:
        with open('data/cur_user_selected.txt', 'r', encoding='utf-8') as f:
            user_id = int(f.read().strip())
        return user_id
    except FileNotFoundError:
        print("Error: data/cur_user_selected.txt not found")
        return None
    except ValueError:
        print("Error: Invalid user ID in file")
        return None

def load_json_data():
    try:
        with open('data/event_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Error: data/event_data.json not found")
        return None

def connect_to_db():
    if DB_CONFIG is None:
        print("Error: Database configuration not loaded")
        return None
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def get_linkedin_data(user_id):
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT user_number, exp_years, top_skill_1, top_skill_2, top_skill_3, 
               skill_div_cat, skill_div_index, skill_cat_1, skill_cat_2, 
               cur_job, exp_type, working_type, created_at
        FROM dim_linkedin 
        WHERE user_number = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            columns = ['user_number', 'exp_years', 'top_skill_1', 'top_skill_2', 'top_skill_3', 
                      'skill_div_cat', 'skill_div_index', 'skill_cat_1', 'skill_cat_2', 
                      'cur_job', 'exp_type', 'working_type', 'created_at']
            return pd.Series(result, index=columns)
        return None
    except Exception as e:
        print(f"Error fetching LinkedIn data: {e}")
        if conn:
            conn.close()
        return None

def get_github_data(user_id):
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT user_number, coding_type, repo_count
        FROM dim_github 
        WHERE user_number = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            columns = ['user_number', 'coding_type', 'repo_count']
            return pd.Series(result, index=columns)
        return None
    except Exception as e:
        print(f"Error fetching GitHub data: {e}")
        if conn:
            conn.close()
        return None

def extract_programming_skills(skills_list):
    programming_keywords = [
        'python', 'javascript', 'java', 'sql', 'html', 'css', 'c++', 'c#', 'react', 
        'node', 'angular', 'vue', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
        'typescript', 'programming', 'coding', 'development'
    ]
    programming_skills = []
    for skill in skills_list:
        if any(keyword in skill.lower() for keyword in programming_keywords):
            programming_skills.append(skill)
    return programming_skills[:3]

def get_image_path(category, value):
    value_clean = value.lower().replace(' ', '_')
    if category == 'experience_type':
        return f"../images/icons/skill_diversity_cat_{value_clean}.png"
    elif category == 'working_type':
        return f"../images/icons/working_type_{value_clean}.png"
    elif category == 'coding_type':
        return f"../images/icons/coding_type_{value_clean}.png"
    return ""

def calculate_age_from_experience(exp_years):
    base_age = 23
    return base_age + int(exp_years)

def classify_working_type(linkedin_data):
    analytical_keywords = [
        'analyst', 'data', 'research', 'analytics', 'scientist', 'risk', 'credit', 
        'financial', 'business intelligence', 'statistics', 'quantitative', 'metrics',
        'reporting', 'analysis', 'insight', 'modeling', 'forecasting', 'evaluation',
        'assessment', 'audit', 'compliance', 'quality assurance', 'consultant',
        'advisor', 'strategic', 'planning', 'intelligence', 'economics', 'finance'
    ]
    
    creative_keywords = [
        'design', 'creative', 'marketing', 'brand', 'content', 'digital marketing',
        'social media', 'graphic', 'ui', 'ux', 'user experience', 'product design',
        'art', 'visual', 'advertising', 'campaign', 'innovation', 'concept',
        'copywriter', 'writer', 'editor', 'photographer', 'video', 'multimedia',
        'web design', 'frontend', 'creative director', 'communications', 'pr'
    ]
    
    operational_keywords = [
        'operations', 'manager', 'coordinator', 'administrator', 'supervisor',
        'executive', 'officer', 'director', 'head', 'lead', 'team lead',
        'project manager', 'program manager', 'account manager', 'sales',
        'customer service', 'support', 'hr', 'human resources', 'recruiting',
        'logistics', 'supply chain', 'procurement', 'vendor', 'client relations',
        'business development', 'relationship manager', 'implementation',
        'deployment', 'integration', 'workflow', 'process', 'production'
    ]
    
    experience = linkedin_data.get("experience", [])
    if not experience:
        return "No Data"
    
    analytical_score = 0
    creative_score = 0
    operational_score = 0
    
    for job in experience:
        position = job.get("position", "").lower()
        company = job.get("company", "").lower()
        duration = job.get("duration_months", 1)
        job_text = f"{position} {company}"
        
        analytical_score += sum(1 for kw in analytical_keywords if kw in job_text) * duration
        creative_score += sum(1 for kw in creative_keywords if kw in job_text) * duration
        operational_score += sum(1 for kw in operational_keywords if kw in job_text) * duration
    
    max_score = max(analytical_score, creative_score, operational_score)
    
    if max_score == 0:
        return "No Data"
    if max_score == analytical_score:
        return "Analytical"
    elif max_score == creative_score:
        return "Creative"
    else:
        return "Operational"

def generate_html_template(data):
    template_loader = FileSystemLoader('templates')
    template_env = Environment(loader=template_loader)
    template = template_env.get_template('hr_profile_template.html')
    return template.render(**data)

def generate_hr_profile(user_id=None):
    if user_id is None:
        user_id = get_current_user_id()
        if user_id is None:
            return "Error: Could not get user ID"
    
    print(f"Generating profile for user ID: {user_id}")
    
    json_data = load_json_data()
    linkedin_data = get_linkedin_data(user_id)
    github_data = get_github_data(user_id)
    
    print(f"JSON data loaded: {json_data is not None}")
    print(f"LinkedIn data loaded: {linkedin_data is not None}")
    print(f"GitHub data loaded: {github_data is not None}")
    
    if not json_data:
        return "Error: Could not load JSON data"
    
    linkedin_json = json_data['payload']['linkedin']
    github_json = json_data['payload']['github']
    
    if 'payload' in linkedin_json and 'linkedin' in linkedin_json['payload']:
        actual_linkedin_data = linkedin_json['payload']['linkedin']
    else:
        actual_linkedin_data = linkedin_json
    
    if github_data is None:
        github_data = pd.Series({
            'coding_type': 'occasional_coder'
        })
    
    name = None
    if 'name' in actual_linkedin_data and actual_linkedin_data['name'] != 'Contact':
        name = actual_linkedin_data['name']
    elif 'name' in github_json:
        name = github_json['name']
    else:
        name = json_data['payload'].get('spotify', {}).get('user_profile', {}).get('display_name', 'Unknown User')
    
    full_name_parts = name.split()
    first_name = full_name_parts[0] if full_name_parts else "Unknown"
    last_name = full_name_parts[-1] if len(full_name_parts) > 1 else ""
    
    email = actual_linkedin_data.get('contact', {}).get('email', 'No email provided')
    location = github_json.get('location') or actual_linkedin_data.get('location') or "Unknown"
    
    experience_years = actual_linkedin_data.get('total_experience_years', linkedin_data.get('exp_years', 0))
    experience_years = float(experience_years) if experience_years else 0
    age = calculate_age_from_experience(experience_years)
    
    positions = actual_linkedin_data.get('experience', [])
    current_position = positions[0] if positions else {"company": "Unknown", "position": "Unknown"}
    company_name = current_position.get('position', 'Unknown')
    position_title = current_position.get('company', 'Unknown')
    current_role = f"{position_title} at {company_name}"
    
    db_skills = [linkedin_data.get('top_skill_1'), linkedin_data.get('top_skill_2'), linkedin_data.get('top_skill_3')]
    if all(skill and skill != 'N/A' for skill in db_skills):
        top_skills = db_skills
    else:
        json_skills = actual_linkedin_data.get('skills', [])
        top_skills = json_skills[:3] if json_skills else ['Python', 'SQL', '']
    
    programming_skills = extract_programming_skills(actual_linkedin_data.get('skills', []))
    
    experience_type = linkedin_data.get('skill_div_cat', 'well_rounded')
    
    # Use the new classify_working_type function
    working_type = classify_working_type(actual_linkedin_data)
    
    coding_type = github_data.get('coding_type', 'Low Coder')
    
    experience_image = get_image_path('experience_type', experience_type)
    working_type_image = get_image_path('working_type', working_type)
    coding_type_image = get_image_path('coding_type', coding_type)
    
    position_tags = []
    for pos in positions[:3]:
        job_title = pos.get('company', 'Unknown')
        if job_title != 'Unknown':
            position_tags.append(job_title)
    
    if not position_tags and linkedin_data.get('cur_job') and linkedin_data.get('cur_job') != 'not found':
        position_tags = [linkedin_data.get('cur_job')]
    
    if not position_tags:
        position_tags = [f"Professional with {experience_years} years experience"]
    
    # Add user picture path
    user_picture_path = f"../images/user_pictures/{first_name.lower()}_picture_hr.png"
    
    # Use existing heatmap image with user's name
    heatmap_image_path = f"../images/charts/working_time_heatmap_{first_name.lower()}.png"
    
    template_data = {
        'name': name,
        'first_name': first_name,
        'last_name': last_name,
        'age': age,
        'location': location,
        'current_role': current_role,
        'email': email,
        'experience_years': experience_years,
        'experience_type': experience_type,
        'experience_image': experience_image,
        'position_tags': position_tags,
        'top_skills': top_skills,
        'working_type': working_type,
        'working_type_image': working_type_image,
        'coding_type': coding_type,
        'coding_type_image': coding_type_image,
        'programming_skills': programming_skills,
        'user_picture': user_picture_path,
        'skills_graph_image': f"../images/charts/skills_graph_{first_name}.png",
        'stability_image': f"../images/charts/job_stability_score_{first_name}.png",
        'heatmap_image': heatmap_image_path
    }
    
    html_content = generate_html_template(template_data)
    
    if html_content is None:
        return "Error: Could not generate HTML template"
    
    output_filename = f"rendered_profiles/hrprofile_{first_name}_{last_name}.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Profile generated successfully: {output_filename}")
    return output_filename

if __name__ == "__main__":
    print("Testing database connection...")
    conn = connect_to_db()
    if conn:
        print("✓ Database connection successful")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            print(f"Available tables: {[table[0] for table in tables]}")
            cursor.execute("SELECT COUNT(*) FROM dim_linkedin")
            print(f"Records in dim_linkedin: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM dim_github")
            print(f"Records in dim_github: {cursor.fetchone()[0]}")
            cursor.close()
        except Exception as e:
            print(f"Table test error: {e}")
        conn.close()
    else:
        print("✗ Database connection failed")
    
    print("\nGenerating profile...")
    result = generate_hr_profile()
    print(f"Result: {result}")