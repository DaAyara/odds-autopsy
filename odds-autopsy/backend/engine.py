import json
from datetime import datetime

def decimal_odds(price):
    return round(price / 1000, 3)

def find_shifts(odds_updates, min_shift=0.05):
    grouped = {}
    for update in odds_updates:
        key = update.get('SuperOddsType') + '_' + str(update.get('MarketParameters', ''))
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(update)

    shifts = []
    for market, updates in grouped.items():
        updates_sorted = sorted(updates, key=lambda x: x.get('Ts', 0))
        for i in range(1, len(updates_sorted)):
            prev = updates_sorted[i - 1]
            curr = updates_sorted[i]
            prev_prices = prev.get('Prices', [])
            curr_prices = curr.get('Prices', [])
            if not prev_prices or not curr_prices:
                continue
            if len(prev_prices) != len(curr_prices):
                continue
            for j in range(len(prev_prices)):
                prev_dec = decimal_odds(prev_prices[j])
                curr_dec = decimal_odds(curr_prices[j])
                if prev_dec == 0:
                    continue
                shift = abs(curr_dec - prev_dec)
                if shift >= min_shift:
                    price_names = curr.get('PriceNames', [])
                    label = price_names[j] if j < len(price_names) else f"price_{j}"
                    shifts.append({
                        'ts': curr.get('Ts'),
                        'time_readable': datetime.utcfromtimestamp(curr.get('Ts', 0) / 1000).strftime('%H:%M:%S'),
                        'market': curr.get('SuperOddsType'),
                        'parameters': curr.get('MarketParameters'),
                        'in_running': curr.get('InRunning', False),
                        'label': label,
                        'from_odds': prev_dec,
                        'to_odds': curr_dec,
                        'shift': round(curr_dec - prev_dec, 3),
                        'abs_shift': round(shift, 3)
                    })

    shifts_sorted = sorted(shifts, key=lambda x: x['abs_shift'], reverse=True)
    return shifts_sorted

def map_shifts_to_events(shifts, score_updates):
    events = []
    for s in score_updates:
        ts = s.get('Ts')
        if not ts:
            continue
        clock = s.get('Clock', {})
        score = s.get('Score', {})
        events.append({
            'ts': ts,
            'time_readable': datetime.utcfromtimestamp(ts / 1000).strftime('%H:%M:%S'),
            'status_id': s.get('StatusId'),
            'game_state': s.get('GameState'),
            'clock_seconds': clock.get('Seconds') if clock else None,
            'score': score
        })

    annotated = []
    for shift in shifts:
        shift_ts = shift['ts']
        nearest_event = None
        nearest_gap = float('inf')
        for event in events:
            gap = abs(shift_ts - event['ts'])
            if gap < nearest_gap:
                nearest_gap = gap
                nearest_event = event
        entry = dict(shift)
        gap_seconds = round(nearest_gap / 1000, 1)
        entry['nearest_event_gap_seconds'] = None if gap_seconds == float('inf') else gap_seconds
        entry['nearest_event'] = nearest_event
        annotated.append(entry)

    return annotated

def run_autopsy(odds_updates, score_updates, fixture_info):
    shifts = find_shifts(odds_updates, min_shift=0.05)
    annotated = map_shifts_to_events(shifts, score_updates)
    top_shifts = annotated[:20]

    report = {
        'fixture': fixture_info,
        'total_odds_updates': len(odds_updates),
        'total_score_updates': len(score_updates),
        'total_shifts_detected': len(shifts),
        'top_20_shifts': top_shifts
    }

    return report