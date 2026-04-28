import pandas as pd
import sqlite3
from datetime import datetime

DB_NAME = 'smart_energy_tracker.db'


def clean_data(df):
    print("Data Summary: ")
    print(df.describe(include='all'))
    print("\n Missing values per column: ")
    print(df.isnull().sum())
    print("\n Cleaning the data...")
    #Only drop rows if power or main columns are NaN
    main_cols = ['Global_active_power']  # columns required for analysis
    df = df.dropna(subset=main_cols)
    df = df.reset_index(drop=True)
    print("\n Data after cleaning is ", df.shape)
    return df


def detect_anomalies(df):
    print("\n Detecting anomalies...")
    df['power'] = pd.to_numeric(df['power'], errors="coerce")
    Q1 = df['power'].quantile(0.25)
    Q3 = df['power'].quantile(0.75)
    IQR = Q3 - Q1
    anomalies = df[(df['power'] < Q1 - 1.5*IQR) | (df['power'] > Q3 + 1.5*IQR)]
    print(anomalies)
    return anomalies


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AnomalyDetector (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName TEXT,
            SavedAt TEXT,
            FileBlob BLOB
        )
    ''')
    conn.commit()
    conn.close()


def save_anomaly_file(file_name, file_blob):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO AnomalyDetector (FileName, SavedAt, FileBlob)
            VALUES (?, ?, ?)
        ''', (file_name, saved_at, file_blob))
        conn.commit()
        conn.close()
    finally:    
        if conn:
            conn.close()


def get_anomaly_file(file_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT FileBlob FROM AnomalyDetector
        WHERE FileName = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (file_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None