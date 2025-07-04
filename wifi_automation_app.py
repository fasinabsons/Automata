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

# Add current directory to path
sys.path.append('.')

# Import our modules
from modules.advanced_scheduler import AdvancedScheduler
from modules.excel_generator import EnhancedExcelGenerator
from modules.windows_service import SystemTrayApp, WindowsIntegration
from corrected_wifi_app import CorrectedWiFiApp

class WiFiAutomationApp:
    """Main WiFi Automation Application"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.scheduler = AdvancedScheduler()
        self.excel_generator = EnhancedExcelGenerator()
        self.wifi_app = CorrectedWiFiApp()
        self.running = False
        
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
            file_handler = logging.FileHandler(log_file)
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
            
            # Create date-specific directory
            from datetime import datetime
            today = datetime.now().strftime("%d%B").lower()  # e.g., "04july"
            csv_dir = Path(f"EHC_Data/{today}")
            csv_dir.mkdir(parents=True, exist_ok=True)
            
            # Execute WiFi automation
            result = self.wifi_app.execute_complete_workflow()
            
            if result.get("success", False):
                files_downloaded = result.get("files_downloaded", 4)  # Default to 4 networks
                self.logger.info(f"✅ {slot_name} slot completed: {files_downloaded} files downloaded")
                
                # Count actual CSV files
                csv_files = list(csv_dir.glob("*.csv"))
                actual_files = len(csv_files)
                
                return {
                    "success": True, 
                    "files_downloaded": actual_files,
                    "slot_name": slot_name,
                    "csv_directory": str(csv_dir)
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
            
            # Log daily summary
            self._log_daily_summary(result)
            
        except Exception as e:
            self.logger.error(f"Merge callback error: {e}")
    
    def _log_daily_summary(self, excel_result: Dict[str, Any]):
        """Log daily summary statistics"""
        try:
            from datetime import datetime
            
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

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="WiFi Automation Application")
    
    # Execution modes
    parser.add_argument("--console", action="store_true", help="Run in console mode")
    parser.add_argument("--tray", action="store_true", help="Run in system tray mode")
    
    # Manual triggers
    parser.add_argument("--trigger-morning", action="store_true", help="Manually trigger morning slot")
    parser.add_argument("--trigger-afternoon", action="store_true", help="Manually trigger afternoon slot")
    parser.add_argument("--trigger-merge", action="store_true", help="Manually trigger Excel merge")
    
    # Status and testing
    parser.add_argument("--status", action="store_true", help="Show application status")
    parser.add_argument("--test-excel", action="store_true", help="Test Excel generation")
    parser.add_argument("--test-scheduler", action="store_true", help="Test scheduler")
    
    # Windows service integration
    parser.add_argument("--install-service", action="store_true", help="Install Windows service")
    parser.add_argument("--remove-service", action="store_true", help="Remove Windows service")
    parser.add_argument("--start-service", action="store_true", help="Start Windows service")
    parser.add_argument("--stop-service", action="store_true", help="Stop Windows service")
    parser.add_argument("--add-startup", action="store_true", help="Add to Windows startup")
    parser.add_argument("--remove-startup", action="store_true", help="Remove from Windows startup")
    
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
    
    # Handle execution modes
    if args.console:
        app.run_console_mode()
    elif args.tray:
        app.run_tray_mode()
    else:
        # Default behavior - show help and run interactive mode
        print("🤖 WiFi Automation Application")
        print("=" * 50)
        print("Available modes:")
        print("  --console     : Run in console mode")
        print("  --tray        : Run in system tray mode")
        print("")
        print("Manual triggers:")
        print("  --trigger-morning   : Trigger morning slot")
        print("  --trigger-afternoon : Trigger afternoon slot")
        print("  --trigger-merge     : Trigger Excel merge")
        print("")
        print("Testing:")
        print("  --test-excel     : Test Excel generation")
        print("  --test-scheduler : Test scheduler")
        print("  --status         : Show status")
        print("")
        print("Windows integration:")
        print("  --install-service : Install Windows service")
        print("  --add-startup     : Add to Windows startup")
        print("")
        
        # Ask user what they want to do
        choice = input("What would you like to do? (console/tray/test): ").strip().lower()
        
        if choice == "console":
            app.run_console_mode()
        elif choice == "tray":
            app.run_tray_mode()
        elif choice == "test":
            print("Running Excel generation test...")
            from modules.excel_generator import test_excel_generation
            test_excel_generation()
        else:
            print("Invalid choice. Use --help for more options.")

if __name__ == "__main__":
    main()