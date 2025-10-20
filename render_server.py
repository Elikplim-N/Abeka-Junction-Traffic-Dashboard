#!/usr/bin/env python3
"""
Render deployment server - serves React frontend and proxies API calls
"""
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import json

FRONTEND_BUILD = Path(__file__).parent / "frontend" / "build"
# On Render, services communicate via onrender.com URLs
API_URL = os.getenv("API_URL", "http://traffic-dashboard-api.onrender.com")
PORT = int(os.getenv("PORT", 10000))

class RenderProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - proxy API or serve static files"""
        if self.path.startswith("/api/"):
            self.proxy_to_backend("GET")
        else:
            self.serve_static("GET")
    
    def do_POST(self):
        """Handle POST requests - proxy to backend"""
        if self.path.startswith("/api/"):
            self.proxy_to_backend("POST")
    
    def proxy_to_backend(self, method):
        """Forward request to backend API"""
        try:
            url = API_URL + self.path
            req = urllib.request.Request(url, method=method)
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    req.add_header(header, value)
            
            # Copy body for POST
            if method == "POST":
                content_length = int(self.headers.get('Content-Length', 0))
                req.data = self.rfile.read(content_length)
            
            response = urllib.request.urlopen(req, timeout=10)
            self.send_response(response.status)
            
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(f"Error: {e.reason}".encode())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Proxy error: {str(e)}".encode())
    
    def serve_static(self, method):
        """Serve static React files"""
        if method == "GET":
            # Redirect / to index.html
            if self.path == "/":
                self.path = "/index.html"
            
            os.chdir(FRONTEND_BUILD)
            try:
                super().do_GET()
            except Exception as e:
                # Fallback to index.html for SPA routing
                try:
                    with open(FRONTEND_BUILD / "index.html", "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(f.read())
                except:
                    self.send_response(404)
                    self.end_headers()

if __name__ == "__main__":
    os.chdir(FRONTEND_BUILD)
    server = HTTPServer(("0.0.0.0", PORT), RenderProxyHandler)
    print(f"🚀 Dashboard running on port {PORT}")
    print(f"📡 API proxy → {API_URL}")
    server.serve_forever()
