import json
import os
from datetime import datetime

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '../../reports')

def save_report(report):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    fixture_id = report['fixture']['fixture_id']
    name = report['fixture']['name'].replace(' ', '_').replace('/', '_')
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{name}_{fixture_id}_{timestamp}.json"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved: {filepath}")
    return filepath

def load_all_reports():
    reports = []
    if not os.path.exists(REPORTS_DIR):
        return reports
    for filename in sorted(os.listdir(REPORTS_DIR)):
        if filename.endswith('.json'):
            filepath = os.path.join(REPORTS_DIR, filename)
            with open(filepath, 'r') as f:
                reports.append(json.load(f))
    return reports