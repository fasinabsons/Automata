#!/usr/bin/env python3
"""
Installation script for WiFi User Data Automation System
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_windows():
    """Check if running on Windows"""
    if platform.system() != "Windows":
        print("Warning: This system is designed for Windows. Some features may not work.")
    else:
        print("✓ Windows detected")

def install_requirements():
    """Install Python requirements"""
    try:
        print("Installing Python requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs",
        "downloads",
        "downloads/CSV_Downloads",
        "downloads/Merged_Files", 
        "downloads/Reports",
        "logs/screenshots"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_config_file():
    """Create configuration file"""
    config_content = """# WiFi Automation System Configuration
# Copy this to config.ini and modify as needed

[WiFi]
target_url = https://51.38.163.73:8443/wsg/
username = admin
password = AdminFlower@123
timeout = 30

[VBS]
primary_path = C:\\Users\\Lenovo\\Music\\moonflower\\AbsonsItERP.exe - Shortcut.lnk
fallback_path = \\\\192.168.10.16\\e\\ArabianLive\\ArabianLive_MoonFlower\\AbsonsItERP.exe
username = Vj
password = 

[Schedule]
slot1_time = 09:30
slot2_time = 13:00
slot3_time = 15:00
processing_time = 15:05
email_time = 09:00
restart_time = 01:00
"""
    
    config_file = Path("config.ini.example")
    with open(config_file, 'w') as f:
        f.write(config_content)
    print(f"✓ Created example configuration: {config_file}")

def create_service_scripts():
    """Create Windows service scripts"""
    
    # Batch file to start the system
    start_script = """@echo off
echo Starting WiFi Automation System...
cd /d "%~dp0"
python main.py
pause
"""
    
    with open("start_automation.bat", 'w') as f:
        f.write(start_script)
    print("✓ Created start_automation.bat")
    
    # Batch file to start API server
    api_script = """@echo off
echo Starting WiFi Automation API Server...
cd /d "%~dp0"
python api/flask_server.py
pause
"""
    
    with open("start_api.bat", 'w') as f:
        f.write(api_script)
    print("✓ Created start_api.bat")

def main():
    """Main installation function"""
    print("WiFi User Data Automation System - Installation")
    print("=" * 50)
    
    # Check system requirements
    check_python_version()
    check_windows()
    
    # Install dependencies
    install_requirements()
    
    # Setup directories and files
    create_directories()
    create_config_file()
    create_service_scripts()
    
    print("\n" + "=" * 50)
    print("Installation completed successfully!")
    print("\nNext steps:")
    print("1. Review and modify config.ini.example")
    print("2. Run 'python main.py --test web_scraping' to test web scraping")
    print("3. Run 'python main.py --test vbs_integration' to test VBS integration")
    print("4. Run 'start_automation.bat' to start the full system")
    print("5. Run 'start_api.bat' to start the API server")
    print("\nFor help, run: python main.py --help")

if __name__ == "__main__":
    main()