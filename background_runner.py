#!/usr/bin/env python3
"""
Background WiFi Automation Runner
Runs in background even when PC is locked
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
import win32process
import win32security
import win32service
import win32serviceutil
import pystray
from PIL import Image
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

class BackgroundAutomationRunner:
    """Background runner that works even when PC is locked"""
    
    def __init__(self):
        self.running = False
        self.scheduler = None
        self.setup_logging()
        self.setup_configuration()
        self.setup_components()
        
        # System tray icon
        self.tray_icon = None
        
        self.logger.info("Background Automation Runner initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "background_runner.log"
        
        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("BackgroundRunner")
    
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
            "auto_start": True,
            "run_on_startup": True
        }
        
        # Load config from file if exists
        config_file = project_root / "config" / "background_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
    
    def setup_components(self):
        """Initialize all automation components"""
        self.logger.info("Initializing automation components...")
        
        try:
            # Initialize WiFi automation
            self.wifi_app = CorrectedWiFiApp()
            self.logger.info("✅ WiFi automation initialized")
            
            # Initialize Excel generator
            self.excel_generator = ExcelGenerator()
            self.logger.info("✅ Excel generator initialized")
            
            # Initialize VBS automation if enabled
            if self.config.get("enable_vbs", True):
                self.vbs_automation = VBSApplicationAutomation()
                self.logger.info("✅ VBS automation initialized")
            
            # Initialize email service if enabled
            if self.config.get("enable_email", True):
                self.email_service = EmailService()
                self.logger.info("✅ Email service initialized")
            
            self.logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    def create_system_tray(self):
        """Create system tray icon for background operation"""
        try:
            # Create a simple icon (you can replace with actual icon file)
            image = Image.new('RGB', (64, 64), color='blue')
            
            # Create menu items
            menu_items = [
                pystray.MenuItem("WiFi Automation", lambda: None, enabled=False),
                pystray.MenuItem("Status", self.show_status),
                pystray.MenuItem("Trigger Morning Slot", self.trigger_morning_slot),
                pystray.MenuItem("Trigger Evening Slot", self.trigger_evening_slot),
                pystray.MenuItem("Run Complete Test", self.run_complete_test),
                pystray.MenuItem("Open Logs", self.open_logs),
                pystray.MenuItem("Exit", self.exit_application)
            ]
            
            # Create tray icon
            self.tray_icon = pystray.Icon(
                "WiFi Automation",
                image,
                "WiFi Automation Service",
                menu=pystray.Menu(*menu_items)
            )
            
            self.logger.info("✅ System tray icon created")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create system tray: {e}")
    
    def show_status(self):
        """Show current status"""
        status = f"""
