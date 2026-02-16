import json
import os
import tempfile
from typing import Dict

# =====================================================
# BASE PATHS
# =====================================================
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

LOG_FILE = os.path.join(BASE_DIR, "logs", "sos_log.json")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# =====================================================
# APPEND LOG (ATOMIC + SAFE)
# =====================================================
def append_log(event: Dict):
    """
    Safely append a new SOS / AI event to sos_log.json
    - Atomic write (no corruption on reload)
    - Newest event always on top
    """

    if not isinstance(event, dict):
        return

    logs = []

    # -------------------------------------------------
    # 1️⃣ READ EXISTING LOGS
    # -------------------------------------------------
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    logs = data
        except json.JSONDecodeError:
            logs = []
        except Exception as e:
            print("⚠️ Failed to read sos_log.json:", e)
            logs = []

    # -------------------------------------------------
    # 2️⃣ INSERT NEW LOG AT TOP
    # -------------------------------------------------
    logs.insert(0, event)

    # -------------------------------------------------
    # 3️⃣ ATOMIC WRITE (CRASH / RELOAD SAFE)
    # -------------------------------------------------
    dir_name = os.path.dirname(LOG_FILE)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=dir_name,
        delete=False
    ) as tmp:
        json.dump(logs, tmp, indent=2)
        temp_path = tmp.name

    os.replace(temp_path, LOG_FILE)
