@echo off
title Enhanced WiFi Automation Service with Email Notifications + 8-File Minimum
echo ========================================
echo   Enhanced WiFi Automation Service
echo   with Email Notifications + Dynamic Folders
echo   + 8-File Minimum Guarantee
echo ========================================
echo.
echo 🛡️ Crash prevention enabled
echo 🔄 Auto-restart enabled
echo 🏥 Health monitoring active
echo 📧 Email notifications enabled
echo 📁 Dynamic date-based folders (DDmonth format)
echo 📊 8-File Minimum: Auto-download if insufficient files
echo 📅 Schedule: 09:30 AM, 1:00 PM (backup: 1:30 PM) - DAY ONLY
echo 📨 Notifications sent to: faseenm@gmail.com
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Change to the automation directory
cd /d "%~dp0"

echo [INFO] Starting Enhanced WiFi Service with Dynamic File Management + 8-File Minimum...
echo [INFO] Directory: %CD%
echo [INFO] Time: %DATE% %TIME%
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "enhanced_service_runner.py" (
    echo ❌ ERROR: enhanced_service_runner.py not found
    echo Please ensure the file exists in the current directory
    pause
    exit /b 1
) else (
    echo ✅ Using enhanced service with dynamic file system + 8-file minimum
    set SERVICE_FILE=enhanced_service_runner.py
)

REM Install/update dependencies
echo [INFO] Installing/updating dependencies...
pip install -r requirements.txt >nul 2>&1

REM Create base directories only (dynamic folders will be created automatically)
if not exist "logs" mkdir logs
if not exist "EHC_Data" mkdir EHC_Data
if not exist "EHC_Data_Merge" mkdir EHC_Data_Merge
if not exist "EHC_Data_Pdf" mkdir EHC_Data_Pdf

echo [INFO] Base directories created. Dynamic date folders will be created automatically.

REM Initialize dynamic file manager to create today's folders and check file count
echo [INFO] Initializing dynamic file manager and checking 8-file requirement...
python -c "from modules.dynamic_file_manager import DynamicFileManager; fm = DynamicFileManager(); status = fm.get_current_date_folder_status(); print(f'Today folder: {status[\"date_folder\"]}'); print(f'CSV files: {status[\"csv_count\"]}/8'); print('✅ Sufficient files' if status['csv_count'] >= 8 else f'⚠️ Need {8 - status[\"csv_count\"]} more files - Service will auto-download')"

REM Start the enhanced service in minimized window
echo [INFO] Launching enhanced service with crash protection, dynamic folders, and 8-file minimum...
start /min "Enhanced WiFi Service" python %SERVICE_FILE%

echo [SUCCESS] Enhanced service started successfully!
echo.
echo [FEATURES ENABLED]
echo   ✅ Crash prevention and auto-restart
echo   ✅ Health monitoring every 5 minutes
echo   ✅ Windows startup integration
echo   ✅ Email notifications for all events
echo   ✅ Dynamic date-based folders (auto-created daily)
echo   ✅ 8-File Minimum: Auto-download if insufficient files
echo   ✅ Schedule: Morning 09:30 AM
echo   ✅ Schedule: Afternoon 13:00 PM (backup: 13:30 PM)
echo   ❌ Evening slots: DISABLED (day-only downloads)
echo   ✅ Excel generation after 8 files reached
echo   ✅ Background operation (survives PC lock)
echo   ✅ CSV file counting in current date folder
echo.
echo [8-FILE MINIMUM GUARANTEE]
echo   📊 System ensures minimum 8 CSV files daily
echo   🚀 Auto-triggers downloads if less than 8 files
echo   ⏰ Checks during business hours (9 AM - 5 PM)
echo   🔄 Health check every 5 minutes monitors file count
echo   📧 Email notifications for download activities
echo   ✅ Excel generation automatically triggered at 8 files
echo.
echo [DYNAMIC FOLDER SYSTEM]
echo   📁 Format: DDmonth (e.g., 06jul, 07jul, 15oct)
echo   📅 Created automatically at 12:00 AM daily
echo   📊 CSV counting checks today's folder, not yesterday's
echo   🧹 Monthly cleanup (2-month retention)
echo.
echo [EMAIL NOTIFICATIONS]
echo   📧 Recipient: faseenm@gmail.com
echo   📨 Download success/failure notifications
echo   📊 Excel generation notifications (8-file trigger)
echo   🚨 System crash alerts
echo   🏥 Health status updates
echo   🧹 Monthly cleanup notifications
echo   📊 8-file minimum enforcement notifications
echo.
echo [SUCCESS] You can safely close this window
echo [SUCCESS] The service will continue running with crash protection
echo [SUCCESS] Dynamic folders will be created automatically
echo [SUCCESS] System will ensure minimum 8 files are available
echo [SUCCESS] You will receive email notifications for all activities
echo.

REM Keep window open for 30 seconds to show status
timeout /t 30 /nobreak >nul

REM Optional: Minimize this window after showing status
REM exit 