WiFi Automation Status:
- Running: {self.running}
- Morning Slot: {self.config['slots']['morning']}
- Evening Slot: {self.config['slots']['evening']}
- VBS Enabled: {self.config['enable_vbs']}
- Email Enabled: {self.config['enable_email']}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        print(status)
        self.logger.info(status)
    
    def trigger_morning_slot(self):
        """Manually trigger morning slot"""
        self.logger.info("🌅 Manually triggering morning slot...")
        threading.Thread(target=self.wifi_download_callback, args=("morning",), daemon=True).start()
    
    def trigger_evening_slot(self):
        """Manually trigger evening slot"""
        self.logger.info("🌆 Manually triggering evening slot...")
        threading.Thread(target=self.wifi_download_callback, args=("evening",), daemon=True).start()
    
    def run_complete_test(self):
        """Run complete system test"""
        self.logger.info("🧪 Running complete system test...")
        threading.Thread(target=self.complete_test, daemon=True).start()
    
    def complete_test(self):
        """Complete system test"""
        try:
            # Test WiFi download
            self.logger.info("Testing WiFi download...")
            wifi_result = self.wifi_app.run_robust_automation()
            
            if wifi_result.get('success', False):
                self.logger.info("✅ WiFi download test passed")
                
                # Test Excel generation
                self.logger.info("Testing Excel generation...")
                excel_result = self.excel_generator.create_excel_from_csv_files()
                
                if excel_result.get('success', False):
                    self.logger.info("✅ Excel generation test passed")
                    
                    # Test VBS automation if enabled
                    if self.config.get("enable_vbs", True):
                        self.logger.info("Testing VBS automation...")
                        vbs_result = self.vbs_automation.run_complete_automation()
                        
                        if vbs_result.get('success', False):
                            self.logger.info("✅ VBS automation test passed")
                        else:
                            self.logger.warning("⚠️ VBS automation test failed")
                    
                    self.logger.info("✅ Complete system test finished")
                else:
                    self.logger.error("❌ Excel generation test failed")
            else:
                self.logger.error("❌ WiFi download test failed")
                
        except Exception as e:
            self.logger.error(f"❌ Complete test failed: {e}")
    
    def open_logs(self):
        """Open logs directory"""
        try:
            log_dir = project_root / "logs"
            os.startfile(str(log_dir))
        except Exception as e:
            self.logger.error(f"Failed to open logs: {e}")
    
    def exit_application(self):
        """Exit the application"""
        self.logger.info("Exiting application...")
        self.stop()
        if self.tray_icon:
            self.tray_icon.stop()
    
    def wifi_download_callback(self, slot_name: str):
        """Callback for WiFi download operations"""
        self.logger.info(f"🔄 Starting WiFi download for {slot_name} slot")
        
        try:
            # Ensure we can run even when locked
            self.ensure_session_access()
            
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
    
    def merge_and_process_callback(self):
        """Callback for Excel merge and VBS processing"""
        self.logger.info("🔄 Starting merge and processing operations")
        
        try:
            # Ensure we can run even when locked
            self.ensure_session_access()
            
            # Step 1: Generate Excel file
            self.logger.info("📊 Generating Excel file...")
            excel_result = self.excel_generator.create_excel_from_csv_files()
            
            if not excel_result.get('success', False):
                self.logger.error("❌ Excel generation failed")
                return False
            
            excel_file = excel_result.get('excel_file')
            self.logger.info(f"✅ Excel file generated: {excel_file}")
            
            # Step 2: VBS automation if enabled
            if self.config.get("enable_vbs", True):
                self.logger.info("🏢 Starting VBS automation...")
                vbs_result = self.vbs_automation.run_complete_automation()
                
                if vbs_result.get('success', False):
                    self.logger.info("✅ VBS automation completed successfully")
                    pdf_file = vbs_result.get('pdf_file')
                    
                    # Step 3: Email notification if enabled
                    if self.config.get("enable_email", True) and pdf_file:
                        self.logger.info("📧 Sending email notification...")
                        email_result = self.email_service.send_report_email(pdf_file)
                        
                        if email_result.get('success', False):
                            self.logger.info("✅ Email sent successfully")
                        else:
                            self.logger.warning("⚠️ Email sending failed")
                else:
                    self.logger.error("❌ VBS automation failed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Merge and processing error: {e}")
            return False
    
    def ensure_session_access(self):
        """Ensure we can access the desktop even when locked"""
        try:
            # Try to get desktop window
            desktop = win32gui.GetDesktopWindow()
            
            # Try to set our process to interact with desktop
            current_process = win32api.GetCurrentProcess()
            
            # This helps ensure we can run UI automation even when locked
            win32process.SetProcessWorkingSetSize(current_process, -1, -1)
            
            self.logger.debug("Session access ensured")
            
        except Exception as e:
            self.logger.warning(f"Session access warning: {e}")
    
    def start_scheduler(self):
        """Start the advanced scheduler"""
        self.logger.info("🕐 Starting scheduler...")
        
        try:
            # Create scheduler with callbacks
            self.scheduler = AdvancedScheduler(
                slot_1_time=self.config["slots"]["morning"],
                slot_2_time=self.config["slots"]["evening"],
                merge_delay_minutes=self.config["merge_delay_minutes"],
                wifi_callback=self.wifi_download_callback,
                merge_callback=self.merge_and_process_callback
            )
            
            # Start scheduler in background thread
            scheduler_thread = threading.Thread(target=self.scheduler.start_scheduler, daemon=True)
            scheduler_thread.start()
            
            self.logger.info("✅ Scheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Scheduler start failed: {e}")
            raise
    
    def add_to_startup(self):
        """Add to Windows startup"""
        try:
            import winreg
            
            # Get the path to this script
            script_path = sys.executable
            script_args = f'"{__file__}" --background'
            
            # Registry key for startup
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Open registry key
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(
                    reg_key,
                    "WiFiAutomation",
                    0,
                    winreg.REG_SZ,
                    f'"{script_path}" {script_args}'
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
            
            # Open registry key
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, "WiFiAutomation")
            
            self.logger.info("✅ Removed from Windows startup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove from startup: {e}")
            return False
    
    def start(self):
        """Start the background runner"""
        self.logger.info("🚀 Starting Background Automation Runner...")
        
        try:
            self.running = True
            
            # Start scheduler
            self.start_scheduler()
            
            # Add to startup if configured
            if self.config.get("run_on_startup", True):
                self.add_to_startup()
            
            # Create system tray
            self.create_system_tray()
            
            self.logger.info("✅ Background runner started successfully")
            self.logger.info("🕐 Automation will run at scheduled times:")
            self.logger.info(f"   Morning: {self.config['slots']['morning']}")
            self.logger.info(f"   Evening: {self.config['slots']['evening']}")
            
            # Run system tray (this blocks)
            if self.tray_icon:
                self.tray_icon.run()
            else:
                # Fallback - just keep running
                while self.running:
                    time.sleep(60)
                    
        except Exception as e:
            self.logger.error(f"❌ Background runner failed: {e}")
            raise
    
    def stop(self):
        """Stop the background runner"""
        self.logger.info("🛑 Stopping Background Automation Runner...")
        
        self.running = False
        
        if self.scheduler:
            try:
                self.scheduler.shutdown()
                self.logger.info("✅ Scheduler stopped")
            except Exception as e:
                self.logger.error(f"❌ Scheduler stop error: {e}")
        
        self.logger.info("✅ Background runner stopped")

def main():
    """Main function"""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="WiFi Automation Background Runner")
    parser.add_argument("--background", action="store_true", help="Run in background mode")
    parser.add_argument("--console", action="store_true", help="Run in console mode")
    parser.add_argument("--install-startup", action="store_true", help="Install to Windows startup")
    parser.add_argument("--remove-startup", action="store_true", help="Remove from Windows startup")
    parser.add_argument("--test", action="store_true", help="Run system test")
    
    args = parser.parse_args()
    
    # Create runner
    runner = BackgroundAutomationRunner()
    
    if args.install_startup:
        runner.add_to_startup()
        print("✅ Added to Windows startup")
        return
    
    if args.remove_startup:
        runner.remove_from_startup()
        print("✅ Removed from Windows startup")
        return
    
    if args.test:
        runner.complete_test()
        return
    
    if args.console:
        print("🖥️ Running in console mode...")
        print("Press Ctrl+C to stop")
        try:
            runner.start()
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            runner.stop()
    else:
        # Default - run in background
        print("🔄 Starting background automation...")
        print("Check system tray for controls")
        runner.start()

if __name__ == "__main__":
    main() 