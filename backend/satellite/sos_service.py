from datetime import datetime
import pytz
import json
import os
import requests
from backend.satellite.twilio_adapter import send_message

LOG_FILE = "backend/logs/sos_log.json"


# ---------------- SEVERITY LOGIC ----------------
def get_severity(message: str):
    msg = message.lower()

    if any(k in msg for k in ["injured", "trapped", "collapsed", "fire"]):
        return "HIGH"
    elif any(k in msg for k in ["help", "emergency"]):
        return "MEDIUM"
    else:
        return "LOW"


# ---------------- REVERSE GEOCODE ----------------
def reverse_geocode(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        headers = {"User-Agent": "SATLINK-EMERGENCY"}
        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()
        return data.get("display_name", "Unknown Location")
    except Exception:
        return "Unknown Location"


# ---------------- MAIN SOS FUNCTION ----------------
def send_sos(latitude: float, longitude: float, message: str):

    # IST Time
    ist = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(ist)

    severity = get_severity(message)
    location_name = reverse_geocode(latitude, longitude)

    sos_text = f"""
🚨 EMERGENCY SOS 🚨
Message: {message}
Severity: {severity}
Location: {location_name}
Map: https://maps.google.com/?q={latitude},{longitude}
Time (IST): {current_time}
"""

    # Simulated satellite send
    msg_id = send_message(sos_text, "RESCUE_CONTROL")

    os.makedirs("backend/logs", exist_ok=True)

    log_entry = {
        "time": str(current_time),
        "message": message,
        "severity": severity,
        "lat": latitude,
        "lon": longitude,
        "location": location_name,
        "transport": "Satellite-Simulation",
        "trigger": "MANUAL",
        "message_id": msg_id
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return msg_id
