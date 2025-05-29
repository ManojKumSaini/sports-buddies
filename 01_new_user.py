import os
import csv
import tkinter as tk
from tkinter import messagebox
import hashlib
import requests
import psycopg2
from datetime import datetime

# ----------- DB Login lesen ------------
def read_db_credentials(path="data/config.txt"):
    creds = {}
    with open(path, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            creds[key] = value
    return creds

def connect_to_db(creds):
    return psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        dbname=creds["database"],
        user=creds["user"],
        password=creds["password"]
    )

# ----------- Datei initialisieren ------------
filename = "data/secret_info.csv"
if not os.path.isfile(filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["first_name", "last_name", "place_of_birth", "date_of_birth", "email", "street", "number", "p_code", "city", "user_id"])

# ----------- API-Funktion ------------
def fetch_city_from_postcode(event=None):
    postcode = entry_address_postcode.get()
    if not postcode:
        return
    try:
        response = requests.get(f"https://api.zippopotam.us/de/{postcode}")
        if response.status_code == 200:
            data = response.json()
            city = data["places"][0]["place name"]
            city_var.set(city)
        else:
            city_var.set("Not found")
    except Exception as e:
        city_var.set("Error")

# ----------- Daten eintragen ------------
def submit():
    # Hash erzeugen
    hash_input = (
        entry_first_name.get() +
        entry_last_name.get() +
        entry_birth_place.get() +
        entry_birth_date.get() +
        entry_email.get()
    ).encode("utf-8")
    user_id = hashlib.sha256(hash_input).hexdigest()

    # Alle Eingabedaten
    data = [
        entry_first_name.get(),
        entry_last_name.get(),
        entry_birth_place.get(),
        entry_birth_date.get(),
        entry_email.get(),
        entry_address_street.get(),
        entry_address_number.get(),
        entry_address_postcode.get(),
        city_var.get(),
        user_id
    ]

    # Prüfen auf leere Felder
    if any(field.strip() == "" for field in data):
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return

    # In CSV schreiben
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data)

    # In DB eintragen
    try:
        creds = read_db_credentials()
        conn = connect_to_db(creds)
        cur = conn.cursor()

        # Prüfen, ob user_id schon existiert
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cur.fetchone() is None:
            # Nächste user_number ermitteln
            cur.execute("SELECT MAX(user_number) FROM users")
            result = cur.fetchone()
            next_number = 1 if result[0] is None else result[0] + 1

            # Einfügen
            cur.execute(
                "INSERT INTO users (user_number, user_id, creation_time) VALUES (%s, %s, %s)",
                (next_number, user_id, datetime.now())
            )
            conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not sync with DB:\n{e}")
        return

    messagebox.showinfo("Success", "Data saved successfully.")
    for entry in entries:
        entry.delete(0, tk.END)
    city_var.set("")

# ----------- GUI Setup ------------
root = tk.Tk()
root.title("User Info Entry")

fields = [
    ("First Name", "entry_first_name"),
    ("Last Name", "entry_last_name"),
    ("Place of Birth", "entry_birth_place"),
    ("Date of Birth (dd.mm.yyyy)", "entry_birth_date"),
    ("Email Address", "entry_email"),
    ("Street", "entry_address_street"),
    ("Number", "entry_address_number"),
    ("Postcode", "entry_address_postcode"),
]

entries = []
for idx, (label_text, var_name) in enumerate(fields):
    label = tk.Label(root, text=label_text)
    label.grid(row=idx, column=0, padx=10, pady=5, sticky="e")

    entry = tk.Entry(root, width=40)
    entry.grid(row=idx, column=1, padx=5, pady=5)
    globals()[var_name] = entry
    entries.append(entry)
    
    if label_text == "Postcode":
        entry.bind("<FocusOut>", fetch_city_from_postcode)

# City-Feld
city_var = tk.StringVar()
tk.Label(root, text="City").grid(row=len(fields), column=0, padx=10, pady=5, sticky="e")
tk.Label(root, textvariable=city_var, anchor="w", width=40, relief="sunken").grid(row=len(fields), column=1, padx=10, pady=5, sticky="w")

# Submit-Button
submit_btn = tk.Button(root, text="Submit", command=submit)
submit_btn.grid(row=len(fields)+1, column=0, columnspan=3, pady=15)

root.mainloop()
