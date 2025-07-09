#!/usr/bin/env python3
"""
Comprehensive WiFi Automation Runner
Runs automation in background, works when PC is locked
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

from modules.advanced_scheduler import AdvancedScheduler
from corrected_wifi_app import CorrectedWiFiApp
from modules.excel_generator import ExcelGenerator

class WiFiAutomationRunner:
    """Main automation runner"""
    
    def __init__(self):
        self.running = False
        self.scheduler = None
        self.setup_logging()
        self.setup_components()
        
        self.logger.info("🚀 WiFi Automation Runner initialized")
    
    def setup_logging(self):
        """Setup logging"""
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "automation_runner.log"
        
        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("AutomationRunner")
    
    def setup_components(self):
        """Initialize components"""
        self.logger.info("🔧 Initializing components...")
        
        try:
            # Initialize WiFi automation
            self.wifi_app = CorrectedWiFiApp()
            self.logger.info("✅ WiFi automation ready")
            
            # Initialize Excel generator
            self.excel_generator = ExcelGenerator()
            self.logger.info("✅ Excel generator ready")
            
            self.logger.info("✅ All components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    def add_to_startup(self):
        """Add to Windows startup"""
        try:
            import winreg
            
            # Get current script path
            script_path = sys.executable
            startup_args = f'"{__file__}"'
            
            # Registry key for startup
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Add to startup
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(
                    reg_key,
                    "WiFiAutomationRunner",
                    0,
                    winreg.REG_SZ,
                    f'"{script_path}" {startup_args}'
                )
            
            self.logger.info("✅ Added to Windows startup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add to startup: {e}")
            return False
    
    def remove_from_startup(self):
        """Remove from Windows startup"""
        try:
            import winreg
            
            # Registry key for startup
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Remove from startup
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, "WiFiAutomationRunner")
            
            self.logger.info("✅ Removed from Windows startup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove from startup: {e}")
            return False
    
    def wifi_download_callback(self, slot_name: str):
        """WiFi download callback"""
        self.logger.info(f"🔄 Starting WiFi download - {slot_name} slot")
        
        try:
            # Run WiFi automation
            result = self.wifi_app.run_robust_automation()
            
            if result.get('success', False):
                files_downloaded = result.get('files_downloaded', 0)
                self.logger.info(f"✅ WiFi download completed: {files_downloaded} files downloaded")
                return True
            else:
                self.logger.error(f"❌ WiFi download failed for {slot_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ WiFi download error: {e}")
            return False
    
    def merge_callback(self):
        """Excel merge callback"""
        self.logger.info("🔄 Starting Excel merge")
        
        try:
            # Generate Excel file
            excel_result = self.excel_generator.create_excel_from_csv_files()
            
            if excel_result.get('success', False):
                excel_file = excel_result.get('excel_file')
                self.logger.info(f"✅ Excel file generated: {excel_file}")
                return True
            else:
                self.logger.error("❌ Excel generation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Excel merge error: {e}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler"""
        self.logger.info("🕐 Starting scheduler...")
        
        try:
            # Create scheduler
            self.scheduler = AdvancedScheduler(
                slot_1_time="09:30",
                slot_2_time="13:00",
                merge_delay_minutes=5,
                wifi_callback=self.wifi_download_callback,
                merge_callback=self.merge_callback
            )
            
            # Start scheduler in background thread
            scheduler_thread = threading.Thread(target=self.scheduler.start_scheduler, daemon=True)
            scheduler_thread.start()
            
            self.logger.info("✅ Scheduler started")
            self.logger.info("🕐 Morning slot: 09:30")
            self.logger.info("🕐 Evening slot: 13:00")
            
        except Exception as e:
            self.logger.error(f"❌ Scheduler start failed: {e}")
            raise
    
    def run_manual_test(self):
        """Run manual test"""
        self.logger.info("🧪 Running manual test...")
        
        try:
            # Test WiFi download
            self.logger.info("Testing WiFi download...")
            wifi_result = self.wifi_download_callback("test")
            
            if wifi_result:
                self.logger.info("✅ WiFi download test passed")
                
                # Test Excel generation
                self.logger.info("Testing Excel generation...")
                excel_result = self.merge_callback()
                
                if excel_result:
                    self.logger.info("✅ Excel generation test passed")
                    self.logger.info("✅ Complete test passed")
                    return True
                else:
                    self.logger.error("❌ Excel generation test failed")
                    return False
            else:
                self.logger.error("❌ WiFi download test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Manual test failed: {e}")
            return False
    
    def start(self):
        """Start the automation runner"""
        self.logger.info("🚀 Starting WiFi Automation Runner...")
        
        try:
            self.running = True
            
            # Add to startup
            self.add_to_startup()
            
            # Start scheduler
            self.start_scheduler()
            
            self.logger.info("✅ Automation runner started successfully")
            self.logger.info("🔄 System will run continuously in background")
            self.logger.info("🔒 Will work even when PC is locked")
            self.logger.info("📅 Daily downloads at 09:30 and 13:00")
            
            # Keep running
            while self.running:
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Received stop signal")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ Automation runner error: {e}")
            raise
    
    def stop(self):
        """Stop the automation runner"""
        self.logger.info("🛑 Stopping automation runner...")
        
        self.running = False
        
        if self.scheduler:
            try:
                self.scheduler.shutdown()
                self.logger.info("✅ Scheduler stopped")
            except Exception as e:
                self.logger.error(f"❌ Scheduler stop error: {e}")
        
        self.logger.info("✅ Automation runner stopped")

def main():
    """Main function"""
    print("🚀 WiFi Automation Runner")
    print("=" * 50)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        runner = WiFiAutomationRunner()
        
        if command == "test":
            print("🧪 Running system test...")
            result = runner.run_manual_test()
            if result:
                print("✅ System test completed successfully")
            else:
                print("❌ System test failed")
            return
        
        elif command == "add-startup":
            print("📝 Adding to Windows startup...")
            if runner.add_to_startup():
                print("✅ Added to Windows startup successfully")
            else:
                print("❌ Failed to add to startup")
            return
        
        elif command == "remove-startup":
            print("🗑️ Removing from Windows startup...")
            if runner.remove_from_startup():
                print("✅ Removed from Windows startup successfully")
            else:
                print("❌ Failed to remove from startup")
            return
        
        elif command == "wifi-only":
            print("📶 Running WiFi download only...")
            result = runner.wifi_download_callback("manual")
            if result:
                print("✅ WiFi download completed")
            else:
                print("❌ WiFi download failed")
            return
        
        elif command == "excel-only":
            print("📊 Running Excel generation only...")
            result = runner.merge_callback()
            if result:
                print("✅ Excel generation completed")
            else:
                print("❌ Excel generation failed")
            return
        
        else:
            print("Usage: python run_automation.py [test|add-startup|remove-startup|wifi-only|excel-only]")
            return
    
    # Default - start the automation runner
    runner = WiFiAutomationRunner()
    
    print("🔄 Starting automation runner...")
    print("Press Ctrl+C to stop")
    print("")
    
    try:
        runner.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        runner.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        runner.stop()

if __name__ == "__main__":
    main() 