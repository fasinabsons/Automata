@echo off
echo ========================================
echo   WiFi Automation - Full System Startup
echo   with 8-File Minimum Guarantee
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

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

:: Check if required files exist
if not exist "enhanced_service_runner_with_email.py" (
    echo WARNING: enhanced_service_runner_with_email.py not found
    echo Falling back to enhanced_service_runner.py
    set SERVICE_FILE=enhanced_service_runner.py
) else (
    echo Using enhanced service with email notifications + 8-file minimum
    set SERVICE_FILE=enhanced_service_runner_with_email.py
)

if not exist "package.json" (
    echo ERROR: package.json not found
    echo Please ensure you're in the correct directory
    echo.
    pause
    exit /b 1
)

:: Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo WARNING: Some Python dependencies may not have installed correctly
    echo.
)

:: Install Node.js dependencies
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install Node.js dependencies
        echo.
        pause
        exit /b 1
    )
) else (
    echo Node.js dependencies already installed
)

:: Create base directories only (dynamic folders will be created automatically)
echo Creating base directories for dynamic file management...
if not exist "logs" mkdir logs
if not exist "EHC_Data" mkdir EHC_Data
if not exist "EHC_Data_Merge" mkdir EHC_Data_Merge
if not exist "EHC_Data_Pdf" mkdir EHC_Data_Pdf
if not exist "downloads" mkdir downloads

:: Initialize dynamic file manager and check 8-file requirement
echo Initializing dynamic file manager and checking 8-file requirement...
python -c "from modules.dynamic_file_manager import DynamicFileManager; fm = DynamicFileManager(); status = fm.get_current_date_folder_status(); print(f'Today folder: {status[\"date_folder\"]}'); print(f'CSV files: {status[\"csv_count\"]}/8'); print('✅ Sufficient files for Excel generation' if status['csv_count'] >= 8 else f'⚠️ Need {8 - status[\"csv_count\"]} more files - Service will auto-download')"
if %errorLevel% neq 0 (
    echo WARNING: Dynamic file manager initialization failed
    echo System will create folders as needed
    echo.
)

:: Check Chrome installation
echo Checking Chrome installation...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Chrome may not be installed
    echo Please install Google Chrome for web scraping
    echo.
)

:: Start both services
echo.
echo ========================================
echo   Starting Full System with 8-File Minimum
echo ========================================
echo.
echo Starting Backend Service with 8-File Minimum...
echo Schedule: 09:30 AM, 13:00 PM (backup: 13:30 PM) - DAY ONLY
echo Dynamic Folders: Date-based folders created automatically (DDmonth format)
echo 8-File Minimum: Auto-download if insufficient files during business hours
echo.

:: Start backend in a new window
start "WiFi Automation Backend" cmd /c "python %SERVICE_FILE% & pause"

:: Wait a moment for backend to start
timeout /t 5 >nul

echo Starting Frontend Dashboard...
echo Dashboard will be available at: http://localhost:3000
echo.

:: Start frontend in a new window
start "WiFi Automation Frontend" cmd /c "npm run dev & pause"

:: Wait a moment for frontend to start
timeout /t 3 >nul

echo.
echo ========================================
echo   Full System Started
echo ========================================
echo.
echo Backend Service: Running in separate window
echo Frontend Dashboard: Running in separate window
echo.
echo Access the dashboard at: http://localhost:3000
echo.
echo System Features:
echo - Automatic WiFi data collection
echo - 8-File Minimum Guarantee (auto-download if needed)
echo - Excel file generation (triggered at 8 files)
echo - VBS integration
echo - Email notifications
echo - PDF report generation
echo - Web dashboard for monitoring
echo - Dynamic date-based folders (DDmonth format)
echo - Health monitoring every 5 minutes
echo.
echo 8-File Minimum Features:
echo - System ensures minimum 8 CSV files daily
echo - Auto-triggers downloads during business hours (9 AM - 5 PM)
echo - Health check monitors file count every 5 minutes
echo - Excel generation automatically triggered at 8 files
echo - Email notifications for all download activities
echo.
echo To stop the system:
echo 1. Close the backend window (or press Ctrl+C)
echo 2. Close the frontend window (or press Ctrl+C)
echo.
echo Log files are saved in: logs\wifi_automation.log
echo.
echo Press any key to open the dashboard in your browser...
pause >nul

:: Open dashboard in default browser
start http://localhost:3000

echo.
echo Dashboard opened in browser.
echo Keep this window open to monitor the system.
echo System will maintain minimum 8 files automatically.
echo.
pause 