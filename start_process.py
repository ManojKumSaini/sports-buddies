import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import pandas as pd

# === CSV-Daten einlesen ===

csv_path = os.path.join("data", "secret_info.csv")

# Mapping: sichtbarer Wert (Spalte 1) → interner Key (Spalte 10)
entry_map = {}

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if len(row) >= 10:
            entry_map[row[0]] = row[9]

options = list(entry_map.keys())

# === GUI erstellen ===

root = tk.Tk()
root.title("Wähle einen Eintrag aus")

selected = tk.StringVar()
selected.set(options[0])

# === DB-Funktionen ===

def read_db_credentials(path="data/config.txt"):
    creds = {}
    with open(path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key.strip()] = value.strip()
    return creds

def connect_to_db(creds):
    return psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        dbname=creds["database"],
        user=creds["user"],
        password=creds["password"]
    )

def data_from_data_sink(query, params=None):
    creds = read_db_credentials()
    conn = connect_to_db(creds)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# === Aktion bei Klick ===

def confirm():
    display_value = selected.get()
    key = entry_map.get(display_value)

    if not key:
        messagebox.showwarning("Fehler", "Kein passender Key gefunden.")
        return

    try:
        query = "SELECT user_number FROM dim_user WHERE user_id = %s"
        user = data_from_data_sink(query, params=[key])

        if not user.empty:
            user_number = user.iloc[0]['user_number']
            messagebox.showinfo("Ergebnis", f"user_number: {user_number}")
            root.destroy()  # Fenster schließen
            global selected_user_number
            selected_user_number = user_number  # Wert für später speichern
            with open("data/cur_user_selected.txt", "w", encoding="utf-8") as f:
                 f.write(str(selected_user_number))

        else:
            messagebox.showwarning("Kein Treffer", "Kein Eintrag in der Datenbank gefunden.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Datenbankfehler:\n{e}")

# === GUI-Elemente ===

ttk.Label(root, text="Bitte wähle einen Eintrag:").pack(padx=10, pady=10)
ttk.Combobox(root, textvariable=selected, values=options, state="readonly").pack(padx=10, pady=5)

# Button wird global referenziert, um ihn im Callback zu deaktivieren
confirm_button = ttk.Button(root, text="Bestätigen", command=confirm)
confirm_button.pack(padx=10, pady=15)

# GUI starten
root.mainloop()  # Fenster schließen
print(selected_user_number)