"""Shared settings for local development and Streamlit Cloud."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def setting(name, default=""):
    # Prefer environment variables for local development.
    value = os.getenv(name)
    if value is not None:
        return value

    # Streamlit Cloud secrets are accessed through st.secrets.
    try:
        import streamlit as st
        return str(st.secrets[name])
    except (ImportError, KeyError, FileNotFoundError):
        return default


DB_PATH = setting("DB_PATH", str(ROOT / "data" / "sensor_data.db"))

BROKER = setting("MQTT_BROKER").strip()
PORT = int(setting("MQTT_PORT", "8883"))
USERNAME = setting("MQTT_USERNAME").strip()
PASSWORD = setting("MQTT_PASSWORD")
TOPIC = setting("MQTT_TOPIC", "factory/machine01/rotating").strip()

TELEGRAM_BOT_TOKEN = setting("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = setting("TELEGRAM_CHAT_ID")
ALERT_COOLDOWN_SECONDS = int(setting("ALERT_COOLDOWN_SECONDS", "120"))


def make_mqtt_client():
    """Create a TLS-enabled MQTT client for HiveMQ Cloud."""
    import paho.mqtt.client as mqtt

    if hasattr(mqtt, "CallbackAPIVersion"):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    else:
        client = mqtt.Client()

    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    return client
