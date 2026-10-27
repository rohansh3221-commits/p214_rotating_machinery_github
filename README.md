# P_214 – Predictive Maintenance for Rotating Machinery

Synthetic generator → MQTT (HiveMQ Cloud) → Python subscriber → SQLite
→ Isolation Forest → Streamlit dashboard + alerts (with cooldown).

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
```

## Option A: quick test, no MQTT needed
```bash
# Terminal 1
python src/synthetic_generator.py --local --interval 1
# Terminal 2
streamlit run dashboard/app.py
```

## Option B: full pipeline with HiveMQ Cloud
1. Create a free Serverless cluster at hivemq.com, note the cluster URL.
2. In Access Management, create credentials with Publish + Subscribe.
3. Copy `.env.example` to `.env` and fill in the broker, username, password.
4. Run three terminals (venv active, from the project root):
```bash
python src/mqtt_subscriber.py
python src/synthetic_generator.py
streamlit run dashboard/app.py
```

## Alerts
Alerts print in the subscriber terminal. For Telegram, create a bot with
@BotFather and put `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.
`ALERT_COOLDOWN_SECONDS` (default 120) limits how often alerts are sent.

## How detection works
Isolation Forest is trained on the healthy-looking part of the last 300
readings (outliers excluded from training), then scores every reading.
Detection starts after 30 readings. In offline tests it caught ~85% of
injected fault readings with ~3% false alarms; the misses are the earliest
fault readings, which are still close to normal.

## Troubleshooting
| Problem | Fix |
|---|---|
| `result code: 5` | Wrong MQTT username/password |
| SSL / timeout error | Check cluster URL and port 8883 |
| Dashboard empty | Generator/subscriber not running |
| `ModuleNotFoundError` | Activate the venv and reinstall requirements |

## Future work
XGBoost on a labeled dataset (e.g. CWRU), real MPU6050 + ESP32 sensor.

P214 Rotating Machinery Dashboard

Live Dashboard

Open the live project dashboard here:

https://p214rotatingmachineryappgit-gfz2hronfxhpgdfk7n3fcq.streamlit.app/

GitHub Repository

View the project source code here:

https://github.com/rohansh3221-commits/p214_rotating

Project Description

This project monitors rotating machinery parameters through a dashboard built using Python and Streamlit.

Features

- Interactive dashboard for machinery readings
- Visualization of sensor data
- Online access through a web browser

How to Access

Click the Live Dashboard link above to view the deployed application.
