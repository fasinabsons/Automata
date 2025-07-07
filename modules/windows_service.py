#!/usr/bin/env python3
"""
Windows Service Integration
Provides Windows service functionality for background operation and startup integration
"""

import os
import sys
import time
import logging
import threading
import win32serviceutil
import win32service
import win32event
import win32api
import win32gui
import win32con
from pathlib import Path
import subprocess
import json
from datetime import datetime, timedelta
import servicemanager
import pystray
from PIL import Image, ImageDraw
import winreg

# Import our modules
sys.path.append('.')
from modules.advanced_scheduler import AdvancedScheduler
from corrected_wifi_app import CorrectedWiFiApp
from modules.vbs_integration import VBSApplicationAutomation
from modules.excel_generator import ExcelGenerator
from modules.email_service import EmailService

class WiFiAutomationService(win32serviceutil.ServiceFramework):
    """Windows Service for WiFi Automation that runs in background even when PC is locked"""
    
    _svc_name_ = "WiFiAutomationService"
    _svc_display_name_ = "WiFi Data Automation Service"
    _svc_description_ = "Automated WiFi data collection and VBS integration service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.scheduler = None
        self.setup_logging()
        
        # Service configuration
        self.config = {
            "service_name": self._svc_name_,
            "project_root": str(Path(__file__).parent.parent),
            "log_file": str(Path(__file__).parent.parent / "logs" / "service.log"),
            "slots": {
                "morning": "09:30",
                "evening": "13:00"
            },
            "merge_delay_minutes": 5,
            "enable_vbs": True,
            "enable_email": True
        }
        
        self.logger.info(f"WiFi Automation Service initialized at {datetime.now()}")
    
    def setup_logging(self):
        """Setup logging for the service"""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "service.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(self._svc_name_)
        
        # Also log to Windows Event Log
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
    
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # Stop the scheduler
        if self.scheduler:
            try:
                self.scheduler.shutdown()
                self.logger.info("Scheduler stopped")
            except Exception as e:
                self.logger.error(f"Error stopping scheduler: {e}")
        
        # Signal the service to stop
        self.running = False
        win32event.SetEvent(self.hWaitStop)
        
        self.logger.info("Service stopped")
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )
    
    def SvcDoRun(self):
        """Main service execution"""
        self.logger.info("Service starting...")
        
        try:
            # Initialize components
            self.initialize_components()
            
            # Start the scheduler
            self.start_scheduler()
            
            # Service main loop
            self.service_main_loop()
            
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, str(e))
            )
    
    def initialize_components(self):
        """Initialize all automation components"""
        self.logger.info("Initializing automation components...")
        
        # Initialize WiFi automation
        self.wifi_app = CorrectedWiFiApp()
        self.logger.info("WiFi automation initialized")
        
        # Initialize Excel generator
        self.excel_generator = ExcelGenerator()
        self.logger.info("Excel generator initialized")
        
        # Initialize VBS automation if enabled
        if self.config.get("enable_vbs", True):
            self.vbs_automation = VBSApplicationAutomation()
            self.logger.info("VBS automation initialized")
        
        # Initialize email service if enabled
        if self.config.get("enable_email", True):
            self.email_service = EmailService()
            self.logger.info("Email service initialized")
        
        self.logger.info("All components initialized successfully")
    
    def start_scheduler(self):
        """Start the advanced scheduler"""
        self.logger.info("Starting scheduler...")
        
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
        
        self.logger.info("Scheduler started successfully")
    
    def wifi_download_callback(self, slot_name: str):
        """Callback for WiFi download operations"""
        self.logger.info(f"Starting WiFi download for {slot_name} slot")
        
        try:
            # Run WiFi automation
            result = self.wifi_app.run_corrected_automation()
            
            if result.get('success', False):
                files_downloaded = result.get('files_downloaded', 0)
                self.logger.info(f"WiFi download completed: {files_downloaded} files downloaded")
                
                # Log to Windows Event Log
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    servicemanager.PYS_SERVICE_STARTED,
                    (f"WiFi Download {slot_name}", f"{files_downloaded} files downloaded")
                )
                
                return True
            else:
                self.logger.error(f"WiFi download failed for {slot_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"WiFi download error: {e}")
            return False
    
    def merge_and_process_callback(self):
        """Callback for Excel merge and VBS processing"""
        self.logger.info("Starting merge and processing operations")
        
        try:
            # Step 1: Generate Excel file
            self.logger.info("Generating Excel file...")
            excel_result = self.excel_generator.create_excel_from_csv_files()
            
            if not excel_result.get('success', False):
                self.logger.error("Excel generation failed")
                return False
            
            excel_file = excel_result.get('excel_file')
            self.logger.info(f"Excel file generated: {excel_file}")
            
            # Step 2: VBS automation if enabled
            if self.config.get("enable_vbs", True):
                self.logger.info("Starting VBS automation...")
                vbs_result = self.vbs_automation.run_complete_automation()
                
                if vbs_result.get('success', False):
                    self.logger.info("VBS automation completed successfully")
                    pdf_file = vbs_result.get('pdf_file')
                    
                    # Step 3: Email notification if enabled
                    if self.config.get("enable_email", True) and pdf_file:
                        self.logger.info("Sending email notification...")
                        email_result = self.email_service.send_report_email(pdf_file)
                        
                        if email_result.get('success', False):
                            self.logger.info("Email sent successfully")
                        else:
                            self.logger.warning("Email sending failed")
                else:
                    self.logger.error("VBS automation failed")
            
            # Log completion to Windows Event Log
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                ("Daily Processing", "Excel merge and VBS processing completed")
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Merge and processing error: {e}")
            return False
    
    def service_main_loop(self):
        """Main service loop"""
        self.logger.info("Service main loop started")
        
        # Wait for stop signal or run indefinitely
        while self.running:
            # Wait for stop event (timeout every 60 seconds to check status)
            result = win32event.WaitForSingleObject(self.hWaitStop, 60000)  # 60 seconds
            
            if result == win32event.WAIT_OBJECT_0:
                # Stop event was signaled
                break
            elif result == win32event.WAIT_TIMEOUT:
                # Timeout - continue running (this is normal)
                self.logger.debug("Service heartbeat - still running")
                continue
            else:
                # Some other result - log and continue
                self.logger.warning(f"Unexpected wait result: {result}")
                continue
        
        self.logger.info("Service main loop ended")

class WiFiAutomationServiceManager:
    """Service management utilities"""
    
    def __init__(self):
        self.service_name = WiFiAutomationService._svc_name_
        self.logger = logging.getLogger("ServiceManager")
    
    def install_service(self):
        """Install the Windows service"""
        try:
            # Install the service
            win32serviceutil.InstallService(
                WiFiAutomationService._svc_reg_class_,
                WiFiAutomationService._svc_name_,
                WiFiAutomationService._svc_display_name_,
                description=WiFiAutomationService._svc_description_
            )
            
            # Set service to start automatically
            self.set_service_startup_type('auto')
            
            print(f"✅ Service '{self.service_name}' installed successfully")
            print("   Service will start automatically with Windows")
            return True
            
        except Exception as e:
            print(f"❌ Service installation failed: {e}")
            return False
    
    def uninstall_service(self):
        """Uninstall the Windows service"""
        try:
            # Stop service if running
            self.stop_service()
            
            # Uninstall the service
            win32serviceutil.RemoveService(self.service_name)
            print(f"✅ Service '{self.service_name}' uninstalled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Service uninstallation failed: {e}")
            return False
    
    def start_service(self):
        """Start the Windows service"""
        try:
            win32serviceutil.StartService(self.service_name)
            print(f"✅ Service '{self.service_name}' started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Service start failed: {e}")
            return False
    
    def stop_service(self):
        """Stop the Windows service"""
        try:
            win32serviceutil.StopService(self.service_name)
            print(f"✅ Service '{self.service_name}' stopped successfully")
            return True
            
        except Exception as e:
            print(f"❌ Service stop failed: {e}")
            return False
    
    def restart_service(self):
        """Restart the Windows service"""
        try:
            self.stop_service()
            time.sleep(2)
            self.start_service()
            print(f"✅ Service '{self.service_name}' restarted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Service restart failed: {e}")
            return False
    
    def get_service_status(self):
        """Get the current service status"""
        try:
            status = win32serviceutil.QueryServiceStatus(self.service_name)
            status_map = {
                win32service.SERVICE_STOPPED: "Stopped",
                win32service.SERVICE_START_PENDING: "Starting",
                win32service.SERVICE_STOP_PENDING: "Stopping", 
                win32service.SERVICE_RUNNING: "Running",
                win32service.SERVICE_CONTINUE_PENDING: "Continuing",
                win32service.SERVICE_PAUSE_PENDING: "Pausing",
                win32service.SERVICE_PAUSED: "Paused"
            }
            
            current_status = status_map.get(status[1], f"Unknown ({status[1]})")
            print(f"Service Status: {current_status}")
            return current_status
            
        except Exception as e:
            print(f"❌ Failed to get service status: {e}")
            return "Unknown"
    
    def set_service_startup_type(self, startup_type: str):
        """Set service startup type (auto, manual, disabled)"""
        try:
            import win32service
            
            startup_map = {
                'auto': win32service.SERVICE_AUTO_START,
                'manual': win32service.SERVICE_DEMAND_START,
                'disabled': win32service.SERVICE_DISABLED
            }
            
            if startup_type not in startup_map:
                raise ValueError(f"Invalid startup type: {startup_type}")
            
            # Open service manager
            scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            
            # Open service
            service = win32service.OpenService(scm, self.service_name, win32service.SERVICE_ALL_ACCESS)
            
            # Change service configuration
            win32service.ChangeServiceConfig(
                service,
                win32service.SERVICE_NO_CHANGE,  # serviceType
                startup_map[startup_type],       # startType
                win32service.SERVICE_NO_CHANGE,  # errorControl
                None,                            # binaryPathName
                None,                            # loadOrderGroup
                0,                               # tagId
                None,                            # dependencies
                None,                            # serviceStartName
                None,                            # password
                None                             # displayName
            )
            
            # Close handles
            win32service.CloseServiceHandle(service)
            win32service.CloseServiceHandle(scm)
            
            print(f"✅ Service startup type set to: {startup_type}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set startup type: {e}")
            return False

class SystemTrayApp:
    """System tray application for monitoring and control"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.scheduler = None
        self.running = False
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for system tray app"""
        logger = logging.getLogger("SystemTrayApp")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def create_icon(self):
        """Create system tray icon"""
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color='green')
        draw = ImageDraw.Draw(image)
        draw.ellipse([16, 16, 48, 48], fill='white')
        draw.text((24, 24), 'W', fill='green')
        
        return image
    
    def create_menu(self):
        """Create system tray menu"""
        return pystray.Menu(
            pystray.MenuItem("WiFi Automation", self.show_status),
            pystray.MenuItem("Status", self.show_status),
            pystray.MenuItem("Trigger Morning Slot", self.trigger_morning_slot),
            pystray.MenuItem("Trigger Afternoon Slot", self.trigger_afternoon_slot),
            pystray.MenuItem("Trigger Merge", self.trigger_merge),
            pystray.MenuItem("Exit", self.quit_application)
        )
    
    def show_status(self, icon, item):
        """Show current status"""
        if self.scheduler:
            status = self.scheduler.get_status()
            self.logger.info(f"Status: {status}")
        else:
            self.logger.info("Scheduler not initialized")
    
    def trigger_morning_slot(self, icon, item):
        """Manually trigger morning slot"""
        if self.scheduler:
            result = self.scheduler.manual_trigger_slot("morning")
            self.logger.info(f"Morning slot trigger result: {result}")
        else:
            self.logger.warning("Scheduler not initialized")
    
    def trigger_afternoon_slot(self, icon, item):
        """Manually trigger afternoon slot"""
        if self.scheduler:
            result = self.scheduler.manual_trigger_slot("afternoon")
            self.logger.info(f"Afternoon slot trigger result: {result}")
        else:
            self.logger.warning("Scheduler not initialized")
    
    def trigger_merge(self, icon, item):
        """Manually trigger Excel merge"""
        if self.scheduler:
            result = self.scheduler.manual_trigger_merge()
            self.logger.info(f"Merge trigger result: {result}")
        else:
            self.logger.warning("Scheduler not initialized")
    
    def quit_application(self, icon, item):
        """Quit the application"""
        self.logger.info("Quitting application")
        self.running = False
        if self.scheduler:
            self.scheduler.stop_scheduler()
        icon.stop()
    
    def run(self):
        """Run the system tray application"""
        try:
            self.logger.info("Starting system tray application")
            
            # Initialize scheduler
            self.scheduler = AdvancedScheduler()
            
            # Initialize WiFi app
            wifi_app = CorrectedWiFiApp()
            
            # Set up callbacks
            self.scheduler.set_download_callback(self._wifi_download_callback)
            self.scheduler.set_merge_callback(self._merge_callback)
            
            # Start scheduler
            if self.scheduler.start_scheduler():
                self.logger.info("Scheduler started successfully")
            else:
                self.logger.error("Failed to start scheduler")
                return
            
            # Create and run system tray
            icon = pystray.Icon(
                "WiFi Automation",
                self.create_icon(),
                menu=self.create_menu()
            )
            
            self.running = True
            self.logger.info("System tray application running")
            icon.run()
            
        except Exception as e:
            self.logger.error(f"System tray application error: {e}")
    
    def _wifi_download_callback(self, slot_name: str) -> Dict[str, Any]:
        """Callback for WiFi download execution"""
        try:
            self.logger.info(f"Executing WiFi download for {slot_name} slot")
            
            # Initialize WiFi app for this execution
            wifi_app = CorrectedWiFiApp()
            result = wifi_app.execute_complete_workflow()
            
            if result.get("success", False):
                files_downloaded = result.get("files_downloaded", 0)
                self.logger.info(f"WiFi download completed: {files_downloaded} files")
                return {"success": True, "files_downloaded": files_downloaded}
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"WiFi download failed: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"WiFi download callback error: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _merge_callback(self, result: Dict[str, Any]):
        """Callback for merge completion"""
        try:
            self.logger.info("Excel merge completed successfully")
            self.logger.info(f"Excel file: {result.get('file_path', 'N/A')}")
            
        except Exception as e:
            self.logger.error(f"Merge callback error: {e}")

