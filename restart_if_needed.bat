@echo off
echo Checking WiFi Automation Status...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if %ERRORLEVEL% NEQ 0 (
    echo WiFi Automation not running. Restarting system...
    shutdown /r /t 30 /c "WiFi Automation restart - System will restart in 30 seconds"
) else (
    echo WiFi Automation is running normally.
) 