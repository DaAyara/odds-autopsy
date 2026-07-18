import sys
import time
import os
import json
import requests

sys.path.insert(0, os.path.dirname(__file__))

from fetcher import HEADERS, BASE_URL, get_odds_for_fixture_on_day, get_scores_for_fixture_on_day
from engine import run_autopsy
from report_builder import save_report, load_all_reports
from anchor import anchor_report

KEYPAIR_PATH = os.path.join(os.path.dirname(__file__), '../../wallet.json')

KNOWN_FIXTURES = {
    18179763: {'name': 'Portugal vs Croatia', 'epoch_day': 20637},
    18179552: {'name': 'Switzerland vs Algeria', 'epoch_day': 20637},
    18172379: {'name': 'USA vs Bosnia and Herzegovina', 'epoch_day': 20636},
    18179551: {'name': 'Spain vs Austria', 'epoch_day': 20636},
    18179759: {'name': 'Mexico vs Ecuador', 'epoch_day': 20635},
    18179764: {'name': 'England vs Congo DR', 'epoch_day': 20635},
    18179550: {'name': 'Belgium vs Senegal', 'epoch_day': 20635},
    18175981: {'name': 'France vs Sweden', 'epoch_day': 20634},
    18172469: {'name': 'Germany vs Paraguay', 'epoch_day': 20633},
    18175983: {'name': 'Brazil vs Japan', 'epoch_day': 20633},
    18175918: {'name': 'Argentina vs Cape Verde', 'epoch_day': 20637},
    18176123: {'name': 'Australia vs Egypt', 'epoch_day': 20637},
    18179549: {'name': 'Colombia vs Ghana', 'epoch_day': 20638},
    18185036: {'name': 'Canada vs Morocco', 'epoch_day': 20638},
    18188721: {'name': 'Paraguay vs France', 'epoch_day': 20638},
    18187298: {'name': 'Brazil vs Norway', 'epoch_day': 20639},
    18192996: {'name': 'Mexico vs England', 'epoch_day': 20640},
    18193785: {'name': 'USA vs Belgium', 'epoch_day': 20641},
    18198205: {'name': 'Portugal vs Spain', 'epoch_day': 20640},
    18218149: {'name': 'Spain vs Belgium', 'epoch_day': 20644},
    18213979: {'name': 'Norway vs England', 'epoch_day': 20645},
    18222446: {'name': 'Argentina vs Switzerland', 'epoch_day': 20646},
    18172280: {'name': 'Netherlands vs Morocco', 'epoch_day': 20634},
    18175397: {'name': 'Ivory Coast vs Norway', 'epoch_day': 20634},
    18202701: {'name': 'Switzerland vs Colombia', 'epoch_day': 20641},
    18202783: {'name': 'Argentina vs Egypt', 'epoch_day': 20641},
    18209181: {'name': 'France vs Morocco', 'epoch_day': 20643},
    18237038: {'name': 'France vs Spain', 'epoch_day': 20648},
    18241006: {'name': 'England vs Argentina', 'epoch_day': 20649},
    18257865: {'name': 'France vs England', 'epoch_day': 20652},
    18257739: {'name': 'Spain vs Argentina', 'epoch_day': 20653},
}

def get_reported_ids():
    reports = load_all_reports()
    return set(r['fixture']['fixture_id'] for r in reports)

def run_for_fixture(fid, name, epoch_day):
    print(f"Processing {name} (day {epoch_day})...")

    odds = get_odds_for_fixture_on_day(fid, epoch_day)
    if not odds:
        print(f"  No odds data, skipping")
        return

    scores = get_scores_for_fixture_on_day(fid, epoch_day)

    fixture_info = {
        'fixture_id': fid,
        'name': name,
        'competition': 'World Cup',
        'epoch_day': epoch_day
    }

    report = run_autopsy(odds, scores, fixture_info)
    filepath = save_report(report)

    with open(filepath, 'r') as f:
        saved = json.load(f)

    result = anchor_report(saved, KEYPAIR_PATH)
    if result:
        saved['solana'] = result
        with open(filepath, 'w') as f:
            json.dump(saved, f, indent=2)
        print(f"  Anchored: {result['signature'][:20]}...")

    print(f"  Done: {name}")
    print()

if __name__ == "__main__":
    reported_ids = get_reported_ids()
    print(f"Already reported: {len(reported_ids)}")
    print()

    for fid, info in KNOWN_FIXTURES.items():
        if fid in reported_ids:
            print(f"Skipping already reported: {info['name']}")
            continue
        run_for_fixture(fid, info['name'], info['epoch_day'])