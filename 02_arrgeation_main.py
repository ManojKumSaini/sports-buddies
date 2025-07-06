import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from functions import get_user_number_from_config, data_from_data_sink

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

# # CSV-Pfad
# csv_path = os.path.join("data", "secret_info.csv")
# output_path = os.path.join("data", "cur_user_selected.txt")

# # CSV laden
# try:
#     df = pd.read_csv(csv_path)
# except FileNotFoundError:
#     messagebox.showerror("Fehler", f"Datei nicht gefunden: {csv_path}")
#     exit()

# # Prüfen, ob benötigte Spalten existieren
# required_cols = {"first_name","last_name","user_id"}
# if not required_cols.issubset(df.columns):
#     messagebox.showerror("Fehler", f"CSV muss die Spalten {required_cols} enthalten")
#     exit()

# # Optionen für Dropdown: "Name Secondname"
# name_options = [f"{row['first_name']} {row['last_name']}" for _, row in df.iterrows()]
# name_to_id = {
#     f"{row['first_name']} {row['last_name']}": row["user_id"] for _, row in df.iterrows()
# }



# # Tkinter GUI
# def on_select(event=None):
#     selected = combo.get()
#     user_id = name_to_id.get(selected)
#     num = data_from_data_sink(f"""
#                     SELECT user_number FROM dim_user WHERE user_id = '{user_id}' LIMIT 1;
#                     """)


#     num = num["user_number"][0]
#     if user_id:
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(str(num))
#         messagebox.showinfo("Erfolg", f"user_id '{user_id} num {num}' wurde in cur_user.txt gespeichert.")
#         root.quit()
#     else:
#         messagebox.showwarning("Fehler", "Benutzer nicht gefunden.")

# root = tk.Tk()
# root.title("Benutzer auswählen")

# label = ttk.Label(root, text="Wähle einen Benutzer:")
# label.pack(padx=10, pady=(10, 2))

# combo = ttk.Combobox(root, values=name_options, state="readonly", width=40)
# combo.pack(padx=10, pady=5)
# combo.bind("<<ComboboxSelected>>", on_select)
# combo.current(0)  # erste Option vorauswählen

# button = ttk.Button(root, text="Bestätigen", command=on_select)
# button.pack(padx=10, pady=(5, 10))

# root.mainloop()



user = get_user_number_from_config()

print(user)

sources = data_from_data_sink(f"SELECT data_source FROM fact_raw_data WHERE user_number = {user};")
sources = sources["data_source"].tolist()

print(sources)

def execute_notebook(notebook_path):
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='myenv')
    ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
    print(f"✅ Notebook ausgeführt: {notebook_path}")

if "health" in sources:
    print("run health")
    execute_notebook("02_aggregation_notebooks/02_health_aggregation.ipynb")

if "strava" in sources:
    print("run strava")
    execute_notebook("02_aggregation_notebooks/04_strava_aggregation.ipynb")

if "linkedin" in sources:
    print("run linkedin")
    execute_notebook("02_aggregation_notebooks/05_linkedin_aggregation.ipynb")

if "steam" in sources:
    print("run steam")
    execute_notebook("02_aggregation_notebooks/06_steam_aggregation.ipynb")

if "github" in sources:
    print("run github")
    execute_notebook("02_aggregation_notebooks/07_github_aggregation.ipynb")

if "spotify" in sources:
    print("run spotify")
    execute_notebook("02_aggregation_notebooks/08_spotify_aggregation.ipynb")
    
print("done!")
    