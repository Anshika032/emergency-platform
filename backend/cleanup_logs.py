import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs", "sos_log.json")
IMAGE_DIR = os.path.join(BASE_DIR, "ai_images")

# ================= LOAD RAW CONTENT =================
with open(LOG_FILE, "r", encoding="utf-8") as f:
    content = f.read().strip()

raw_items = []

# Try normal JSON first
try:
    parsed = json.loads(content)
    raw_items = parsed if isinstance(parsed, list) else [parsed]
except Exception:
    # Fallback: JSON lines
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            raw_items.append(json.loads(line))
        except json.JSONDecodeError:
            pass

# ================= FLATTEN EVERYTHING =================
logs = []

def flatten(item):
    if isinstance(item, dict):
        logs.append(item)
    elif isinstance(item, list):
        for sub in item:
            flatten(sub)

for item in raw_items:
    flatten(item)

print(f"Loaded {len(logs)} flattened log entries")

# ================= CLEAN LOGS =================
cleaned_logs = []

for log in logs:
    if not isinstance(log, dict):
        continue

    img = log.get("image")
    if img:
        img_path = os.path.join(IMAGE_DIR, img)
        if os.path.exists(img_path):
            cleaned_logs.append(log)
    else:
        cleaned_logs.append(log)

# ================= SAVE CLEAN JSON =================
with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned_logs, f, indent=2)

print(f"✅ Cleanup complete. Final logs count: {len(cleaned_logs)}")
