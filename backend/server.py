"""Loopback API and website host. Start: python backend/server.py"""
import argparse
import json
import sqlite3
import sys
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from core import answer, validate

ROOT = Path(__file__).resolve().parents[1]


class Store:
    def __init__(self, path):
        self.path = path
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS readings(device TEXT, stamp TEXT, body TEXT, PRIMARY KEY(device,stamp))')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        try:
            with db:
                yield db
        finally:
            db.close()

    def put(self, item):
        with self.connect() as db:
            previous = db.execute('SELECT body FROM readings WHERE device=? AND stamp=?', (item['device_id'],item['timestamp'])).fetchone()
            if previous and json.loads(previous[0]) != item:
                raise ValueError('Conflicting duplicate timestamp')
            db.execute('INSERT OR IGNORE INTO readings VALUES(?,?,?)', (item['device_id'],item['timestamp'],json.dumps(item)))
        return previous is None

    def latest(self):
        with self.connect() as db:
            rows = db.execute('SELECT body FROM readings WHERE device=? ORDER BY stamp DESC LIMIT 60', ('website-synthetic-demo',)).fetchall()
        return list(reversed([json.loads(row[0]) for row in rows]))


class Handler(SimpleHTTPRequestHandler):
    store = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'docs'), **kwargs)

    def send_json(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/demo':
            return self.send_json(200, {'source': 'Local SQLite', 'synthetic': True, 'readings': self.store.latest()})
        if path == '/api/health':
            return self.send_json(200, {'status': 'ok', 'storage': 'SQLite', 'synthetic_only': True})
        if path.startswith('/api/'):
            return self.send_json(404, {'error': 'Unknown endpoint'})
        return super().do_GET()

    def do_POST(self):
        host = self.headers.get('Host', '')
        if host not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
            return self.send_json(403, {'error': 'Invalid host'})
        origin = self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):
            return self.send_json(403, {'error': 'Cross-origin writes blocked'})
        path = urlparse(self.path).path
        if path not in ['/api/readings', '/api/analyze']:
            return self.send_json(404, {'error': 'Unknown endpoint'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 8192:
                return self.send_json(413, {'error': 'Body must be 1..8192 bytes'})
            if self.headers.get_content_type() != 'application/json':
                return self.send_json(415, {'error': 'JSON required'})
            body = json.loads(self.rfile.read(size))
            if path == '/api/readings':
                item = validate(body)
                if item['device_id'] != 'website-synthetic-demo':
                    raise ValueError('Reserved demonstration device required')
                created = self.store.put(item)
                return self.send_json(201 if created else 200, {'reading': item, 'created': created})
            if not isinstance(body, dict):
                raise ValueError('JSON object required')
            return self.send_json(200, answer(body.get('question'), self.store.latest()))
        except (ValueError, TypeError, UnicodeError):
            return self.send_json(400, {'error': 'Invalid JSON, reading, duplicate, or question'})
        except Exception:
            return self.send_json(503, {'error': 'Service temporarily unavailable'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8877)
    parser.add_argument('--db', default=str(ROOT / '.local' / 'readings.db'))
    args = parser.parse_args()
    Path(args.db).resolve().parent.mkdir(parents=True, exist_ok=True)
    Handler.store = Store(args.db)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Pulse local API: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
