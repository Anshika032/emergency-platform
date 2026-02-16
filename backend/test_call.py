import os
from dotenv import load_dotenv
from pathlib import Path

from satellite.twilio_adapter import make_voice_call

# 🔥 FORCE load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print("DEBUG SID =", os.getenv("TWILIO_SID"))
print("DEBUG TOKEN =", os.getenv("TWILIO_TOKEN"))
print("DEBUG NUMBER =", os.getenv("TWILIO_NUMBER"))

make_voice_call(
    os.getenv("EMERGENCY_NUMBER"),
    "This is a test emergency call from the Satlink system."
)
