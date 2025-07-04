import pandas as pd
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pytz
import requests
import psycopg2
import os
import pickle



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
def data_from_data_sink(query):
    creds = read_db_credentials()
    conn = connect_to_db(creds)
    cur = conn.cursor()
    
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    return df

def save_df_to_db(df, table_name, conflict_column='user_number'):
    creds = read_db_credentials()
    conn = connect_to_db(creds)
    cursor = conn.cursor()
    
    df = df.where(pd.notnull(df), None)  # Replace NaN with None for SQL

    columns = list(df.columns)
    column_names = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))

    # Set update expression for each column
    update_assignments = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != conflict_column])

    insert_query = f"""
        INSERT INTO {table_name} ({column_names})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_column})
        DO UPDATE SET {update_assignments};
    """

    for _, row in df.iterrows():
        cursor.execute(insert_query, row.tolist())

    conn.commit()
    cursor.close()
    conn.close()
    return "saved (with upsert)"

    
def load_json_data_from_db_as_json(user, source):
    creds = read_db_credentials()
    conn = connect_to_db(creds)

    query = f"SELECT raw_json FROM fact_raw_data WHERE data_source = '{source}' AND user_number = {user};"
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()

    parsed_data = result[0] if result else {}
    return parsed_data


def get_user_number_from_config(path="data/cur_user_selected.txt"):
    with open(path, "r") as f:
        return int(f.read().strip())