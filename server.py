#!/usr/bin/env python3
"""
Simple server to serve the React frontend and proxy API calls to backend
"""
import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.request
import urllib.error

FRONTEND_BUILD = Path(__file__).parent / "frontend" / "build"
BACKEND_URL = "http://localhost:8001"

class ProxyHandler(SimpleHTTPRequestHandler):
    def proxy_request(self, method):
        if self.path.startswith("/api/") or self.path.startswith("/ws"):
            try:
                url = BACKEND_URL + self.path
                req = urllib.request.Request(url, method=method)
                if method == "POST":
                    content_length = int(self.headers.get('Content-Length', 0))
                    req.data = self.rfile.read(content_length)
                response = urllib.request.urlopen(req, timeout=5)
                self.send_response(response.status)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.read())
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            os.chdir(FRONTEND_BUILD)
            if method == "GET":
                super().do_GET()
    
    def do_GET(self):
        self.proxy_request("GET")
    
    def do_POST(self):
        self.proxy_request("POST")
    
    def translate_path(self, path):
        """Translate to frontend build directory"""
        if path == "/":
            path = "/index.html"
        return super().translate_path(path)

if __name__ == "__main__":
    os.chdir(FRONTEND_BUILD)
    server = HTTPServer(("0.0.0.0", 3000), ProxyHandler)
    print(f"🚀 Dashboard running at http://localhost:3000")
    print(f"📡 API proxy → {BACKEND_URL}")
    server.serve_forever()
