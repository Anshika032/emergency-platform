# from dotenv import load_dotenv
# load_dotenv()
import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import requests
import os
import json
from datetime import datetime

from backend.satellite.sos_service import send_sos
from backend.ai_event_receiver import router as ai_event_router
from backend.utils.sos_logger import append_log, LOG_FILE

# =====================================================
# APP INITIALIZATION (ONLY ONCE)
# =====================================================
app = FastAPI(title="Satellite SOS Messaging System")

# =====================================================
# CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# STATIC FILES (AI IMAGES)
# URL → http://127.0.0.1:8000/ai-images/<filename>
# =====================================================
app.mount(
    "/ai-images",
    StaticFiles(directory="backend/ai_alerts"),
    name="ai-images"
)

# =====================================================
# ROUTERS
# =====================================================
app.include_router(ai_event_router)

# =====================================================
# MANUAL SOS
# =====================================================
@app.post("/sos")
def trigger_sos(lat: float, lon: float, msg: str = "Manual SOS Triggered"):
    # Send SOS via satellite simulation
    send_sos(lat, lon, msg)

    event = {
        "time": datetime.now().isoformat(),
        "message": msg,
        "event_type": "manual",
        "confidence": 1.0,
        "severity": "LOW",

        # unified coordinates
        "lat": lat,
        "lon": lon,

        "image": None,
        "transport": "Satellite-Simulation",
        "source": "MANUAL"
    }

    append_log(event)

    return {
        "status": "SOS SENT",
        "source": "MANUAL",
        "lat": lat,
        "lon": lon
    }

# =====================================================
# SOS LOGS
# =====================================================
@app.get("/sos_logs")
def get_sos_logs():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print("❌ Failed to read SOS logs:", e)
        return []

# =====================================================
# EXPORT LOGS
# =====================================================
@app.get("/export_logs")
def export_logs():
    return FileResponse(
        LOG_FILE,
        filename="sos_report.json",
        media_type="application/json"
    )

# =====================================================
# WEATHER
# =====================================================
WEATHER_API_KEY = "8e06b630f01305f30899651ce183be38"

@app.get("/weather")
def get_weather(lat: float, lon: float):
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        )

        response = requests.get(url, timeout=5)
        data = response.json()

        if "weather" not in data:
            return {
                "condition": "UNKNOWN",
                "description": data.get("message", "Weather data unavailable"),
                "temperature_c": "--",
                "wind_speed": "--",
                "alert": "WEATHER DATA UNAVAILABLE"
            }

        return {
            "location": data.get("name", "Selected Area"),
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "temperature_c": data["main"]["temp"],
            "wind_speed": data["wind"]["speed"],
            "alert": "NORMAL"
        }

    except Exception as e:
        return {
            "condition": "ERROR",
            "description": str(e),
            "temperature_c": "--",
            "wind_speed": "--",
            "alert": "WEATHER SERVICE DOWN"
        }