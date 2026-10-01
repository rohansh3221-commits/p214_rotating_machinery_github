"""MQTT subscriber: receives telemetry from HiveMQ Cloud, stores + scores it."""
import json
from config import BROKER, PORT, TOPIC, make_mqtt_client
from database import init_db
from processing import process_reading

REQUIRED = ["device_id", "timestamp", "vibration_rms", "bearing_temp", "rpm"]


def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected, result code:", rc)   # 0 = success, 5 = bad credentials
    client.subscribe(TOPIC, qos=1)


def on_message(client, userdata, msg):
    try:
        p = json.loads(msg.payload.decode("utf-8"))
        if not all(k in p for k in REQUIRED):
            print("Missing field(s), skipping:", p)
            return
        _, flag = process_reading(p)
        print("Stored:", p, "-> ANOMALY" if flag else "")
    except Exception as e:
        print("Invalid message:", e)


def main():
    if not BROKER:
        raise SystemExit("MQTT_BROKER is empty. Fill in your .env file first.")
    init_db()
    client = make_mqtt_client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
