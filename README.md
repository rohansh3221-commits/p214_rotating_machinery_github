
## P214 Rotating Machinery Dashboard

🚀 Live Dashboard

"Click here to open the live dashboard" (https://p214rotatingmachineryappgit-gfz2hronfxhpgdfk7n3fcq.streamlit.app/)

📂 GitHub Repository

"View the project source code" (https://github.com/rohansh3221-commits/p214_rotating_machinery_github.git)

📌 Project Overview

The P214 Rotating Machinery Dashboard is a Python-based application built using Streamlit to visualize rotating machinery readings and sensor data.

✨ Features

- Interactive dashboard for machinery readings
- Visualization of sensor data
- Web-based access to the deployed dashboard

🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- Data visualization libraries


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


## Working Dashboard Screenshots
<img width="1917" height="1078" alt="Screenshot 2026-10-30 214607" src="https://github.com/user-attachments/assets/d0553a00-fe6b-4a7d-8795-a21f002dd8d4" />
<img width="1908" height="1077" alt="Screenshot 2026-10-30 214636" src="https://github.com/user-attachments/assets/5829d9b1-69c0-4094-8ede-b27d094989b3" />
<img width="1917" height="1078" alt="Screenshot 2026-10-30 214653" src="https://github.com/user-attachments/assets/82ef52aa-5301-457d-9190-57903de71a99" />
<img width="1907" height="1060" alt="Screenshot 2026-10-30 214714" src="https://github.com/user-attachments/assets/78b80f38-b0bf-48d8-8220-e004a81397d5" />
<img width="1913" height="1076" alt="Screenshot 2026-10-30 214726" src="https://github.com/user-attachments/assets/8cb34457-bf91-4241-884b-098c1b509643" />
<img width="1917" height="1078" alt="Screenshot 2026-10-30 214738" src="https://github.com/user-attachments/assets/0c3a6eec-b7c9-4c9f-9e0a-f33213e2b76d" />
