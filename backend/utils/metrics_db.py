import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../metrics.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
       CREATE TABLE IF NOT EXISTS metrics (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           function_name TEXT,
           runtime TEXT,
           duration FLOAT,
           cpu_percent FLOAT,
           memory_mb FLOAT,
           error TEXT,
           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       );
    """)
    conn.commit()
    conn.close()

def store_metrics(function_name, runtime, metrics):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO metrics (
           function_name,
           runtime,
           duration,
           cpu_percent,
           memory_mb,
           error
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        function_name,
        runtime,
        metrics.get("duration", 0),
        metrics.get("cpu_percent", 0),
        metrics.get("memory_mb", 0),
        metrics.get("error")
    ))
    conn.commit()
    conn.close()

def get_aggregated_metrics(function_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT AVG(duration), COUNT(*)
        FROM metrics
        WHERE function_name = ?
    """, (function_name,))
    result = c.fetchone()
    conn.close()
    return {
        "average_duration": result[0],
        "total_invocations": result[1]
    }
def get_runtime_metrics():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT runtime,
               AVG(duration),
               COUNT(*)
        FROM metrics
        GROUP BY runtime
    """)

    rows = c.fetchall()

    conn.close()

    result = {}

    for runtime, avg_duration, count in rows:
        result[runtime] = {
            "average_duration": round(avg_duration, 4),
            "invocations": count
        }

    return result
    

