import requests

def reverse_geocode(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        headers = {
            "User-Agent": "satlink-emergency-platform"
        }

        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()

        return data.get("display_name", "Unknown Location")
    except Exception:
        return "Unknown Location"
