"""Store a reading, score it against recent history, and alert if abnormal."""
from database import insert_reading, update_anomaly_flags
from anomaly_detector import load_data, detect_anomalies
from alerts import send_alert


def process_reading(p):
    row_id = insert_reading(p["device_id"], p["timestamp"], p["vibration_rms"],
                            p["bearing_temp"], p["rpm"])
    df = detect_anomalies(load_data(300))
    latest = df.iloc[-1]
    flag = int(latest["is_anomaly"])
    if flag == 1:
        update_anomaly_flags([(row_id, 1)])
        send_alert(
            f"{p['device_id']}: anomaly - vibration {p['vibration_rms']} mm/s, "
            f"bearing {p['bearing_temp']} C, {p['rpm']} RPM"
        )
    return row_id, flag
