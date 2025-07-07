@echo off
title WiFi Automation Service Starter
echo ========================================
echo    WiFi Automation Service Starter
echo ========================================
echo.

REM Change to the automation directory
cd /d "%~dp0"

echo [INFO] Starting WiFi Automation Service...
echo [INFO] Directory: %CD%
echo [INFO] Time: %DATE% %TIME%
echo.

REM Start the enhanced service runner in minimized window
echo [INFO] Launching WiFi Automation Service...
start /min "WiFi Automation Service" python service_runner.py

echo [INFO] Background service started successfully!
echo [INFO] The automation will run at:
echo        - Morning: 09:30 AM
echo        - Evening: 1:00 PM (13:00)
echo.
echo [INFO] Service is now running in background...
echo [INFO] Check logs folder for operation status
echo.
echo [SUCCESS] You can safely close this window
echo [SUCCESS] The automation will continue running
echo.

REM Keep window open for 10 seconds to show status
timeout /t 10 /nobreak >nul

REM Optional: Minimize this window after showing status
REM exit 