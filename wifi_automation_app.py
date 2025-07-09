#!/usr/bin/env python3
"""
WiFi Automation Application
Complete background automation system for WiFi data collection and Excel generation
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add current directory to path
sys.path.append('.')

# Import our modules
from modules.advanced_scheduler import AdvancedScheduler
from modules.excel_generator import EnhancedExcelGenerator
from modules.windows_service import SystemTrayApp, WindowsIntegration
from modules.vbs_integration import VBSApplicationAutomation
from modules.email_service import EmailService
from corrected_wifi_app import CorrectedWiFiApp

class WiFiAutomationApp:
    """Main WiFi Automation Application"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.scheduler = AdvancedScheduler()
        self.excel_generator = EnhancedExcelGenerator()
        self.vbs_automation = VBSApplicationAutomation()
        self.email_service = EmailService()
        self.wifi_app = CorrectedWiFiApp()
        self.running = False
        
        # Setup directories with dynamic date
        today = datetime.now().strftime("%d%B").lower()  # e.g., "04january", "29february" (leap year)
        self.csv_dir = Path(f"EHC_Data/{today}")
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("WiFi Automation App initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for main application"""
        logger = logging.getLogger("WiFiAutomationApp")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        if not logger.handlers:
            # File handler
            log_file = log_dir / "wifi_automation.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def setup_callbacks(self):
        """Setup scheduler callbacks"""
        self.scheduler.set_download_callback(self._wifi_download_callback)
        self.scheduler.set_merge_callback(self._merge_callback)
        self.logger.info("Callbacks configured")
    
    def _wifi_download_callback(self, slot_name: str) -> Dict[str, Any]:
        """Callback for WiFi download execution"""
        try:
            self.logger.info(f"🚀 Executing WiFi download for {slot_name} slot")
            
            # Execute WiFi automation
            result = self.wifi_app.run_robust_automation()
            
            if result.get("success", False):
                files_downloaded = result.get("files_downloaded", 4)  # Default to 4 networks
                self.logger.info(f"✅ {slot_name} slot completed: {files_downloaded} files downloaded")
                
                # Count actual CSV files
                csv_files = list(self.csv_dir.glob("*.csv"))
                actual_files = len(csv_files)
                
                return {
                    "success": True, 
                    "files_downloaded": actual_files,
                    "slot_name": slot_name,
                    "csv_directory": str(self.csv_dir)
                }
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"❌ {slot_name} slot failed: {error_msg}")
                return {"success": False, "error": error_msg, "slot_name": slot_name}
                
        except Exception as e:
            error_msg = f"WiFi download callback error: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg, "slot_name": slot_name}
    
    def _merge_callback(self, result: Dict[str, Any]):
        """Callback for merge completion"""
        try:
            self.logger.info("📊 Excel merge completed successfully")
            self.logger.info(f"📄 Excel file: {result.get('file_path', 'N/A')}")
            self.logger.info(f"📏 File size: {result.get('file_size_mb', 0)} MB")
            self.logger.info(f"📝 Records: {result.get('rows_written', 0)}")
            
            # Get Excel file path
            excel_file_path = result.get('file_path')
            if excel_file_path and Path(excel_file_path).exists():
                self.logger.info("🔄 Starting VBS application automation")
                self.logger.info("⏰ Note: VBS processing can take 5-30 minutes for import and up to 1 hour for updates")
                
                # Upload Excel to VBS application and generate PDF
                vbs_result = self.vbs_automation.run_complete_automation()
                
                if vbs_result.get("success", False):
                    self.logger.info("✅ VBS workflow completed successfully")
                    self.logger.info(f"📤 Excel uploaded: {vbs_result.get('excel_uploaded', False)}")
                    self.logger.info(f"📄 PDF generated: {vbs_result.get('pdf_generated', False)}")
                    
                    if vbs_result.get("report_path"):
                        self.logger.info(f"📄 PDF saved to: {vbs_result.get('report_path')}")
                        
                        # Send PDF report via email
                        self.logger.info("📧 Sending PDF report via email")
                        email_result = self.email_service.send_pdf_report(Path(vbs_result.get('report_path')))
                        
                        if email_result.get("success", False):
                            self.logger.info("✅ PDF report sent via email successfully")
                            result["email_sent"] = True
                            result["email_recipients"] = email_result.get("recipients", [])
                        else:
                            self.logger.error(f"❌ Failed to send PDF report via email: {email_result.get('error', 'Unknown error')}")
                            result["email_sent"] = False
                            result["email_error"] = email_result.get("error")
                    
                    # Update result with VBS information
                    result["vbs_upload_success"] = True
                    result["vbs_pdf_path"] = vbs_result.get("report_path")
                else:
                    self.logger.error(f"❌ VBS workflow failed: {vbs_result.get('error', 'Unknown error')}")
                    result["vbs_upload_success"] = False
                    result["vbs_error"] = vbs_result.get("error")
            else:
                self.logger.warning("⚠️ Excel file not found - skipping VBS upload")
                result["vbs_upload_success"] = False
                result["vbs_error"] = "Excel file not found"
            
            # Log daily summary
            self._log_daily_summary(result)
            
        except Exception as e:
            self.logger.error(f"Merge callback error: {e}")
            result["vbs_upload_success"] = False
            result["vbs_error"] = str(e)
    
    def _log_daily_summary(self, excel_result: Dict[str, Any]):
        """Log daily summary statistics"""
        try:
            status = self.scheduler.get_status()
            daily_status = status.get("daily_status", {})
            
            summary = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "slots_completed": len(daily_status.get("slots_completed", [])),
                "total_slots": len(self.scheduler.time_slots),
                "csv_files_downloaded": daily_status.get("csv_files_count", 0),
                "excel_file_generated": excel_result.get("file_path", "N/A"),
                "excel_file_size_mb": excel_result.get("file_size_mb", 0),
                "total_records": excel_result.get("rows_written", 0)
            }
            
            self.logger.info("📈 DAILY SUMMARY:")
            for key, value in summary.items():
                self.logger.info(f"   {key}: {value}")
                
        except Exception as e:
            self.logger.error(f"Error logging daily summary: {e}")
    
    def run_console_mode(self):
        """Run in console mode (for testing)"""
        try:
            self.logger.info("🖥️ Starting WiFi Automation in console mode")
            
            # Setup callbacks
            self.setup_callbacks()
            
            # Start scheduler
            if self.scheduler.start_scheduler():
                self.logger.info("✅ Scheduler started successfully")
                self.logger.info("📅 Scheduled slots:")
                for slot in self.scheduler.time_slots:
                    self.logger.info(f"   - {slot['name']}: {slot['time']}")
            else:
                self.logger.error("❌ Failed to start scheduler")
                return False
            
            self.running = True
            self.logger.info("🔄 Application running... Press Ctrl+C to stop")
            
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("⏹️ Stop signal received")
                self.running = False
            
            # Stop scheduler
            self.scheduler.stop_scheduler()
            self.logger.info("✅ Application stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Console mode error: {e}")
            return False
    
    def run_tray_mode(self):
        """Run in system tray mode"""
        try:
            self.logger.info("🔧 Starting WiFi Automation in system tray mode")
            
            # Create and run system tray app
            tray_app = SystemTrayApp()
            tray_app.run()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Tray mode error: {e}")
            return False
    
    def manual_trigger_slot(self, slot_name: str) -> Dict[str, Any]:
        """Manually trigger a specific slot"""
        self.setup_callbacks()
        return self.scheduler.manual_trigger_slot(slot_name)
    
    def manual_trigger_merge(self) -> Dict[str, Any]:
        """Manually trigger Excel merge"""
        return self.scheduler.manual_trigger_merge()
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status"""
        scheduler_status = self.scheduler.get_status()
        
        return {
            "application_running": self.running,
            "scheduler_status": scheduler_status,
            "excel_generator_available": True,
            "wifi_app_available": True
        }
    
    def setup_windows_integration(self):
        """Setup robust Windows integration for 365-366 day operation"""
        try:
            self.logger.info("Setting up robust Windows integration...")
            
            # Create Windows startup entry
            if self._create_windows_startup_entry():
                self.logger.info("✅ Windows startup entry created successfully")
            else:
                self.logger.warning("❌ Failed to create Windows startup entry")
            
            # Create Windows service entry (optional)
            if self._create_windows_service():
                self.logger.info("✅ Windows service created successfully")
            else:
                self.logger.warning("❌ Failed to create Windows service")
                
            # Configure Windows power settings
            if self._configure_power_settings():
                self.logger.info("✅ Power settings configured successfully")
            else:
                self.logger.warning("❌ Failed to configure power settings")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Windows integration setup failed: {e}")
            return False
    
    def _create_windows_startup_entry(self):
        """Create Windows startup registry entry"""
        try:
            import winreg
            import sys
            
            # Get current script path
            script_path = os.path.abspath(__file__)
            python_exe = sys.executable
            
            # Create startup command
            startup_cmd = f'"{python_exe}" "{script_path}" --background'
            
            # Registry key for current user startup
            reg_key = winreg.HKEY_CURRENT_USER
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Open registry key
            with winreg.OpenKey(reg_key, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "WiFiAutomation", 0, winreg.REG_SZ, startup_cmd)
            
            self.logger.info(f"Startup registry entry created: {startup_cmd}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create startup entry: {e}")
            return False
    
    def _create_windows_service(self):
        """Create Windows service for robust operation"""
        try:
            import subprocess
            import sys
            
            # Create service using sc command
            service_name = "WiFiAutomationService"
            script_path = os.path.abspath(__file__)
            python_exe = sys.executable
            
            # Service command
            service_cmd = f'"{python_exe}" "{script_path}" --service'
            
            # Create service
            cmd = [
                'sc', 'create', service_name,
                'binPath=', service_cmd,
                'start=', 'auto',
                'DisplayName=', 'WiFi Automation Service'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                self.logger.info(f"Windows service created: {service_name}")
                return True
            else:
                self.logger.warning(f"Service creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create Windows service: {e}")
            return False
    
    def _configure_power_settings(self):
        """Configure Windows power settings for 365-366 day operation"""
        try:
            import subprocess
            
            # Power settings commands
            power_commands = [
                # Never sleep
                ['powercfg', '/change', 'standby-timeout-ac', '0'],
                ['powercfg', '/change', 'standby-timeout-dc', '0'],
                # Never turn off display
                ['powercfg', '/change', 'monitor-timeout-ac', '0'],
                ['powercfg', '/change', 'monitor-timeout-dc', '0'],
                # Never turn off hard disk
                ['powercfg', '/change', 'disk-timeout-ac', '0'],
                ['powercfg', '/change', 'disk-timeout-dc', '0'],
                # Disable hibernation
                ['powercfg', '/hibernate', 'off']
            ]
            
            success_count = 0
            for cmd in power_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        success_count += 1
                    else:
                        self.logger.warning(f"Power command failed: {' '.join(cmd)}")
                except Exception as e:
                    self.logger.warning(f"Power command error: {e}")
            
            if success_count >= len(power_commands) // 2:
                self.logger.info(f"Power settings configured ({success_count}/{len(power_commands)} commands successful)")
                return True
            else:
                self.logger.warning(f"Power settings partially configured ({success_count}/{len(power_commands)} commands successful)")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to configure power settings: {e}")
            return False

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="WiFi Automation Application")
    
    # Execution modes
    parser.add_argument("--console", action="store_true", help="Run in console mode")
    parser.add_argument("--tray", action="store_true", help="Run in system tray mode")
    
    # Manual triggers
    parser.add_argument("--trigger-morning", action="store_true", help="Manually trigger morning slot")
    parser.add_argument("--trigger-afternoon", action="store_true", help="Manually trigger afternoon slot")
    parser.add_argument("--trigger-evening", action="store_true", help="Manually trigger evening slot")
    parser.add_argument("--trigger-merge", action="store_true", help="Manually trigger Excel merge")
    
    # Status and testing
    parser.add_argument("--status", action="store_true", help="Show application status")
    parser.add_argument("--test-excel", action="store_true", help="Test Excel generation")
    parser.add_argument("--test-scheduler", action="store_true", help="Test scheduler")
    parser.add_argument("--test-vbs", action="store_true", help="Test VBS integration")
    parser.add_argument("--test-vbs-upload", type=str, help="Test VBS upload with specific Excel file")
    
    # Windows service integration
    parser.add_argument("--install-service", action="store_true", help="Install Windows service")
    parser.add_argument("--remove-service", action="store_true", help="Remove Windows service")
    parser.add_argument("--start-service", action="store_true", help="Start Windows service")
    parser.add_argument("--stop-service", action="store_true", help="Stop Windows service")
    parser.add_argument("--add-startup", action="store_true", help="Add to Windows startup")
    parser.add_argument("--remove-startup", action="store_true", help="Remove from Windows startup")
    
    # Email testing
    parser.add_argument('--test-email', action='store_true', help='Test email configuration')
    parser.add_argument('--send-test-email', action='store_true', help='Send test email')
    parser.add_argument('--email-config', action='store_true', help='Show email configuration help')
    parser.add_argument('--complete-test', action='store_true', help='Run complete system test')
    
    args = parser.parse_args()
    
    # Create application instance
    app = WiFiAutomationApp()
    
    # Handle Windows service operations
    if any([args.install_service, args.remove_service, args.start_service, 
            args.stop_service, args.add_startup, args.remove_startup]):
        integration = WindowsIntegration()
        
        if args.install_service:
            result = integration.install_service()
            print(f"Service installation: {'Success' if result else 'Failed'}")
        elif args.remove_service:
            result = integration.remove_service()
            print(f"Service removal: {'Success' if result else 'Failed'}")
        elif args.start_service:
            result = integration.start_service()
            print(f"Service start: {'Success' if result else 'Failed'}")
        elif args.stop_service:
            result = integration.stop_service()
            print(f"Service stop: {'Success' if result else 'Failed'}")
        elif args.add_startup:
            result = integration.add_to_startup()
            print(f"Add to startup: {'Success' if result else 'Failed'}")
        elif args.remove_startup:
            result = integration.remove_from_startup()
            print(f"Remove from startup: {'Success' if result else 'Failed'}")
        
        return
    
    # Handle manual triggers
    if args.trigger_morning:
        result = app.manual_trigger_slot("morning")
        print(f"Morning slot trigger: {result}")
        return
    elif args.trigger_afternoon:
        result = app.manual_trigger_slot("afternoon")
        print(f"Afternoon slot trigger: {result}")
        return
    elif args.trigger_evening:
        result = app.manual_trigger_slot("evening")
        print(f"Evening slot trigger: {result}")
        return
    elif args.trigger_merge:
        result = app.manual_trigger_merge()
        print(f"Merge trigger: {result}")
        return
    
    # Handle status and testing
    if args.status:
        status = app.get_status()
        print("📊 Application Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        return
    elif args.test_excel:
        from modules.excel_generator import test_excel_generation
        test_excel_generation()
        return
    elif args.test_scheduler:
        from modules.advanced_scheduler import test_scheduler
        test_scheduler()
        return
    elif args.test_vbs:
        from modules.vbs_integration import test_vbs_integration
        test_vbs_integration()
        return
    elif args.test_vbs_upload:
        from modules.vbs_integration import test_vbs_upload
        test_vbs_upload(args.test_vbs_upload)
        return
    
    elif args.test_email:
        # Test email configuration
        from modules.email_service import EmailService
        email_service = EmailService()
        result = email_service.test_email_connection()
        
        if result["success"]:
            print("✅ Email configuration test: SUCCESS")
            print(f"   {result['message']}")
        else:
            print("❌ Email configuration test: FAILED")
            print(f"   Error: {result['error']}")
    
    elif args.send_test_email:
        # Send test email
        from modules.email_service import EmailService
        email_service = EmailService()
        result = email_service.send_test_email()
        
        if result["success"]:
            print("✅ Test email sent successfully")
            print(f"   Recipients: {result.get('recipients', [])}")
        else:
            print("❌ Failed to send test email")
            print(f"   Error: {result['error']}")
    
    elif args.email_config:
        # Show email configuration help
        from config.email_config import print_setup_instructions, test_email_config
        print_setup_instructions("gmail")
        test_email_config()
    
    elif args.complete_test:
        # Run complete system test
        print("🔄 Running complete system test...")
        app = WiFiAutomationApp()
        
        # Test WiFi download
        print("\n1. Testing WiFi download...")
        wifi_result = app._wifi_download_callback("test")
        if wifi_result.get("success"):
            print("✅ WiFi download: SUCCESS")
        else:
            print("❌ WiFi download: FAILED")
        
        # Test Excel generation
        print("\n2. Testing Excel generation...")
        excel_result = app._merge_callback(None)
        if excel_result.get("success"):
            print("✅ Excel generation: SUCCESS")
        else:
            print("❌ Excel generation: FAILED")
        
        # Test email if PDF exists
        if excel_result.get("vbs_pdf_path"):
            print("\n3. Testing email delivery...")
            email_result = app.email_service.send_pdf_report(Path(excel_result["vbs_pdf_path"]))
            if email_result.get("success"):
                print("✅ Email delivery: SUCCESS")
            else:
                print("❌ Email delivery: FAILED")
        
        print("\n🏁 Complete system test finished")
    
    elif args.console:
        # Console mode
        print("🖥️  Starting WiFi Automation in console mode...")
        app = WiFiAutomationApp()
        app.run_console_mode()
    
    elif args.tray:
        # System tray mode
        print("📋 Starting WiFi Automation in system tray mode...")
        app = WiFiAutomationApp()
        app.run_tray_mode()
    
    else:
        # Default: show help
        parser.print_help()

if __name__ == "__main__":
    main()