"""
Synthetic rotating-machine telemetry generator.

  python src/synthetic_generator.py           -> publish to HiveMQ via MQTT
  python src/synthetic_generator.py --local   -> no broker: write straight to SQLite
  Options: --interval 5   seconds between readings

A "developing fault" makes vibration and bearing temperature drift up while
RPM sags, mimicking bearing wear / lubrication loss.
"""
import argparse
import json
import random
import time
from datetime import datetime, timezone
from config import BROKER, PORT, TOPIC, make_mqtt_client

DEVICE_ID = "MACHINE_01"
BASE_VIBRATION, BASE_TEMP, BASE_RPM = 2.0, 45.0, 1500.0

fault_active = False
fault_progress = 0.0


def generate_reading():
    global fault_active, fault_progress
    if not fault_active and random.random() < 0.02:
        fault_active, fault_progress = True, 0.0

    if fault_active:
        fault_progress += random.uniform(0.05, 0.15)
        vibration = BASE_VIBRATION + fault_progress * random.uniform(4, 7)
        temp = BASE_TEMP + fault_progress * random.uniform(10, 18)
        rpm = BASE_RPM - fault_progress * random.uniform(20, 60)
        if fault_progress >= 1.0:
            fault_active, fault_progress = False, 0.0
    else:
        vibration = random.normalvariate(BASE_VIBRATION, 0.25)
        temp = random.normalvariate(BASE_TEMP, 1.5)
        rpm = random.normalvariate(BASE_RPM, 10)

    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vibration_rms": round(max(vibration, 0), 3),
        "bearing_temp": round(temp, 2),
        "rpm": round(rpm, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true", help="skip MQTT, write to SQLite")
    ap.add_argument("--interval", type=float, default=5.0)
    args = ap.parse_args()

    if args.local:
        from database import init_db
        from processing import process_reading
        init_db()
        print("LOCAL mode: writing directly to SQLite (no MQTT).")
        while True:
            p = generate_reading()
            _, flag = process_reading(p)
            print(p, "-> ANOMALY" if flag else "")
            time.sleep(args.interval)

    if not BROKER:
        raise SystemExit("MQTT_BROKER is empty. Fill in .env, or use --local.")
    client = make_mqtt_client()
    client.connect(BROKER, PORT, 60)
    client.loop_start()          # needed so messages are actually sent over TLS
    print(f"Publishing to topic: {TOPIC}")
    while True:
        p = generate_reading()
        client.publish(TOPIC, json.dumps(p), qos=1)
        print(p)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
