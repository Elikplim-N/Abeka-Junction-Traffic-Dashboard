# Abeka Junction Traffic Dashboard - Installation Guide

## For End Users (Simple Installation)

### Step 1: Download
Download the installer file:
- **Abeka-Junction-Traffic-Dashboard-Setup.exe**

### Step 2: Run Installer
1. Double-click the `.exe` file
2. Click "Next" to proceed
3. Choose installation location (default is recommended)
4. Click "Install"
5. Wait for installation to complete

### Step 3: Launch Dashboard
After installation, you'll find:
- **Desktop Shortcut**: "Abeka Junction Traffic Dashboard"
- **Start Menu**: Abeka Junction → Traffic Dashboard

Click to launch! The dashboard opens automatically in your browser.

### Step 4: Connect Your Device
1. Connect your RFID sensor via USB
2. In the dashboard, select your port from the dropdown
3. Keep baud rate at **115200**
4. Click **Connect**
5. Watch real-time congestion predictions!

---

## System Requirements
- Windows 10 or Windows 11
- 2GB RAM minimum (4GB recommended)
- 300MB free disk space
- USB port for serial device
- Administrator rights (for serial port access)

---

## Features

### Real-Time Monitoring
- Live sensor data streaming
- Congestion level 0-100%
- Confidence ratings
- Status indicators (Free Flow, Light, Moderate, Heavy, Severe)

### Data Management
- Automatic database storage
- Historical data retention
- CSV export capabilities
- Daily statistics

### Smart Predictions
- Headway-time based analysis
- Next-minute predictions
- Traffic recommendations
- Trend analysis

---

## Usage Tips

### Export Data
Click the "Export Data" section in the sidebar:
- **📥 Readings CSV** - Raw sensor data
- **📥 Predictions CSV** - Congestion predictions
- **📥 All Data CSV** - Complete dataset

### Baud Rate Selection
Common rates available:
- 9600
- 19200
- 38400
- 57600
- **115200** (recommended for most devices)
- 230400
- 460800

### Changing Serial Port
1. Click "Disconnect"
2. Select new port from dropdown
3. Click "Connect"

---

## Troubleshooting

### Dashboard won't open
- Wait 10 seconds after launching
- Check if port 3000 is already in use
- Restart the application

### No serial ports showing
- Ensure USB device is connected
- Try different USB port
- Install device drivers if needed
- Run application as Administrator

### "Connection refused" error
- Make sure "Connect" button is clicked
- Verify baud rate matches your device
- Check USB cable connection

### Data not appearing
- Confirm device is transmitting data
- Check that serial connection shows "Connected"
- Verify JSON format from device
- Check browser console for errors (F12)

---

## Uninstallation

### Method 1: Control Panel (Recommended)
1. Open Windows Settings
2. Go to "Apps" → "Apps & Features"
3. Find "Abeka Junction Traffic Dashboard"
4. Click "Uninstall"
5. Confirm uninstallation

### Method 2: Start Menu
1. Click Start Menu
2. Find "Abeka Junction"
3. Right-click "Uninstall"
4. Confirm

### Method 3: Direct
- Go to installed location (usually `C:\Program Files\Abeka Junction Traffic Dashboard`)
- Run `uninstall.exe`

---

## Data Location

Your traffic data is stored in:
```
C:\Users\[YourUsername]\AppData\Local\Abeka Junction\traffic_data.db
```

This SQLite database contains:
- All sensor readings
- Predictions and statistics
- Searchable historical data

**Backup your data regularly!**

---

## Advanced Options

### Simulate Traffic Data
For testing/demonstration purposes, the system includes a traffic simulator.

Open Command Prompt in the installation directory and run:
```bash
python simulator.py --mode cycle
```

Simulation modes available:
- `--mode free` - Light traffic
- `--mode light` - Moderate traffic
- `--mode moderate` - Higher congestion
- `--mode heavy` - Heavy traffic
- `--mode severe` - Maximum congestion
- `--mode cycle` - Full cycle demo

---

## Getting Help

### Common Issues Checklist
- [ ] Device is connected via USB
- [ ] Application is running as Administrator
- [ ] Baud rate matches device (115200)
- [ ] Port is correctly selected
- [ ] No other application is using the port

### Contact Support
For issues or questions:
1. Check the troubleshooting section above
2. Review the README.md file
3. Consult the technical documentation

---

## License

**Abeka Junction Traffic Dashboard**
MIT License - Free to use and modify

---

**Version 1.0**
Last Updated: October 2025

Thank you for using Abeka Junction Traffic Dashboard!
