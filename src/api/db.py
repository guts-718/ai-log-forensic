import sqlite3
import json

conn = sqlite3.connect("logs.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT
)
""")

def insert_log(log):
    cursor.execute("INSERT INTO logs (data) VALUES (?)", (json.dumps(log),))
    conn.commit()

def get_logs():
    cursor.execute("SELECT data FROM logs")
    rows = cursor.fetchall()
    return [json.loads(r[0]) for r in rows]