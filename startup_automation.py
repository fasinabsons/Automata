#!/usr/bin/env python3
"""
Startup Automation Script
Runs WiFi automation in background even when PC is locked
"""

import os
import sys
import time
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import win32gui
import win32con
import win32api
import win32service
import win32serviceutil
import schedule
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.advanced_scheduler import AdvancedScheduler
from corrected_wifi_app import CorrectedWiFiApp
from modules.excel_generator import ExcelGenerator
from modules.vbs_integration import VBSApplicationAutomation
from modules.email_service import EmailService

class StartupAutomation:
    """Main startup automation class"""
    
    def __init__(self):
        self.running = False
        self.scheduler = None
        self.setup_logging()
        self.setup_configuration()
        self.setup_components()
        
        self.logger.info("🚀 Startup Automation initialized")
    
    def setup_logging(self):
        """Setup logging with UTF-8 encoding"""
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "startup_automation.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("StartupAutomation")
    
    def setup_configuration(self):
        """Setup configuration"""
        self.config = {
            "slots": {
                "morning": "09:30",
                "evening": "13:00"
            },
            "merge_delay_minutes": 5,
            "enable_vbs": True,
            "enable_email": True,
            "continuous_operation": True,
            "run_on_startup": True
        }
    
    def setup_components(self):
        """Initialize all components"""
        self.logger.info("🔧 Initializing components...")
        
        try:
            # Initialize WiFi automation
            self.wifi_app = CorrectedWiFiApp()
            self.logger.info("✅ WiFi automation ready")
            
            # Initialize Excel generator
            self.excel_generator = ExcelGenerator()
            self.logger.info("✅ Excel generator ready")
            
            # Initialize VBS automation
            if self.config.get("enable_vbs", True):
                self.vbs_automation = VBSApplicationAutomation()
                self.logger.info("✅ VBS automation ready")
            
            # Initialize email service
            if self.config.get("enable_email", True):
                self.email_service = EmailService()
                self.logger.info("✅ Email service ready")
            
            self.logger.info("✅ All components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    def add_to_windows_startup(self):
        """Add to Windows startup registry"""
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
                    "WiFiAutomationStartup",
                    0,
                    winreg.REG_SZ,
                    f'"{script_path}" {startup_args}'
                )
            
            self.logger.info("✅ Added to Windows startup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add to startup: {e}")
            return False
    
    def wifi_download_task(self, slot_name: str):
        """WiFi download task"""
        self.logger.info(f"🔄 Starting WiFi download - {slot_name} slot")
        
        try:
            # Run WiFi automation
            result = self.wifi_app.run_corrected_automation()
            
            if result.get('success', False):
                files_downloaded = result.get('files_downloaded', 0)
                self.logger.info(f"✅ WiFi download completed: {files_downloaded} files")
                return True
            else:
                self.logger.error(f"❌ WiFi download failed for {slot_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ WiFi download error: {e}")
            return False
    
    def merge_and_vbs_task(self):
        """Excel merge and VBS processing task"""
        self.logger.info("🔄 Starting merge and VBS processing")
        
        try:
            # Step 1: Generate Excel file
            self.logger.info("📊 Generating Excel file...")
            excel_result = self.excel_generator.create_excel_from_csv_files()
            
            if not excel_result.get('success', False):
                self.logger.error("❌ Excel generation failed")
                return False
            
            excel_file = excel_result.get('excel_file')
            self.logger.info(f"✅ Excel file generated: {excel_file}")
            
            # Step 2: VBS automation
            if self.config.get("enable_vbs", True):
                self.logger.info("🏢 Starting VBS automation...")
                vbs_result = self.vbs_automation.run_complete_automation()
                
                if vbs_result.get('success', False):
                    self.logger.info("✅ VBS automation completed")
                    pdf_file = vbs_result.get('pdf_file')
                    
                    # Step 3: Email notification
                    if self.config.get("enable_email", True) and pdf_file:
                        self.logger.info("📧 Sending email...")
                        email_result = self.email_service.send_report_email(pdf_file)
                        
                        if email_result.get('success', False):
                            self.logger.info("✅ Email sent successfully")
                        else:
                            self.logger.warning("⚠️ Email sending failed")
                else:
                    self.logger.error("❌ VBS automation failed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Merge and VBS processing error: {e}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler"""
        self.logger.info("🕐 Starting scheduler...")
        
        try:
            # Create scheduler
            self.scheduler = AdvancedScheduler(
                slot_1_time=self.config["slots"]["morning"],
                slot_2_time=self.config["slots"]["evening"],
                merge_delay_minutes=self.config["merge_delay_minutes"],
                wifi_callback=self.wifi_download_task,
                merge_callback=self.merge_and_vbs_task
            )
            
            # Start scheduler in background thread
            scheduler_thread = threading.Thread(target=self.scheduler.start_scheduler, daemon=True)
            scheduler_thread.start()
            
            self.logger.info("✅ Scheduler started")
            self.logger.info(f"🕐 Morning slot: {self.config['slots']['morning']}")
            self.logger.info(f"🕐 Evening slot: {self.config['slots']['evening']}")
            
        except Exception as e:
            self.logger.error(f"❌ Scheduler start failed: {e}")
            raise
    
    def run_test(self):
        """Run a complete test"""
        self.logger.info("🧪 Running complete system test...")
        
        try:
            # Test WiFi download
            self.logger.info("Testing WiFi download...")
            if self.wifi_download_task("test"):
                self.logger.info("✅ WiFi download test passed")
                
                # Test Excel and VBS
                self.logger.info("Testing Excel and VBS...")
                if self.merge_and_vbs_task():
                    self.logger.info("✅ Complete system test passed")
                    return True
                else:
                    self.logger.error("❌ Excel/VBS test failed")
                    return False
            else:
                self.logger.error("❌ WiFi download test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ System test failed: {e}")
            return False
    
    def start(self):
        """Start the automation"""
        self.logger.info("🚀 Starting WiFi Automation System...")
        
        try:
            self.running = True
            
            # Add to startup if configured
            if self.config.get("run_on_startup", True):
                self.add_to_windows_startup()
            
            # Start scheduler
            self.start_scheduler()
            
            self.logger.info("✅ Automation system started successfully")
            self.logger.info("🔄 System will run continuously in background")
            self.logger.info("🔒 Will work even when PC is locked")
            
            # Keep running
            while self.running:
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Received stop signal")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ Automation system error: {e}")
            raise
    
    def stop(self):
        """Stop the automation"""
        self.logger.info("🛑 Stopping automation system...")
        
        self.running = False
        
        if self.scheduler:
            try:
                self.scheduler.shutdown()
                self.logger.info("✅ Scheduler stopped")
            except Exception as e:
                self.logger.error(f"❌ Scheduler stop error: {e}")
        
        self.logger.info("✅ Automation system stopped")

