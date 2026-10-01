"""SQLite storage for rotating-machinery sensor data."""
import os
import sqlite3
from config import DB_PATH


def _connect():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _connect()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    vibration_rms REAL NOT NULL,
                    bearing_temp REAL NOT NULL,
                    rpm REAL NOT NULL,
                    is_anomaly INTEGER DEFAULT 0
                )
            """)
    finally:
        conn.close()


def insert_reading(device_id, timestamp, vibration_rms, bearing_temp, rpm, is_anomaly=0):
    """Insert one reading and return its row id."""
    conn = _connect()
    try:
        with conn:
            cur = conn.execute(
                """INSERT INTO sensor_data
                   (device_id, timestamp, vibration_rms, bearing_temp, rpm, is_anomaly)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (device_id, timestamp, vibration_rms, bearing_temp, rpm, is_anomaly),
            )
            return cur.lastrowid
    finally:
        conn.close()


def update_anomaly_flags(ids_and_flags):
    """ids_and_flags: list of (row_id, is_anomaly)."""
    conn = _connect()
    try:
        with conn:
            conn.executemany(
                "UPDATE sensor_data SET is_anomaly = ? WHERE id = ?",
                [(int(flag), int(row_id)) for row_id, flag in ids_and_flags],
            )
    finally:
        conn.close()
