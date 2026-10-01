
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
from anomaly_detector import load_data, detect_anomalies, sync_anomaly_flags, MIN_ROWS
from database import init_db

st.set_page_config(page_title="Rotating Machinery Monitor", layout="wide")
st.title("Predictive Maintenance - Rotating Machinery (P_214)")

st.sidebar.header("Settings")
window = st.sidebar.slider("Readings to analyse", 50, 1000, 300, step=50)
refresh = st.sidebar.slider("Refresh every (seconds)", 2, 30, 5)
auto = st.sidebar.checkbox("Auto-refresh", value=True)

init_db()
df = load_data(window)

if df.empty:
    st.warning("No sensor data yet. Start the generator (and subscriber) first.")
else:
    df = detect_anomalies(df)
    sync_anomaly_flags(df)
    latest = df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vibration RMS", f"{latest['vibration_rms']:.2f} mm/s")
    c2.metric("Bearing Temp", f"{latest['bearing_temp']:.1f} °C")
    c3.metric("RPM", f"{latest['rpm']:.0f}")
    c4.metric("Status", "ANOMALY" if latest["is_anomaly"] else "NORMAL")

    if len(df) < MIN_ROWS:
        st.info(f"Collecting data: {len(df)}/{MIN_ROWS} readings before detection starts.")
    elif latest["is_anomaly"] == 1:
        st.error("⚠️ Anomaly detected — possible developing fault (check vibration / bearing temp trend).")
    else:
        st.success("Machine operating normally.")

    chart = df.set_index("timestamp")
    st.subheader("Vibration RMS (mm/s)")
    st.line_chart(chart["vibration_rms"])
    st.subheader("Bearing Temperature (°C)")
    st.line_chart(chart["bearing_temp"])
    st.subheader("RPM")
    st.line_chart(chart["rpm"])

    st.subheader("Recent Anomalies")
    an = df[df["is_anomaly"] == 1].sort_values("id", ascending=False)
    if an.empty:
        st.write("No anomalies in the current window.")
    else:
        st.dataframe(an[["timestamp", "vibration_rms", "bearing_temp", "rpm"]])

    st.subheader("Recent Readings")
    st.dataframe(df.tail(20).iloc[::-1])
    st.caption(f"Readings shown: {len(df)} | Anomalies flagged: {int(df['is_anomaly'].sum())}")

if auto:
    time.sleep(refresh)
    st.rerun()
