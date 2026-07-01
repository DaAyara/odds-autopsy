from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/api/reports':
            self.send_reports_list()
        elif self.path.startswith('/api/reports/'):
            filename = self.path.replace('/api/reports/', '')
            self.send_report(filename)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.end_headers()

    def send_reports_list(self):
        files = []
        if os.path.exists(REPORTS_DIR):
            for f in sorted(os.listdir(REPORTS_DIR)):
                if f.endswith('.json'):
                    files.append(f)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(files).encode())

    def send_report(self, filename):
        filepath = os.path.join(REPORTS_DIR, filename)
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            return
        with open(filepath, 'r') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data.encode())

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'Server running on port {port}')
    server.serve_forever()