def main():
    """Main function"""
    print("🚀 WiFi Automation Startup Script")
    print("==================================")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        automation = StartupAutomation()
        
        if command == "test":
            print("🧪 Running system test...")
            result = automation.run_test()
            if result:
                print("✅ System test completed successfully")
            else:
                print("❌ System test failed")
            return
        
        elif command == "add-startup":
            print("📝 Adding to Windows startup...")
            if automation.add_to_windows_startup():
                print("✅ Added to Windows startup successfully")
            else:
                print("❌ Failed to add to startup")
            return
        
        elif command == "wifi-only":
            print("📶 Running WiFi download only...")
            result = automation.wifi_download_task("manual")
            if result:
                print("✅ WiFi download completed")
            else:
                print("❌ WiFi download failed")
            return
        
        elif command == "vbs-only":
            print("🏢 Running VBS automation only...")
            result = automation.merge_and_vbs_task()
            if result:
                print("✅ VBS automation completed")
            else:
                print("❌ VBS automation failed")
            return
        
        else:
            print("Usage: python startup_automation.py [test|add-startup|wifi-only|vbs-only]")
            return
    
    # Default - start the automation
    automation = StartupAutomation()
    
    print("🔄 Starting automation system...")
    print("Press Ctrl+C to stop")
    
    try:
        automation.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        automation.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        automation.stop()

if __name__ == "__main__":
    main() 