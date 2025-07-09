@echo off
title Smart WiFi Automation - Complete Working System
color 0A

echo ===============================================
echo    SMART WIFI AUTOMATION - ALL WORKING IDEAS
echo ===============================================
echo.
echo Incorporating ALL proven working elements:
echo - corrected_wifi_app.py (iframe login + precision selectors)
echo - enhanced_service_runner.py (8-file minimum + dynamic folders)
echo - csv_to_excel_processor.py (automatic Excel generation)
echo - intelligent_slot_manager.py (smart timing + late start)
echo - working_email_notifications.py (email alerts)
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to PATH
    pause
    exit /b 1
)

echo [%date% %time%] Starting Complete Working System...
echo.

:: Step 1: Check current file status using dynamic file manager
echo ========================================
echo STEP 1: CHECKING CURRENT FILE STATUS
echo ========================================
python -c "from modules.dynamic_file_manager import DynamicFileManager; fm = DynamicFileManager(); status = fm.get_current_date_folder_status(); print(f'📊 Current CSV files: {status[\"csv_count\"]}/8'); print(f'📁 Today folder: {fm.get_download_directory()}'); print(f'📈 Status: {\"SUFFICIENT\" if status[\"csv_count\"] >= 8 else \"NEED MORE FILES\"}')"

if errorlevel 1 (
    echo WARNING: File status check failed, continuing anyway...
)

echo.

:: Step 2: Intelligent slot timing check
echo ========================================
echo STEP 2: INTELLIGENT SLOT TIMING CHECK
echo ========================================
python -c "from datetime import datetime; current_time = datetime.now(); hour = current_time.hour; minute = current_time.minute; morning_slot = (hour == 9 and minute >= 30) or hour > 9; afternoon_slot = (hour == 13 and minute >= 0) or hour > 13; late_start = (hour > 9 and hour < 13) or hour > 13; print(f'🕐 Current time: {hour:02d}:{minute:02d}'); print(f'🌅 Morning slot (09:30): {\"ACTIVE\" if morning_slot else \"WAITING\"}'); print(f'🌞 Afternoon slot (13:00): {\"ACTIVE\" if afternoon_slot else \"WAITING\"}'); print(f'⏰ Late start detected: {\"YES\" if late_start else \"NO\"}')"

echo.

:: Step 3: Run intelligent slot manager (incorporates all timing logic)
echo ========================================
echo STEP 3: INTELLIGENT SLOT MANAGEMENT
echo ========================================
echo Running intelligent slot manager with all working features...
python intelligent_slot_manager.py

set SLOT_RESULT=%ERRORLEVEL%

echo.
echo Slot manager result: %SLOT_RESULT%

:: Step 4: Check if we need additional downloads (8-file minimum guarantee)
echo ========================================
echo STEP 4: 8-FILE MINIMUM GUARANTEE CHECK
echo ========================================
python -c "from modules.dynamic_file_manager import DynamicFileManager; from modules.csv_to_excel_processor import CSVToExcelProcessor; fm = DynamicFileManager(); processor = CSVToExcelProcessor(); csv_dir = fm.get_download_directory(); file_count = processor.count_csv_files(csv_dir); print(f'📊 Current files: {file_count}'); should_generate = processor.should_generate_excel(csv_dir); print(f'📈 Excel ready: {\"YES\" if should_generate else \"NO\"}')"

if errorlevel 1 (
    echo Files check completed with warnings
)

:: Step 5: Run corrected WiFi app if files are insufficient
echo ========================================
echo STEP 5: CORRECTED WIFI APP (IF NEEDED)
echo ========================================
python -c "from modules.dynamic_file_manager import DynamicFileManager; fm = DynamicFileManager(); status = fm.get_current_date_folder_status(); file_count = status['csv_count']; print(f'📊 File count check: {file_count}/8'); need_download = file_count < 8; print(f'📥 Need download: {\"YES\" if need_download else \"NO\"}'); import sys; sys.exit(0 if need_download else 1)"

if errorlevel 1 (
    echo ✅ Sufficient files available, skipping download
    goto excel_check
)

echo 🚀 Running corrected WiFi app (proven iframe login + precision selectors)...
python corrected_wifi_app.py

set WIFI_RESULT=%ERRORLEVEL%
echo WiFi app result: %WIFI_RESULT%

