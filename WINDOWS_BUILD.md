# Building for Windows

Complete guide to create a standalone Windows executable for Abeka Junction Traffic Dashboard.

## Prerequisites

1. **Python 3.8+** - Download from https://www.python.org
   - **IMPORTANT**: Check "Add Python to PATH" during installation
   
2. **Node.js & npm** - Download from https://nodejs.org
   - Choose LTS version
   
3. **Git** (optional) - For version control

## Build Steps

### Step 1: Install PyInstaller

Open Command Prompt and run:

```bash
pip install pyinstaller
```

### Step 2: Build React Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

This creates an optimized build in `frontend/build/`

### Step 3: Build Python Backend Executable

```bash
pyinstaller build_windows.spec --onefile
```

This creates `dist/Abeka-Junction-Traffic-Dashboard.exe`

### Step 4: Create Distribution Package

```bash
mkdir dist/Abeka-Junction-Dashboard
mkdir dist/Abeka-Junction-Dashboard/frontend
mkdir dist/Abeka-Junction-Dashboard/backend

REM Copy built files
xcopy frontend\build dist\Abeka-Junction-Dashboard\frontend\ /E
xcopy dist\Abeka-Junction-Traffic-Dashboard.exe dist\Abeka-Junction-Dashboard\backend\
xcopy start-dashboard.bat dist\Abeka-Junction-Dashboard\

REM Copy dependencies
xcopy backend\venv dist\Abeka-Junction-Dashboard\backend\venv\ /E
```

### Step 5: Create Windows Installer (Optional - Advanced)

Install NSIS:
```bash
pip install pyinstaller-hooks-contrib
choco install nsis  # or download from https://nsis.sourceforge.io
```

## Quick Start on Windows

### Method 1: Batch Script (Easy - Recommended)

1. Download the full project folder
2. Right-click `start-dashboard.bat`
3. Select "Run as administrator"
4. Dashboard opens automatically in browser

### Method 2: Manual

1. Open Command Prompt as Administrator
2. Navigate to project folder:
   ```bash
   cd path\to\traffic-dashboard
   ```
3. Start backend:
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. Open new Command Prompt and start frontend:
   ```bash
   cd frontend
   npm start
   ```
5. Open browser to `http://localhost:3000`

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Restart Command Prompt after installation

### "npm is not recognized"
- Restart Command Prompt after installing Node.js
- Or add Node.js to PATH manually

### Serial port not accessible
- Run as Administrator
- Install USB drivers for your serial device

### Port 8000 or 3000 already in use
- Kill existing processes:
  ```bash
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

## File Structure

```
Abeka-Junction-Dashboard/
├── backend/
│   ├── main.py
│   ├── serial_handler.py
│   ├── prediction_model.py
│   ├── database.py
│   ├── simulator.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── build/ (created after npm run build)
├── start-dashboard.bat
└── README.md
```

## Deployment

To distribute the system:

1. Create folder: `Abeka-Junction-Dashboard-Installer`
2. Copy all files from the structure above
3. Add `README.md` with installation instructions
4. Zip the folder
5. Share with users

Users only need:
- Windows 10/11
- Administrator rights (for serial port)
- No Python/Node.js installation required if using exe

## System Requirements

- **OS**: Windows 10/11
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 200MB free space
- **Serial Port**: USB (automatic detection)

## Features Included

✅ Real-time traffic sensor data streaming
✅ Live congestion prediction (0-100%)
✅ Historical data with SQLite database
✅ CSV export functionality
✅ Serial port auto-detection
✅ Configurable baud rates
✅ Beautiful web dashboard
✅ Responsive design (desktop/tablet)

## License

MIT License - Feel free to modify and distribute

---

For support, contact: [your contact info]
