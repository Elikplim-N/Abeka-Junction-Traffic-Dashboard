# Deployment Guide - Abeka Junction Traffic Dashboard

## Complete Packaging & Distribution Guide

---

## Building the Installer

### Prerequisites on Build Machine
- Windows 10/11
- Python 3.8+ (with pip)
- Node.js & npm (LTS version)
- NSIS Installer (https://nsis.sourceforge.io)
- Git (optional)

### Step 1: Install Build Tools
```powershell
# Run PowerShell as Administrator

# Install NSIS
choco install nsis  # If using Chocolatey
# Or download manually from https://nsis.sourceforge.io

# Install PyInstaller
pip install pyinstaller
```

### Step 2: Build Installer
```powershell
# Navigate to project directory
cd "C:\Path\To\traffic-dashboard"

# Run the build script (as Administrator)
.\build-installer.ps1
```

### Step 3: Output
The script creates:
- `Abeka-Junction-Traffic-Dashboard-Setup.exe` (Installer)
- Size: ~150-200 MB
- Ready to distribute!

---

## Distribution Methods

### Method 1: Direct Download Link
Host the `.exe` file on:
- GitHub Releases
- Google Drive
- Dropbox
- AWS S3
- Your company website

**Recommended**: GitHub Releases for version control

### Method 2: Windows Store / Microsoft Store
Submit for official store distribution (advanced)

### Method 3: USB or Email
Package the `.exe` and distribute via:
- USB drives
- Email
- Shared network drives

---

## Installation by End Users

### Step 1: Download
User downloads `Abeka-Junction-Traffic-Dashboard-Setup.exe`

### Step 2: Run Installer
1. Double-click the `.exe`
2. Click "Next"
3. Accept license
4. Choose install location
5. Click "Install"
6. Wait ~2-3 minutes

### Step 3: Post-Installation
- Desktop shortcut created
- Start Menu entry created
- System registry updated
- Uninstaller created

### Step 4: First Launch
Click desktop shortcut → Dashboard opens in browser

---

## Technical Details

### What Gets Installed

```
C:\Program Files\Abeka Junction Traffic Dashboard\
├── backend/
│   ├── Abeka-Junction-Traffic-Dashboard.exe (Backend server)
│   ├── traffic_data.db (SQLite database - created on first run)
│   └── [Python dependencies bundled]
├── frontend/
│   ├── index.html
│   ├── static/
│   └── [Built React app - optimized]
├── start-dashboard.bat (Launcher)
├── README.md
└── INSTALL.md
```

### System Changes
1. **Start Menu** → "Abeka Junction" folder with shortcuts
2. **Desktop** → "Abeka Junction Traffic Dashboard" shortcut
3. **Registry** → Version tracking and uninstaller registration
4. **AppData** → Database location (if user changes default)

### Uninstallation
- Removes all files
- Removes Start Menu entries
- Removes desktop shortcut
- Removes registry entries
- **Does NOT** remove user data (database) unless explicitly chosen

---

## Versioning & Updates

### Version Format
`Abeka-Junction-Traffic-Dashboard-v1.0.0-Setup.exe`

### Update Strategy

**Option 1: Full Reinstall**
- User uninstalls old version
- User installs new version
- Data persists (in database)

**Option 2: Patch Delivery**
- Provide update script
- Update specific files only
- Faster than full reinstall

### Version Control
Keep releases at: `releases/v1.0.0/`

---

## Verification Checklist

Before distributing, verify:

- [ ] Application launches without errors
- [ ] Serial ports are detected correctly
- [ ] Dashboard displays without issues
- [ ] Export features work (CSV generation)
- [ ] Database creates successfully
- [ ] Uninstaller works properly
- [ ] All shortcuts work
- [ ] Documentation is included
- [ ] File size is reasonable (~150-200 MB)
- [ ] No hardcoded paths or localhost restrictions

---

## Troubleshooting Installation Issues

### "Windows protected your PC" warning
- Click "More info"
- Click "Run anyway"
- This is normal for unsigned executables (cost ~$300/year to avoid)

### Installation fails with "Permission denied"
- Run installer as Administrator
- Disable antivirus temporarily
- Try different installation directory

### "Python not found" after installation
- Python is bundled in the exe
- No external Python needed
- If error persists, reinstall

### Application won't start
- Run `start-dashboard.bat` manually
- Check Windows Event Viewer for errors
- Ensure port 8000 and 3000 are free

---

## Security Considerations

### Code Signing (Optional)
To remove "untrusted publisher" warning:
- Purchase code signing certificate (~$200-400/year)
- Sign the exe before distribution
- Improves user trust and professionalism

### Firewall
Dashboard runs locally on:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- No internet access required

### Data Protection
- Database stored in user's AppData
- No cloud sync by default
- Users must backup their data

---

## Performance Optimization

### Installer Size
Current size: ~150-200 MB

To reduce:
- Remove unused node modules
- Minify frontend code (already done)
- Strip debug symbols from exe

### Installation Time
Typical: 2-3 minutes on SSD

Factors:
- Disk speed
- System load
- Antivirus scanning

---

## Support & Maintenance

### Support Channels
1. Email support
2. GitHub Issues
3. Knowledge base
4. Video tutorials

### Maintenance Schedule
- Monthly bug fixes
- Quarterly feature updates
- Annual major releases

### Log Files
User can collect logs from:
- `C:\Users\[User]\AppData\Local\Abeka Junction\logs\`
- `C:\Program Files\Abeka Junction Traffic Dashboard\logs\`

---

## Distribution Checklist

Before releasing, ensure:

```
Setup Files
- [ ] Abeka-Junction-Traffic-Dashboard-Setup.exe (tested)
- [ ] Installer file is digitally signed (optional)
- [ ] Virus scanned (upload to VirusTotal)
- [ ] File integrity verified

Documentation
- [ ] INSTALL.md (included in installer)
- [ ] README.md (included in project)
- [ ] WINDOWS_BUILD.md (for developers)
- [ ] This DEPLOYMENT.md (for administrators)

Quality Assurance
- [ ] Tested on Windows 10 clean install
- [ ] Tested on Windows 11 clean install
- [ ] All features verified
- [ ] Export functionality working
- [ ] Database operations tested

Deployment
- [ ] Version tagged in git
- [ ] Release notes prepared
- [ ] Download link ready
- [ ] User documentation available
```

---

## License & Legal

Include in distribution:

**MIT License** - Free for personal and commercial use

```
MIT License

Copyright (c) 2025 Abeka Junction

Permission is hereby granted, free of charge...
[Full license text]
```

---

**Ready to deploy!**

Your Abeka Junction Traffic Dashboard is ready for professional distribution.

Questions? Refer to INSTALL.md for end users or README.md for technical details.