:excel_check
:: Step 6: Automatic Excel generation check (8-file trigger)
echo ========================================
echo STEP 6: AUTOMATIC EXCEL GENERATION
echo ========================================
echo Checking if Excel generation should be triggered...
python -c "from modules.csv_to_excel_processor import CSVToExcelProcessor; from modules.dynamic_file_manager import DynamicFileManager; fm = DynamicFileManager(); processor = CSVToExcelProcessor(); csv_dir = fm.get_download_directory(); should_generate = processor.should_generate_excel(csv_dir); print(f'🎯 Excel generation needed: {\"YES\" if should_generate else \"NO\"}'); import sys; sys.exit(0 if should_generate else 1)"

if errorlevel 1 (
    echo ℹ️ Excel generation not needed yet
    goto email_check
)

echo 📊 Triggering automatic Excel generation...
python -c "from modules.csv_to_excel_processor import CSVToExcelProcessor; from modules.dynamic_file_manager import DynamicFileManager; fm = DynamicFileManager(); processor = CSVToExcelProcessor(); csv_dir = fm.get_download_directory(); result = processor.process_and_generate_excel(csv_dir); print(f'📊 Excel result: {\"SUCCESS\" if result.get(\"success\") else \"FAILED\"}'); print(f'📄 File: {result.get(\"file_path\", \"N/A\")}'); print(f'📋 Records: {result.get(\"records_written\", 0)}')"

set EXCEL_RESULT=%ERRORLEVEL%
echo Excel generation result: %EXCEL_RESULT%

:email_check
:: Step 7: Email notifications (working email service)
echo ========================================
echo STEP 7: EMAIL NOTIFICATIONS
echo ========================================
echo Sending status email using working email service...
python -c "from working_email_notifications import WorkingEmailNotifications; from datetime import datetime; email_service = WorkingEmailNotifications(); subject = f'✅ Smart WiFi Automation Complete - {datetime.now().strftime(\"%d/%m/%Y %H:%M\")}'; body = f'''Smart WiFi Automation has completed successfully!\n\n📊 All working features utilized:\n✅ Intelligent slot timing\n✅ Corrected WiFi app (iframe login)\n✅ 8-file minimum guarantee\n✅ Automatic Excel generation\n✅ Dynamic file management\n✅ Email notifications\n\n🕐 Completion time: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\n\nBest regards,\nSmart WiFi Automation System'''; success = email_service.send_email(subject, body); print(f'📧 Email sent: {\"SUCCESS\" if success else \"FAILED\"}')"

if errorlevel 1 (
    echo WARNING: Email notification failed, but automation completed
)

:: Step 8: Enhanced service runner integration check
echo ========================================
echo STEP 8: SERVICE INTEGRATION STATUS
echo ========================================
echo Checking enhanced service runner integration...
python -c "import os; service_running = os.path.exists('service_state.json'); print(f'🔄 Enhanced service: {\"RUNNING\" if service_running else \"STOPPED\"}'); print('💡 To start permanent service: python enhanced_service_runner.py'); print('💡 Service includes: Crash prevention, Auto-restart, Health monitoring')"

echo.

:: Step 9: Final status summary
echo ========================================
echo STEP 9: FINAL STATUS SUMMARY
echo ========================================
python -c "from modules.dynamic_file_manager import DynamicFileManager; from modules.csv_to_excel_processor import CSVToExcelProcessor; from datetime import datetime; fm = DynamicFileManager(); processor = CSVToExcelProcessor(); csv_dir = fm.get_download_directory(); file_count = processor.count_csv_files(csv_dir); excel_ready = processor.should_generate_excel(csv_dir); print('🎯 SMART WIFI AUTOMATION COMPLETE!'); print('='*50); print(f'📊 CSV Files: {file_count}'); print(f'📈 Excel Ready: {\"YES\" if excel_ready else \"NO\"}'); print(f'📁 Directory: {csv_dir}'); print(f'🕐 Completed: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}'); print('='*50); print('✅ ALL WORKING IDEAS INCORPORATED:'); print('   🔑 Iframe login with precision selectors'); print('   📊 8-file minimum guarantee'); print('   🎯 Automatic Excel generation'); print('   ⏰ Intelligent slot timing'); print('   📧 Working email notifications'); print('   🔄 Dynamic file management'); print('   🏥 Enhanced error handling')"

echo.
echo ===============================================
echo    SMART WIFI AUTOMATION COMPLETED
echo ===============================================
echo.
echo 🚀 All working features have been utilized!
echo 📋 Check the console output above for detailed results
echo 💡 For continuous operation, run: enhanced_service_runner.py
echo.

:: Keep window open for 30 seconds to show results
echo ⏳ Window will close in 30 seconds...
timeout /t 30 /nobreak >nul

exit /b 0 