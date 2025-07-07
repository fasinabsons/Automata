@echo off
echo ========================================
echo   WiFi Automation - Frontend Dashboard
echo ========================================
echo.

:: Set the working directory
cd /d "%~dp0"
echo Working directory: %cd%
echo.

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

:: Check if npm is installed
npm --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: npm is not installed or not in PATH
    echo Please install Node.js which includes npm
    echo.
    pause
    exit /b 1
)

:: Check if package.json exists
if not exist "package.json" (
    echo ERROR: package.json not found
    echo Please ensure you're in the correct directory
    echo.
    pause
    exit /b 1
)

:: Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install dependencies
        echo.
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed
)

:: Check if backend is running
echo Checking if backend is running...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Backend service may not be running
    echo Please start the backend service first using start_backend_only.bat
    echo The frontend will still start but may not function correctly
    echo.
    timeout /t 3 >nul
)

:: Start the frontend development server
echo.
echo ========================================
echo   Starting Frontend Dashboard
echo ========================================
echo.
echo Dashboard will be available at: http://localhost:3000
echo.
echo Features available:
echo - System status monitoring
echo - Folder configuration
echo - Download history
echo - Email notification status
echo - Schedule management
echo.
echo Press Ctrl+C to stop the frontend
echo.

:: Start the development server
npm run dev

:: If the service exits, show status
echo.
echo ========================================
echo   Frontend Dashboard Stopped
echo ========================================
echo.
echo Frontend has stopped.
echo.
pause 