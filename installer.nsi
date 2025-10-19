; Abeka Junction Traffic Dashboard Installer
; NSIS Installer Script

!include "MUI2.nsh"
!include "x64.nsh"

; General settings
Name "Abeka Junction Traffic Dashboard"
OutFile "Abeka-Junction-Traffic-Dashboard-Setup.exe"
InstallDir "$PROGRAMFILES\Abeka Junction Traffic Dashboard"
InstallDirRegKey HKLM "Software\Abeka Junction" "Install_Dir"

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy all files
  File /r "backend\*.*"
  File /r "frontend\build\*.*"
  File "start-dashboard.bat"
  File "README.md"
  File "WINDOWS_BUILD.md"
  
  ; Create shortcuts
  SetOutPath "$INSTDIR"
  CreateDirectory "$SMPROGRAMS\Abeka Junction"
  CreateShortCut "$SMPROGRAMS\Abeka Junction\Traffic Dashboard.lnk" "$INSTDIR\start-dashboard.bat" "" "$INSTDIR\frontend\public\favicon.ico"
  CreateShortCut "$SMPROGRAMS\Abeka Junction\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortCut "$DESKTOP\Abeka Junction Traffic Dashboard.lnk" "$INSTDIR\start-dashboard.bat"
  
  ; Write registry
  WriteRegStr HKLM "Software\Abeka Junction" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Abeka Junction" "DisplayName" "Abeka Junction Traffic Dashboard"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Abeka Junction" "UninstallString" "$INSTDIR\uninstall.exe"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove files
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  RMDir /r "$SMPROGRAMS\Abeka Junction"
  Delete "$DESKTOP\Abeka Junction Traffic Dashboard.lnk"
  
  ; Remove registry
  DeleteRegKey HKLM "Software\Abeka Junction"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Abeka Junction"
SectionEnd
