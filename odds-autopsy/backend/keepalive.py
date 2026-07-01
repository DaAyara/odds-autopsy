import requests
import time

URL = "https://odds-autopsy-api.onrender.com/api/reports"

while True:
    try:
        r = requests.get(URL, timeout=10)
        print(f"Ping: {r.status_code}")
    except Exception as e:
        print(f"Ping failed: {e}")
    time.sleep(840)