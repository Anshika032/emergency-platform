from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime
import os
import time

from backend.utils.sos_logger import append_log
from backend.satellite.twilio_adapter import make_voice_call



EMERGENCY_NUMBER = os.getenv("EMERGENCY_NUMBER")

# ===================== ROUTER =====================
router = APIRouter()

# ===================== PATHS =====================
IMAGE_DIR = "backend/ai_alerts"
os.makedirs(IMAGE_DIR, exist_ok=True)

# ===================== CALL COOLDOWN =====================
LAST_CALL_TIME = 0
CALL_COOLDOWN = 300  # 5 minutes

# ===================== AI ALERT ENDPOINT =====================
@router.post("/ai-alert")
async def receive_ai_alert(
    event_type: str = Form(...),
    confidence: float = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    image: UploadFile = File(None)
):
    global LAST_CALL_TIME

    image_filename = None

    # ---------- SAVE IMAGE ----------
    if image:
        image_filename = (
            f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        save_path = os.path.join(IMAGE_DIR, image_filename)

        with open(save_path, "wb") as f:
            f.write(await image.read())

    # ---------- SEVERITY LOGIC ----------
    if event_type in ["fire", "collapse"] and confidence >= 0.7:
        severity = "HIGH"
    elif confidence >= 0.4:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # ---------- EVENT OBJECT ----------
    event = {
        "time": datetime.now().isoformat(),
        "message": f"AI Detected {event_type.upper()}",
        "severity": severity,
        "lat": float(lat),
        "lon": float(lon),
        "image": image_filename,
        "event_type": event_type,
        "confidence": round(confidence, 3),
        "transport": "Satellite-Simulation",
        "source": "AI-CAMERA"
    }

    # ---------- LOG EVENT ----------
    append_log(event)
    print("🚨 AI ALERT RECEIVED:", event)

    # ===================== AUTO VOICE CALL =====================
    if severity == "HIGH" and EMERGENCY_NUMBER:
        now = time.time()

        if now - LAST_CALL_TIME > CALL_COOLDOWN:
            try:
                voice_message = (
    f"This is an emergency alert. "
    f"{event_type} has been detected. "
    f"Severity is high. "
    f"Please respond immediately."
)


                make_voice_call(EMERGENCY_NUMBER, voice_message)

                LAST_CALL_TIME = now
                print(f"📞 Emergency call placed to {EMERGENCY_NUMBER}")

            except Exception as e:
                print("❌ Failed to place emergency call:", e)
        else:
            print("⏳ Call skipped due to cooldown")

    # ---------- RESPONSE ----------
    return {
        "status": "AI ALERT RECEIVED",
        "event": event
    }
