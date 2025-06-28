
import os
import json
import pandas as pd
import glob

import tkinter as tk
from tkinter import filedialog

def select_data_folder():
    root = tk.Tk()
    root.withdraw()  # Kein Hauptfenster anzeigen
    folder_selected = filedialog.askdirectory(title="Wähle einen Datenordner aus")
    return folder_selected

data_folder = select_data_folder()

all_data = {}

# Find all CSV files in the directory
csv_files = glob.glob(os.path.join(data_folder, "*.csv"))

for csv_file in csv_files:
    try:
        # Get the filename without extension to use as key
        filename = os.path.basename(csv_file).replace('.csv', '')
        
        # Read CSV file using pandas
        df = pd.read_csv(csv_file)
        
        # Convert to JSON (as list of dictionaries)
        json_data = df.to_dict('records')
        
        # Store in the main dictionary
        all_data[filename] = json_data
        
        print(f"Processed {filename} - {len(json_data)} records")
        
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")

# Save all combined data to a single JSON file
output_file = os.path.join("../user_data/strava_export_combined.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"All data combined into {output_file}")
print(f"Total files processed: {len(all_data)}")