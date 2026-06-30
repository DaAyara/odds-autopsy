import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

BASE_URL = os.getenv("TXLINE_BASE_URL", "https://txline.txodds.com")
JWT = os.getenv("TXLINE_JWT")
API_TOKEN = os.getenv("TXLINE_API_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {JWT}",
    "X-Api-Token": API_TOKEN
}

def get_fixtures():
    url = f"{BASE_URL}/api/fixtures/snapshot"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_odds_history(fixture_id):
    url = f"{BASE_URL}/api/odds/snapshot/{fixture_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_scores_history(fixture_id):
    url = f"{BASE_URL}/api/scores/snapshot/{fixture_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_odds_for_fixture_on_day(fixture_id, epoch_day):
    all_odds = []
    for hour in range(0, 24):
        url = f"{BASE_URL}/api/odds/updates/{epoch_day}/{hour}/0"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                matches = [x for x in data if x.get('FixtureId') == fixture_id]
                all_odds.extend(matches)
        except Exception as e:
            print(f"Hour {hour} failed: {e}")
            continue
    return all_odds

def get_scores_for_fixture_on_day(fixture_id, epoch_day):
    all_scores = []
    for hour in range(0, 24):
        url = f"{BASE_URL}/api/scores/updates/{epoch_day}/{hour}/0"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                matches = [x for x in data if x.get('FixtureId') == fixture_id]
                all_scores.extend(matches)
        except Exception as e:
            print(f"Hour {hour} failed: {e}")
            continue
    return all_scores

if __name__ == "__main__":
    print("Fetching fixtures...")
    fixtures = get_fixtures()
    print(f"Found {len(fixtures)} fixtures")
    for f in fixtures[:5]:
        print(f" - {f.get('Participant1')} vs {f.get('Participant2')} | id: {f.get('FixtureId')} | competition: {f.get('Competition')}")