#!/usr/bin/env python3
"""
WiFi Automation Service Runner
Runs like Windows service (AnyDesk/Print Spooler style)
Handles CSV downloads, Excel merging, and background operation
"""

import os
import sys
import time
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import schedule
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from corrected_wifi_app import CorrectedWiFiApp

class WiFiAutomationService:
    """Main WiFi Automation Service like Windows service"""
    
    def __init__(self):
        self.running = False
        self.setup_logging()
        self.setup_components()
        self.daily_files_downloaded = 0
        self.excel_generated_today = False
        
        self.logger.info("🚀 WiFi Automation Service initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "service_runner.log"
        
        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("WiFiService")
    
    def setup_components(self):
        """Initialize components"""
        self.logger.info("🔧 Initializing components...")
        
        try:
            # Initialize WiFi automation
            self.wifi_app = CorrectedWiFiApp()
            self.logger.info("✅ WiFi automation ready")
            
            self.logger.info("✅ All components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    def add_to_startup(self):
        """Add to Windows startup"""
        try:
            import winreg
            
            # Get current script directory and batch file
            batch_file = project_root / "start_automation.bat"
            
            # Registry key for startup
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Add batch file to startup
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(
                    reg_key,
                    "WiFiAutomationService",
                    0,
                    winreg.REG_SZ,
                    f'"{batch_file}"'
                )
            
            self.logger.info("✅ Added to Windows startup (batch file)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add to startup: {e}")
            return False
    
    def run_wifi_download(self, slot_name="scheduled"):
        """Run WiFi download and track daily progress"""
        self.logger.info(f"🔄 Starting WiFi download - {slot_name}")
        
        try:
            # Run WiFi automation
            result = self.wifi_app.run_corrected_automation()
            
            if result.get('success', False):
                files_downloaded = result.get('files_downloaded', 0)
                self.daily_files_downloaded += files_downloaded
                
                self.logger.info(f"✅ WiFi download completed: {files_downloaded} files downloaded")
                self.logger.info(f"📊 Daily total so far: {self.daily_files_downloaded} files")
                
                # Check if we have 8 files (2 slots completed)
                if self.daily_files_downloaded >= 8 and not self.excel_generated_today:
                    self.logger.info("🎯 Daily target reached (8+ files), triggering Excel generation...")
                    self.generate_excel_file()
                
                return True
            else:
                self.logger.error(f"❌ WiFi download failed for {slot_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ WiFi download error: {e}")
            return False
    
    def generate_excel_file(self):
        """Generate Excel file from downloaded CSV files"""
        self.logger.info("📊 Starting Excel file generation...")
        
        try:
            # Import Excel generator
            from modules.excel_generator import ExcelGenerator
            excel_generator = ExcelGenerator()
            
            # Generate Excel file
            result = excel_generator.create_excel_from_csv_files()
            
            if result.get('success', False):
                excel_file = result.get('excel_file')
                unique_records = result.get('unique_records', 0)
                
                self.logger.info(f"✅ Excel file generated: {excel_file}")
                self.logger.info(f"📊 Records processed: {unique_records}")
                
                self.excel_generated_today = True
                return True
            else:
                self.logger.error("❌ Excel generation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Excel generation error: {e}")
            return False
    
    def reset_daily_counters(self):
        """Reset daily counters at midnight"""
        self.logger.info("🔄 Resetting daily counters...")
        self.daily_files_downloaded = 0
        self.excel_generated_today = False
        self.logger.info("✅ Daily counters reset")
    
    def schedule_tasks(self):
        """Schedule the automation tasks"""
        self.logger.info("🕐 Scheduling tasks...")
        
        # Schedule morning slot (09:30)
        schedule.every().day.at("09:30").do(self.run_wifi_download, "morning")
        
        # Schedule evening slot (13:00)
        schedule.every().day.at("13:00").do(self.run_wifi_download, "evening")
        
        # Schedule daily reset at midnight
        schedule.every().day.at("00:00").do(self.reset_daily_counters)
        
        self.logger.info("✅ Tasks scheduled:")
        self.logger.info("   🌅 Morning slot: 09:30")
        self.logger.info("   🌆 Evening slot: 13:00")
        self.logger.info("   🔄 Daily reset: 00:00")
    
    def schedule_test_run(self, test_time: str):
        """Schedule a test run at specific time"""
        self.logger.info(f"🧪 Scheduling test run at {test_time}")
        
        try:
            # Parse time (format: HH:MM)
            test_hour, test_minute = test_time.split(":")
            current_time = datetime.now()
            test_datetime = current_time.replace(hour=int(test_hour), minute=int(test_minute), second=0, microsecond=0)
            
            # If test time is in the past today, schedule for tomorrow
            if test_datetime <= current_time:
                test_datetime += timedelta(days=1)
            
            self.logger.info(f"🕐 Test run scheduled for: {test_datetime}")
            
            # Schedule the test
            schedule.every().day.at(test_time).do(self.run_wifi_download, "test").tag('test')
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule test: {e}")
            return False
    
    def start_service(self):
        """Start the service like Windows service"""
        self.logger.info("🚀 Starting WiFi Automation Service...")
        
        try:
            self.running = True
            
            # Add to startup
            self.add_to_startup()
            
            # Schedule regular tasks
            self.schedule_tasks()
            
            # Schedule test run for 4:50 PM if requested
            current_time = datetime.now()
            if current_time.hour < 16 or (current_time.hour == 16 and current_time.minute < 50):
                self.schedule_test_run("16:50")
                self.logger.info("🧪 Test run scheduled for 4:50 PM today")
            
            self.logger.info("✅ Service started successfully")
            self.logger.info("🔄 Running like Windows service (AnyDesk/Print Spooler style)")
            self.logger.info("🔒 Will work even when PC is locked")
            self.logger.info("📅 Daily downloads: 09:30 AM and 1:00 PM")
            self.logger.info("📊 Excel generation: After 8 files downloaded")
            
            # Service main loop
            while self.running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Received stop signal")
            self.stop_service()
        except Exception as e:
            self.logger.error(f"❌ Service error: {e}")
            raise
    
    def stop_service(self):
        """Stop the service"""
        self.logger.info("🛑 Stopping WiFi Automation Service...")
        self.running = False
        self.logger.info("✅ Service stopped")
    
    def get_service_status(self):
        """Get current service status"""
        status = {
            "running": self.running,
            "daily_files": self.daily_files_downloaded,
            "excel_generated": self.excel_generated_today,
            "scheduled_jobs": len(schedule.jobs),
            "next_run": str(schedule.next_run()) if schedule.jobs else "No jobs scheduled"
        }
        
        self.logger.info(f"📊 Service Status: {status}")
        return status

def main():
    """Main function"""
    print("🚀 WiFi Automation Service")
    print("=" * 50)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        service = WiFiAutomationService()
        
        if command == "test":
            print("🧪 Running test download...")
            result = service.run_wifi_download("test")
            if result:
                print("✅ Test download completed successfully")
            else:
                print("❌ Test download failed")
            return
        
        elif command == "test-schedule":
            print("🕐 Starting service with test schedule...")
            service.schedule_test_run("16:50")
            service.start_service()
            return
        
        elif command == "add-startup":
            print("📝 Adding to Windows startup...")
            if service.add_to_startup():
                print("✅ Added to Windows startup successfully")
            else:
                print("❌ Failed to add to startup")
            return
        
        elif command == "status":
            print("📊 Getting service status...")
            status = service.get_service_status()
            for key, value in status.items():
                print(f"   {key}: {value}")
            return
        
        elif command == "excel":
            print("📊 Generating Excel file...")
            result = service.generate_excel_file()
            if result:
                print("✅ Excel generation completed")
            else:
                print("❌ Excel generation failed")
            return
        
        else:
            print("Usage: python service_runner.py [test|test-schedule|add-startup|status|excel]")
            return
    
    # Default - start the service
    service = WiFiAutomationService()
    
    print("🔄 Starting service...")
    print("Service will run like Windows service (AnyDesk/Print Spooler)")
    print("Press Ctrl+C to stop")
    print("")
    
    try:
        service.start_service()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        service.stop_service()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        service.stop_service()

if __name__ == "__main__":
    main() 