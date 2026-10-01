"""Alerting with a cooldown, so a fault episode doesn't spam you."""
import time
import urllib.request
import urllib.parse
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ALERT_COOLDOWN_SECONDS

_last_alert = 0.0


def _send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10)
    except Exception as e:
        print("Telegram alert failed:", e)


def send_alert(message):
    """Print (and optionally Telegram) an alert, at most once per cooldown."""
    global _last_alert
    now = time.time()
    if now - _last_alert < ALERT_COOLDOWN_SECONDS:
        return False
    _last_alert = now
    print(f"\n*** ALERT *** {message}\n")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        _send_telegram(f"⚠️ {message}")
    return True
