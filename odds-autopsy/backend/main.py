import sys
import time
import os

sys.path.insert(0, os.path.dirname(__file__))

from fetcher import get_fixtures, get_odds_for_fixture_on_day, get_scores_for_fixture_on_day
from engine import run_autopsy
from report_builder import save_report

def run_for_fixture(fixture, epoch_day):
    fid = fixture.get('FixtureId')
    name = f"{fixture.get('Participant1')} vs {fixture.get('Participant2')}"
    print(f"Running autopsy for {name}...")

    odds = get_odds_for_fixture_on_day(fid, epoch_day)
    scores = get_scores_for_fixture_on_day(fid, epoch_day)

    if not odds:
        print(f"No odds data found for {name}, skipping.")
        return None

    fixture_info = {
        'fixture_id': fid,
        'name': name,
        'competition': fixture.get('Competition'),
        'epoch_day': epoch_day
    }

    report = run_autopsy(odds, scores, fixture_info)
    path = save_report(report)
    return path

if __name__ == "__main__":
    epoch_day = int(time.time() / 86400)
    fixtures = get_fixtures()

    target_ids = [18172280, 18175397]

    for f in fixtures:
        if f.get('FixtureId') in target_ids:
            run_for_fixture(f, epoch_day)