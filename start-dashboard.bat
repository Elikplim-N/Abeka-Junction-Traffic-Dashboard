@echo off
REM Abeka Junction Traffic Congestion Prediction Dashboard
REM Windows Startup Script

setlocal enabledelayedexpansion

echo ========================================
echo  Abeka Junction Traffic Dashboard
echo  Real-time Congestion Prediction System
echo ========================================
echo.

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0

REM Check if running as admin (for serial port access)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Please run this as Administrator for full serial port access
    echo.
)

REM Start Backend Server
echo [1/2] Starting Backend Server...
cd /d "%SCRIPT_DIR%backend"
start "Abeka Junction - Backend" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak

REM Start Frontend
echo [2/2] Starting Frontend...
cd /d "%SCRIPT_DIR%frontend"
start "Abeka Junction - Frontend" cmd /k "npm start"

REM Wait and open browser
timeout /t 8 /nobreak
echo.
echo ========================================
echo Opening Dashboard in browser...
echo ========================================
start http://localhost:3000

echo.
echo Dashboard is ready!
echo.
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:3000
echo.
echo Keep both windows open. Close them to stop the dashboard.
pause
