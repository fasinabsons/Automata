#!/usr/bin/env python3
"""
WiFi Automation Service Monitor
Monitors service status, logs, and file counts
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

from modules.dynamic_file_manager import DynamicFileManager

class ServiceMonitor:
    """Monitor for WiFi Automation Service"""
    
    def __init__(self):
        self.project_root = project_root
        self.log_dir = project_root / "logs"
        self.data_dir = project_root / "EHC_Data"
        self.file_manager = DynamicFileManager()
        self.merge_dir = project_root / "EHC_Data_Merge"
    
    def check_process_running(self):
        """Check if automation process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'simple_background_runner.py' in cmdline or 'service_runner.py' in cmdline:
                        return {
                            'running': True,
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {'running': False}
            
        except Exception as e:
            return {'running': False, 'error': str(e)}
    
    def get_file_counts(self):
        """Get CSV file counts by date"""
        try:
            file_counts = {}
            
            if self.data_dir.exists():
                for date_dir in self.data_dir.iterdir():
                    if date_dir.is_dir():
                        csv_files = list(date_dir.glob("*.csv"))
                        file_counts[date_dir.name] = len(csv_files)
            
            return file_counts
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_today_files(self):
        """Get today's file count using dynamic file manager"""
        try:
            today_folder = self.file_manager.get_date_folder_name()
            today_dir = self.data_dir / today_folder
            
            if today_dir.exists():
                csv_files = list(today_dir.glob("*.csv"))
                return {
                    'date': today_folder,
                    'count': len(csv_files),
                    'files': [f.name for f in csv_files]
                }
            else:
                return {
                    'date': today_folder,
                    'count': 0,
                    'files': []
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_latest_logs(self, lines=20):
        """Get latest log entries"""
        try:
            logs = {}
            
            # Check different log files
            log_files = [
                'simple_runner.log',
                'service_runner.log',
                'automation.log'
            ]
            
            for log_file in log_files:
                log_path = self.log_dir / log_file
                if log_path.exists():
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            all_lines = f.readlines()
                            latest_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                            logs[log_file] = [line.strip() for line in latest_lines]
                    except Exception as e:
                        logs[log_file] = [f"Error reading log: {e}"]
                else:
                    logs[log_file] = ["Log file not found"]
            
            return logs
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_startup_registration(self):
        """Check Windows startup registration"""
        try:
            import winreg
            
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            startup_entries = {}
            
            with winreg.OpenKey(key, key_path) as reg_key:
                # Check for different possible entries
                entry_names = [
                    "WiFiAutomationService",
                    "SimpleWiFiRunner",
                    "WiFiAutomationRunner"
                ]
                
                for entry_name in entry_names:
                    try:
                        value = winreg.QueryValueEx(reg_key, entry_name)[0]
                        startup_entries[entry_name] = value
                    except FileNotFoundError:
                        startup_entries[entry_name] = "Not found"
            
            return startup_entries
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_next_scheduled_time(self):
        """Get next scheduled run time"""
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
            
            # Find next run
            next_run = min(morning, evening)
            time_until = next_run - now
            
            return {
                'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S'),
                'time_until': str(time_until).split('.')[0]  # Remove microseconds
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def display_status(self):
        """Display comprehensive status"""
        print("🖥️  WiFi Automation Service Monitor")
        print("=" * 60)
        print()
        
        # Process status
        print("🔍 Process Status:")
        process_info = self.check_process_running()
        if process_info['running']:
            print(f"   ✅ Service is RUNNING (PID: {process_info['pid']})")
            print(f"   📝 Command: {process_info['cmdline']}")
        else:
            print("   ❌ Service is NOT RUNNING")
        print()
        
        # Startup registration
        print("🚀 Windows Startup:")
        startup_info = self.check_startup_registration()
        if 'error' in startup_info:
            print(f"   ❌ Error: {startup_info['error']}")
        else:
            for name, value in startup_info.items():
                if value != "Not found":
                    print(f"   ✅ {name}: Registered")
                else:
                    print(f"   ❌ {name}: Not found")
        print()
        
        # File counts
        print("📁 File Status:")
        today_files = self.get_today_files()
        if 'error' in today_files:
            print(f"   ❌ Error: {today_files['error']}")
        else:
            print(f"   📅 Today ({today_files['date']}): {today_files['count']} files")
            if today_files['count'] > 0:
                print(f"   📋 Files: {', '.join(today_files['files'][:5])}")
                if len(today_files['files']) > 5:
                    print(f"        ... and {len(today_files['files']) - 5} more")
        
        file_counts = self.get_file_counts()
        if 'error' not in file_counts:
            print(f"   📊 Total directories: {len(file_counts)}")
            total_files = sum(file_counts.values())
            print(f"   📈 Total files: {total_files}")
        print()
        
        # Schedule info
        print("⏰ Schedule Information:")
        schedule_info = self.get_next_scheduled_time()
        if 'error' in schedule_info:
            print(f"   ❌ Error: {schedule_info['error']}")
        else:
            print(f"   🕐 Next run: {schedule_info['next_run']}")
            print(f"   ⏳ Time until: {schedule_info['time_until']}")
        print()
        
        # Recent logs
        print("📋 Recent Logs (last 5 entries):")
        logs = self.get_latest_logs(5)
        if 'error' in logs:
            print(f"   ❌ Error: {logs['error']}")
        else:
            for log_file, entries in logs.items():
                if entries and entries != ["Log file not found"]:
                    print(f"   📝 {log_file}:")
                    for entry in entries[-3:]:  # Show last 3 entries
                        print(f"      {entry}")
        print()
    
    def monitor_live(self, interval=30):
        """Monitor service in real-time"""
        print("🔄 Live monitoring started (Ctrl+C to stop)")
        print(f"📊 Refreshing every {interval} seconds")
        print("=" * 60)
        
        try:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
                print(f"🕐 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                self.display_status()
                print(f"⏳ Next refresh in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

def main():
    """Main function"""
    monitor = ServiceMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            monitor.display_status()
        elif command == "live":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            monitor.monitor_live(interval)
        elif command == "files":
            today_files = monitor.get_today_files()
            file_counts = monitor.get_file_counts()
            print("📁 File Status:")
            print(f"Today: {today_files}")
            print(f"All dates: {file_counts}")
        elif command == "logs":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            logs = monitor.get_latest_logs(lines)
            for log_file, entries in logs.items():
                print(f"\n📝 {log_file}:")
                for entry in entries:
                    print(f"  {entry}")
        else:
            print("Usage: python monitor_service.py [status|live|files|logs] [options]")
            print("  status     - Show current status")
            print("  live [sec] - Live monitoring (default 30 sec)")
            print("  files      - Show file counts")
            print("  logs [num] - Show recent logs (default 20 lines)")
    else:
        monitor.display_status()

if __name__ == "__main__":
    main() 