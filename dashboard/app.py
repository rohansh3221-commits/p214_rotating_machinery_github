import sys
import json
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
from anomaly_detector import (
    load_data,
    detect_anomalies,
    sync_anomaly_flags,
    MIN_ROWS,
)
from database import init_db
from config import BROKER, PORT, TOPIC, make_mqtt_client
from processing import process_reading

st.set_page_config(
    page_title="Rotating Machinery Monitor",
    layout="wide",
)

st.title("Predictive Maintenance - Rotating Machinery (P_214)")


# Start one MQTT client per Streamlit server process.
@st.cache_resource
def start_mqtt():
    if not BROKER:
        return None, "MQTT_BROKER is missing from Secrets."

    client = make_mqtt_client()
    client._mqtt_status = "Connecting to HiveMQ..."

    def on_connect(client, userdata, flags, reason_code, properties=None):
        code = getattr(reason_code, "value", reason_code)

        if code == 0:
            client._mqtt_status = "Connected to HiveMQ"

            result, _ = client.subscribe(TOPIC, qos=1)
            if result != 0:
                client._mqtt_status = (
                    f"Connected, but subscription failed: {result}"
                )
        else:
            client._mqtt_status = (
                f"MQTT connection rejected: {reason_code}"
            )

    def on_disconnect(
        client, userdata, disconnect_flags, reason_code=None,
        properties=None
    ):
        if reason_code is None:
            reason_code = disconnect_flags

        code = getattr(reason_code, "value", reason_code)
        client._mqtt_status = f"Disconnected from HiveMQ: {code}"

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))

            required = [
                "device_id",
                "timestamp",
                "vibration_rms",
                "bearing_temp",
                "rpm",
            ]

            if all(key in payload for key in required):
                process_reading(payload)
            else:
                print("MQTT message missing required fields:", payload)

        except Exception as exc:
            print("MQTT message processing error:", exc)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        return client, "Connecting to HiveMQ..."
    except Exception as exc:
        return None, f"MQTT connection failed: {exc}"


init_db()
client, mqtt_status = start_mqtt()

st.caption(f"MQTT topic: {TOPIC}")

if client is None:
    st.error(mqtt_status)
elif client.is_connected():
    st.success("Connected to HiveMQ")
else:
    st.info(getattr(client, "_mqtt_status", mqtt_status))


# Dashboard settings
st.sidebar.header("Settings")

window = st.sidebar.slider(
    "Readings to analyse",
    50,
    1000,
    300,
    step=50,
)

refresh = st.sidebar.slider(
    "Refresh every (seconds)",
    2,
    30,
    5,
)

auto = st.sidebar.checkbox("Auto-refresh", value=True)


# Load readings
df = load_data(window)

if df.empty:
    st.warning(
        "No sensor data yet. Confirm the MQTT connection and publish "
        "readings to the configured HiveMQ topic."
    )

else:
    df = detect_anomalies(df)
    sync_anomaly_flags(df)
    latest = df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Vibration RMS",
        f"{latest['vibration_rms']:.2f} mm/s",
    )

    c2.metric(
        "Bearing Temp",
        f"{latest['bearing_temp']:.1f} °C",
    )

    c3.metric(
        "RPM",
        f"{latest['rpm']:.0f}",
    )

    c4.metric(
        "Status",
        "ANOMALY" if latest["is_anomaly"] else "NORMAL",
    )

    if len(df) < MIN_ROWS:
        st.info(
            f"Collecting data: {len(df)}/{MIN_ROWS} readings "
            "before detection starts."
        )
    elif latest["is_anomaly"] == 1:
        st.error(
            "Anomaly detected — check vibration and bearing temperature."
        )
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

    anomalies = df[df["is_anomaly"] == 1].sort_values(
        "id",
        ascending=False,
    )

    if anomalies.empty:
        st.write("No anomalies in the current window.")
    else:
        st.dataframe(
            anomalies[
                [
                    "timestamp",
                    "vibration_rms",
                    "bearing_temp",
                    "rpm",
                ]
            ]
        )

    st.subheader("Recent Readings")
    st.dataframe(df.tail(20).iloc[::-1])

    st.caption(
        f"Readings shown: {len(df)} | "
        f"Anomalies flagged: {int(df['is_anomaly'].sum())}"
    )


# Automatically refresh the dashboard.
if auto:
    time.sleep(refresh)
    st.rerun()
