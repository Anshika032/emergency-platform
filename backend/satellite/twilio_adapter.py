def send_message(text: str, to_number: str):
    print("\n=== SATELLITE LINK (SIMULATED) ===")
    print("Recipient:", to_number)
    print(text)
    print("=== MESSAGE TRANSMITTED ===\n")

    return "SIMULATED_SATELLITE_MSG"
# backend/satellite/twilio_adapter.py
from twilio.rest import Client
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

def make_voice_call(to_number, message):
    call = client.calls.create(
        to=to_number,
        from_=TWILIO_NUMBER,
        twiml=f"""
        <Response>
            <Say voice="alice" language="en-IN">
                {message}
            </Say>
        </Response>
        """
    )
    return call.sid
