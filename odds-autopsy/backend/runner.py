import time
import os
import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from fetcher import get_fixtures, get_scores_for_fixture_on_day, get_odds_for_fixture_on_day
from engine import run_autopsy
from report_builder import save_report, load_all_reports
from anchor import anchor_report

KEYPAIR_PATH = os.path.join(os.path.dirname(__file__), '../../wallet.json')
CHECK_INTERVAL = 1800

def get_finished_fixture_ids():
    fixtures = get_fixtures()
    finished = []
    for f in fixtures:
        fid = f.get('FixtureId')
        epoch_day = int(time.time() / 86400)
        scores = get_scores_for_fixture_on_day(fid, epoch_day)
        for s in scores:
            state = s.get('GameState', '')
            if state in ['finished', 'complete', 'ended', 'ft', 'post']:
                finished.append(f)
                break
    return finished

def get_already_reported_ids():
    reports = load_all_reports()
    return set(r['fixture']['fixture_id'] for r in reports)

def run_once():
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Checking for finished matches...")
    epoch_day = int(time.time() / 86400)

    try:
        fixtures = get_fixtures()
    except Exception as e:
        print(f"Failed to fetch fixtures: {e}")
        return

    reported_ids = get_already_reported_ids()

    for f in fixtures:
        fid = f.get('FixtureId')
        name = f"{f.get('Participant1')} vs {f.get('Participant2')}"
        competition = f.get('Competition', '')

        if competition != 'World Cup':
            continue

        if fid in reported_ids:
            print(f"  Already reported: {name}")
            continue

        scores = get_scores_for_fixture_on_day(fid, epoch_day)
        is_finished = any(
            s.get('GameState') in ['finished', 'complete', 'ended', 'ft', 'post']
            for s in scores
        )

        if not is_finished:
            print(f"  Not finished yet: {name}")
            continue

        print(f"  New finished match: {name}, running autopsy...")

        try:
            odds = get_odds_for_fixture_on_day(fid, epoch_day)
            if not odds:
                print(f"  No odds data for {name}, skipping")
                continue

            fixture_info = {
                'fixture_id': fid,
                'name': name,
                'competition': competition,
                'epoch_day': epoch_day
            }

            report = run_autopsy(odds, scores, fixture_info)
            filepath = save_report(report)

            with open(filepath, 'r') as file:
                saved = json.load(file)

            result = anchor_report(saved, KEYPAIR_PATH)
            if result:
                saved['solana'] = result
                with open(filepath, 'w') as file:
                    json.dump(saved, file, indent=2)
                print(f"  Anchored on Solana: {result['signature'][:20]}...")

            print(f"  Done: {name}")

        except Exception as e:
            print(f"  Error processing {name}: {e}")

def main():
    print("Odds Autopsy runner started")
    print(f"Checking every {CHECK_INTERVAL // 60} minutes")
    print()
    while True:
        run_once()
        print(f"Next check in {CHECK_INTERVAL // 60} minutes")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()