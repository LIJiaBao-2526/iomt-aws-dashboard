"""Assigned owner: CHAN Ka Ming. Synthetic device HTTP publisher, never a physical sensor."""
import argparse
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone

SCENARIOS = {'normal': [73,75,74,77,76,79,78,76,80,79,77,78],
             'high': [76,78,81,85,94,104,109,112,116,120,118,121]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', choices=SCENARIOS, default='normal')
    parser.add_argument('--interval', type=float, default=0, help='Delay between sends; 0 replays historical samples')
    parser.add_argument('--base-url', default='http://127.0.0.1:8877')
    args = parser.parse_args()
    if args.interval < 0:
        parser.error('interval must be nonnegative')
    if not args.base_url.startswith(('http://127.0.0.1:', 'http://localhost:')):
        parser.error('This publisher is restricted to the local prototype')
    rates = SCENARIOS[args.scenario]
    start = datetime.now(timezone.utc) - timedelta(minutes=len(rates)-1) if not args.interval else datetime.now(timezone.utc)
    for i, rate in enumerate(rates):
        stamp = start + timedelta(minutes=i) if not args.interval else datetime.now(timezone.utc)
        body = {'device_id': 'website-synthetic-demo', 'timestamp': stamp.isoformat(), 'heart_rate': rate, 'synthetic': True}
        req = urllib.request.Request(args.base_url+'/api/readings', data=json.dumps(body).encode(), headers={'Content-Type':'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=10) as res:
            print(res.status, rate, 'bpm', stamp.isoformat())
        if args.interval and i < len(rates)-1:
            time.sleep(args.interval)


if __name__ == '__main__':
    main()
