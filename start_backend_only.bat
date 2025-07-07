@echo off
echo ========================================
echo   WiFi Automation - Backend Only
echo ========================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Set the working directory
cd /d "%~dp0"
echo Working directory: %cd%
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    echo.
    pause
    exit /b 1
)

:: Check if required files exist
if not exist "enhanced_service_runner.py" (
    echo ERROR: enhanced_service_runner.py not found
    echo Please ensure you're in the correct directory
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo Please ensure you're in the correct directory
    echo.
    pause
    exit /b 1
)

:: Install/update dependencies
echo Installing/updating Python dependencies...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo WARNING: Some dependencies may not have installed correctly
    echo.
)

:: Create necessary directories
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "EHC_Data" mkdir EHC_Data
if not exist "EHC_Data_Merge" mkdir EHC_Data_Merge
if not exist "EHC_Data_Pdf" mkdir EHC_Data_Pdf
if not exist "downloads" mkdir downloads

:: Check Chrome installation
echo Checking Chrome installation...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Chrome may not be installed
    echo Please install Google Chrome for web scraping
    echo.
)

:: Start the backend service
echo.
echo ========================================
echo   Starting Backend Service
echo ========================================
echo.
echo Service will run with the following schedule:
echo - Morning: 09:30 AM (backup: 09:30 AM if fails)
echo - Afternoon: 13:00 PM (backup: 13:30 PM if fails)
echo - Evening: 21:05 PM (backup: 21:11 PM if fails)
echo.
echo Press Ctrl+C to stop the service
echo.

:: Start the enhanced service runner
python enhanced_service_runner.py

:: If the service exits, show status
echo.
echo ========================================
echo   Backend Service Stopped
echo ========================================
echo.
echo Service has stopped. Check logs for details.
echo Log file: logs\wifi_automation.log
echo.
pause 