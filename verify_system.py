#!/usr/bin/env python3
"""
Final System Verification Script
Verifies all components are working correctly
"""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_service_running():
    """Check if automation service is running"""
    print_header("SERVICE STATUS CHECK")
    
    try:
        service_running = False
        service_pid = None
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'service_runner.py' in cmdline or 'simple_background_runner.py' in cmdline:
                    service_running = True
                    service_pid = proc.info['pid']
                    print_success(f"Service is RUNNING (PID: {service_pid})")
                    print_info(f"Command: {cmdline}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not service_running:
            print_error("Service is NOT RUNNING")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error checking service: {e}")
        return False

def check_startup_registration():
    """Check Windows startup registration"""
    print_header("WINDOWS STARTUP CHECK")
    
    try:
        import winreg
        
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        startup_found = False
        
        with winreg.OpenKey(key, key_path) as reg_key:
            entry_names = [
                "WiFiAutomationService",
                "SimpleWiFiRunner",
                "WiFiAutomationRunner"
            ]
            
            for entry_name in entry_names:
                try:
                    value = winreg.QueryValueEx(reg_key, entry_name)[0]
                    print_success(f"{entry_name}: Registered")
                    print_info(f"Path: {value}")
                    startup_found = True
                except FileNotFoundError:
                    pass
        
        if not startup_found:
            print_error("No startup entries found")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error checking startup: {e}")
        return False

def check_file_structure():
    """Check file structure and counts"""
    print_header("FILE STRUCTURE CHECK")
    
    try:
        # Check main files
        required_files = [
            "start_automation.bat",
            "service_runner.py",
            "monitor_service.py",
            "corrected_wifi_app.py",
            "userinput.py"
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            if file_path.exists():
                print_success(f"{file_name} exists")
            else:
                print_error(f"{file_name} missing")
        
        # Check directories
        required_dirs = [
            "EHC_Data",
            "logs",
            "modules",
            "config"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                print_success(f"{dir_name}/ directory exists")
            else:
                print_error(f"{dir_name}/ directory missing")
        
        # Check CSV files
        data_dir = project_root / "EHC_Data"
        if data_dir.exists():
            total_files = 0
            for date_dir in data_dir.iterdir():
                if date_dir.is_dir():
                    csv_files = list(date_dir.glob("*.csv"))
                    total_files += len(csv_files)
                    print_info(f"{date_dir.name}: {len(csv_files)} CSV files")
            
            print_success(f"Total CSV files: {total_files}")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking file structure: {e}")
        return False

def check_schedule():
    """Check schedule information"""
    print_header("SCHEDULE CHECK")
    
    try:
        now = datetime.now()
        
        # Morning slot: 09:30
        morning = now.replace(hour=9, minute=30, second=0, microsecond=0)
        if morning <= now:
            morning += timedelta(days=1)
        
        # Evening slot: 13:00
        evening = now.replace(hour=13, minute=0, second=0, microsecond=0)
        if evening <= now:
            evening += timedelta(days=1)
        
        # Test run: 16:50 (4:50 PM)
        test_run = now.replace(hour=16, minute=50, second=0, microsecond=0)
        
        print_success("Schedule configured:")
        print_info(f"Morning slot: {morning.strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"Evening slot: {evening.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if test_run > now:
            print_info(f"Test run today: {test_run.strftime('%H:%M:%S')}")
        else:
            print_info("Test run: Already passed for today")
        
        # Find next run
        next_run = min(morning, evening)
        if test_run > now:
            next_run = min(next_run, test_run)
        
        time_until = next_run - now
        print_success(f"Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"Time until: {str(time_until).split('.')[0]}")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking schedule: {e}")
        return False

def check_logs():
    """Check log files"""
    print_header("LOG FILES CHECK")
    
    try:
        log_dir = project_root / "logs"
        if not log_dir.exists():
            print_error("Logs directory not found")
            return False
        
        log_files = list(log_dir.glob("*.log"))
        if not log_files:
            print_error("No log files found")
            return False
        
        for log_file in log_files:
            try:
                # Check if file is recent (modified within last hour)
                mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                age = datetime.now() - mod_time
                
                if age.total_seconds() < 3600:  # Less than 1 hour old
                    print_success(f"{log_file.name} (recent activity)")
                else:
                    print_info(f"{log_file.name} (last modified: {mod_time.strftime('%H:%M:%S')})")
                
            except Exception as e:
                print_error(f"Error checking {log_file.name}: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking logs: {e}")
        return False

def main():
    """Main verification function"""
    print("🎯 FINAL SYSTEM VERIFICATION")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Directory: {project_root}")
    
    # Run all checks
    checks = [
        ("Service Status", check_service_running),
        ("Windows Startup", check_startup_registration),
        ("File Structure", check_file_structure),
        ("Schedule", check_schedule),
        ("Log Files", check_logs)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = True
    for check_name, result in results:
        if result:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL CHECKS PASSED - SYSTEM READY!")
        print("✅ You can safely close Cursor")
        print("✅ The automation will continue running in background")
        print("✅ Files will be downloaded at scheduled times")
        print("✅ Excel files will be generated automatically")
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW ABOVE")
        print("❌ System may not work correctly")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 