class WindowsIntegration:
    """Windows integration utilities"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.service_name = "WiFiAutomationService"
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("WindowsIntegration")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def install_service(self) -> bool:
        """Install Windows service"""
        try:
            self.logger.info("Installing Windows service")
            
            # Install service
            win32serviceutil.InstallService(
                WiFiAutomationService,
                self.service_name,
                "WiFi Data Automation Service"
            )
            
            self.logger.info("Windows service installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install service: {e}")
            return False
    
    def remove_service(self) -> bool:
        """Remove Windows service"""
        try:
            self.logger.info("Removing Windows service")
            
            # Stop service if running
            self.stop_service()
            
            # Remove service
            win32serviceutil.RemoveService(self.service_name)
            
            self.logger.info("Windows service removed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove service: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start Windows service"""
        try:
            self.logger.info("Starting Windows service")
            
            win32serviceutil.StartService(self.service_name)
            
            self.logger.info("Windows service started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop Windows service"""
        try:
            self.logger.info("Stopping Windows service")
            
            win32serviceutil.StopService(self.service_name)
            
            self.logger.info("Windows service stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop service: {e}")
            return False
    
    def add_to_startup(self) -> bool:
        """Add application to Windows startup"""
        try:
            self.logger.info("Adding to Windows startup")
            
            # Get current script path
            script_path = Path(__file__).parent.parent / "main.py"
            python_path = sys.executable
            
            # Create startup command
            startup_command = f'"{python_path}" "{script_path}" --tray'
            
            # Add to registry
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(
                key,
                "WiFiAutomation",
                0,
                winreg.REG_SZ,
                startup_command
            )
            
            winreg.CloseKey(key)
            
            self.logger.info("Added to Windows startup successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add to startup: {e}")
            return False
    
    def remove_from_startup(self) -> bool:
        """Remove application from Windows startup"""
        try:
            self.logger.info("Removing from Windows startup")
            
            # Remove from registry
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.DeleteValue(key, "WiFiAutomation")
            winreg.CloseKey(key)
            
            self.logger.info("Removed from Windows startup successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove from startup: {e}")
            return False

# Command line interface
def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WiFi Automation Windows Service")
    parser.add_argument("--install", action="store_true", help="Install Windows service")
    parser.add_argument("--remove", action="store_true", help="Remove Windows service")
    parser.add_argument("--start", action="store_true", help="Start Windows service")
    parser.add_argument("--stop", action="store_true", help="Stop Windows service")
    parser.add_argument("--tray", action="store_true", help="Run system tray application")
    parser.add_argument("--add-startup", action="store_true", help="Add to Windows startup")
    parser.add_argument("--remove-startup", action="store_true", help="Remove from Windows startup")
    
    args = parser.parse_args()
    
    integration = WindowsIntegration()
    
    if args.install:
        integration.install_service()
    elif args.remove:
        integration.remove_service()
    elif args.start:
        integration.start_service()
    elif args.stop:
        integration.stop_service()
    elif args.tray:
        tray_app = SystemTrayApp()
        tray_app.run()
    elif args.add_startup:
        integration.add_to_startup()
    elif args.remove_startup:
        integration.remove_from_startup()
    else:
        print("WiFi Automation Windows Service")
        print("Use --help for available options")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # If no arguments, try to run as service
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(WiFiAutomationService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as e:
            print(f"Service execution error: {e}")
            main()
    else:
        main()