
import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from config import DB_PATH

FEATURES = ["vibration_rms", "bearing_temp", "rpm"]
MIN_ROWS = 30


def load_data(limit=500):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    try:
        df = pd.read_sql_query(
            "SELECT * FROM sensor_data ORDER BY id DESC LIMIT ?", conn, params=(limit,)
        )
    finally:
        conn.close()
    return df.sort_values("id").reset_index(drop=True)


def _healthy_mask(X):
    """Rows within 3 robust (MAD-based) deviations of the median on every feature."""
    med = X.median()
    mad = (X - med).abs().median().replace(0, 1e-6) * 1.4826
    z = ((X - med) / mad).abs()
    return (z < 3).all(axis=1)


def detect_anomalies(df):
    df = df.copy()
    if len(df) < MIN_ROWS:
        df["score"] = 0.0
        df["is_anomaly"] = 0
        return df

    X = df[FEATURES]
    healthy = _healthy_mask(X)
    train = X[healthy] if healthy.sum() >= MIN_ROWS else X

    scaler = StandardScaler().fit(train)
    model = IsolationForest(n_estimators=150, contamination=0.005, random_state=42)
    model.fit(scaler.transform(train))

    scaled = scaler.transform(X)
    df["score"] = model.decision_function(scaled)      # lower = more abnormal
    df["is_anomaly"] = (model.predict(scaled) == -1).astype(int)
    return df


def sync_anomaly_flags(df):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    try:
        with conn:
            conn.executemany(
                "UPDATE sensor_data SET is_anomaly = ? WHERE id = ?",
                [(int(a), int(i)) for a, i in zip(df["is_anomaly"], df["id"])],
            )
    finally:
        conn.close()


if __name__ == "__main__":
    data = load_data()
    if data.empty:
        print("No data yet. Run the generator first.")
    else:
        res = detect_anomalies(data)
        sync_anomaly_flags(res)
        print(f"Processed {len(res)} rows, {int(res['is_anomaly'].sum())} flagged.")
