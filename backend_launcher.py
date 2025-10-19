#!/usr/bin/env python3
"""
Abeka Junction Traffic Dashboard - Linux App Launcher
Starts backend, frontend server, and opens dashboard in browser
"""
import subprocess
import time
import webbrowser
import os
import signal
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_BUILD = PROJECT_ROOT / "frontend" / "build"
PORT = 3000

def signal_handler(sig, frame):
    print("\n✓ Shutting down dashboard...")
    os.system("pkill -f 'uvicorn main:app'")
    os.system("pkill -f 'python server.py'")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("🚀 Starting Abeka Junction Traffic Dashboard...")

# Start backend
print("📡 Starting backend server...")
backend_proc = subprocess.Popen(
    ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
    cwd=BACKEND_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(2)

# Start frontend server
print("🎨 Starting frontend server...")
server_proc = subprocess.Popen(
    ["python", "server.py"],
    cwd=PROJECT_ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(2)

# Open browser
print(f"🌐 Opening dashboard at http://localhost:{PORT}")
webbrowser.open(f"http://localhost:{PORT}")

print("\n✅ Dashboard is running!")
print(f"📍 Access at: http://localhost:{PORT}")
print("🛑 Press Ctrl+C to stop\n")

try:
    backend_proc.wait()
except KeyboardInterrupt:
    signal_handler(None, None)
