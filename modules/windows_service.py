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
from pathlib import Path
from typing import Dict, Any, Optional
import win32serviceutil
import win32service
import win32event
import servicemanager
import pystray
from PIL import Image, ImageDraw
import winreg

# Import our modules
sys.path.append('.')
from modules.advanced_scheduler import AdvancedScheduler
from corrected_wifi_app import CorrectedWiFiApp

class WiFiAutomationService(win32serviceutil.ServiceFramework):
    """Windows Service for WiFi Automation"""
    
    _svc_name_ = "WiFiAutomationService"
    _svc_display_name_ = "WiFi Data Automation Service"
    _svc_description_ = "Automated WiFi data collection and Excel generation service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._setup_logging()
        self.scheduler = None
        self.wifi_app = None
        self.running = False
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Windows service"""
        logger = logging.getLogger("WiFiAutomationService")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / "wifi_automation_service.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        return logger
    
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        
        # Stop scheduler
        if self.scheduler:
            self.scheduler.stop_scheduler()
            
        self.logger.info("Service stopped")
    
    def SvcDoRun(self):
        """Run the service"""
        self.logger.info("Service starting")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        
        self.running = True
        self.main()
    
    def main(self):
        """Main service logic"""
        try:
            self.logger.info("Initializing WiFi automation service")
            
            # Initialize scheduler
            self.scheduler = AdvancedScheduler()
            
            # Initialize WiFi app
            self.wifi_app = CorrectedWiFiApp()
            
            # Set up callbacks
            self.scheduler.set_download_callback(self._wifi_download_callback)
            self.scheduler.set_merge_callback(self._merge_callback)
            
            # Start scheduler
            if self.scheduler.start_scheduler():
                self.logger.info("Scheduler started successfully")
            else:
                self.logger.error("Failed to start scheduler")
                return
            
            self.logger.info("WiFi automation service is running")
            
            # Wait for stop signal
            while self.running:
                rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if rc == win32event.WAIT_OBJECT_0:
                    break
            
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            servicemanager.LogErrorMsg(f"Service error: {e}")
    
    def _wifi_download_callback(self, slot_name: str) -> Dict[str, Any]:
        """Callback for WiFi download execution"""
        try:
            self.logger.info(f"Executing WiFi download for {slot_name} slot")
            
            # Execute WiFi automation
            result = self.wifi_app.execute_complete_workflow()
            
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
            
            # Here you could add additional post-merge actions
            # like email notifications, file uploads, etc.
            
        except Exception as e:
            self.logger.error(f"Merge callback error: {e}")

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
            win32serviceutil.HandleCommandLine(WiFiAutomationService)
        except Exception as e:
            print(f"Service error: {e}")
            main()
    else:
        main()