#!/usr/bin/env python3
"""
Enhanced WiFi Service Runner with Dynamic Files and 8-File Minimum Guarantee
Now with FAST automation for improved performance
"""

import os
import sys
import time
import json
import logging
import schedule
import traceback
import subprocess
import winreg
import psutil
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import components
from modules.dynamic_file_manager import DynamicFileManager
from working_email_notifications import WorkingEmailNotifications
from corrected_wifi_app import CorrectedWiFiApp  # Fast version
from modules.efficient_vbs_controller import EfficientVBSController  # VBS automation

# Configuration
BUSINESS_HOURS_START = 9  # 9 AM
BUSINESS_HOURS_END = 17   # 5 PM
MINIMUM_FILES_REQUIRED = 8

class EnhancedWiFiServiceWithDynamicFiles:
    """Enhanced WiFi Service with Dynamic Files, Fast Automation, and VBS Integration"""
    
    def __init__(self):
        self.running = False
        self.crash_count = 0
        self.max_crashes = 5
        self.restart_delay = 30
        self.last_crash_time = None
        self.last_successful_run = None
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = datetime.now()
        
        # Dynamic file system
        self.file_manager = DynamicFileManager()
        self.minimum_files_required = MINIMUM_FILES_REQUIRED
        
        # Business hours
        self.business_hours_start = BUSINESS_HOURS_START
        self.business_hours_end = BUSINESS_HOURS_END
        
        # Daily tracking
        self.daily_files_downloaded = 0
        self.excel_generated_today = False
        self.vbs_automation_completed_today = False
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.setup_components()
        
        # Initialize email service
        self.email_service = WorkingEmailNotifications()
        
        # Initialize VBS controller
        self.vbs_controller = EfficientVBSController()
        
        # Initialize dynamic file system
        self.initialize_dynamic_system()
        
        self.logger.info("✅ Enhanced WiFi Service with Dynamic Files and VBS Integration initialized")
    
    def setup_logging(self):
        """Setup logging with crash logging"""
        try:
            # Main logger
            self.logger = logging.getLogger("EnhancedWiFiService")
            self.logger.setLevel(logging.INFO)
            
            # Crash logger
            self.crash_logger = logging.getLogger("CrashLogger")
            self.crash_logger.setLevel(logging.ERROR)
            
            # Create handlers if they don't exist
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                
                # File handler
                log_file = project_root / "EHC_Logs" / "enhanced_service.log"
                log_file.parent.mkdir(exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"❌ Logging setup failed: {e}")
    
    def setup_components(self):
        """Initialize FAST components with error handling"""
        try:
            self.logger.info("🔧 Initializing FAST WiFi components...")
            
            # Initialize FAST WiFi automation with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.wifi_app = CorrectedWiFiApp()  # Fast version
                    self.logger.info("✅ FAST WiFi automation initialized")
                    break
                except Exception as e:
                    self.logger.error(f"❌ WiFi app init attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(5)
            
            self.logger.info("✅ All FAST components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            self.handle_crash(e, "Component initialization")
            raise
    
    def initialize_dynamic_system(self):
        """Initialize dynamic file system and check 8-file minimum"""
        try:
            self.logger.info("📁 Initializing dynamic file system...")
            
            # Create today's folder if it doesn't exist
            today_folder = self.file_manager.get_download_directory()
            self.logger.info(f"📁 Today's folder: {today_folder}")
            
            # Check current file status
            status = self.file_manager.get_current_date_folder_status()
            current_files = status['csv_count']
            
            self.logger.info(f"📊 Current CSV files: {current_files}/{self.minimum_files_required}")
            
            # Check if we need to download files to meet minimum
            if current_files < self.minimum_files_required:
                files_needed = self.minimum_files_required - current_files
                self.logger.warning(f"⚠️ Only {current_files} files found, need {files_needed} more files")
                
                # Check if we're in business hours
                if self.is_business_hours():
                    self.logger.info("🕐 In business hours, will ensure minimum files")
                    # The ensure_minimum_files will be called during health checks
                else:
                    self.logger.info("🌙 Outside business hours, will check again during business hours")
            else:
                self.logger.info("✅ Sufficient files for Excel generation")
            
            # Schedule daily folder creation at midnight
            schedule.every().day.at("00:00").do(self.create_daily_folder)
            
            # Schedule monthly cleanup
            schedule.every().month.do(self.file_manager.cleanup_old_files)
            
            self.logger.info("✅ Dynamic file system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Dynamic file system initialization failed: {e}")
            # Don't crash the service for this
    
    def is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        current_hour = datetime.now().hour
        return self.business_hours_start <= current_hour <= self.business_hours_end
    
    def create_daily_folder(self):
        """Create new daily folder at midnight"""
        try:
            self.logger.info("🌅 Creating new daily folder at midnight...")
            
            # Create new folder
            new_folder = self.file_manager.get_download_directory()
            self.logger.info(f"📁 Created new folder: {new_folder}")
            
            # Reset daily counters
            self.daily_files_downloaded = 0
            self.excel_generated_today = False
            
            # Send notification
            self.email_service.send_daily_folder_notification(str(new_folder))
            
            self.logger.info("✅ Daily folder creation completed")
            
        except Exception as e:
            self.logger.error(f"❌ Daily folder creation failed: {e}")
    
    def ensure_minimum_files(self) -> bool:
        """Ensure minimum 8 files are available - triggers FAST downloads if needed"""
        try:
            if not self.is_business_hours():
                self.logger.info("🌙 Outside business hours, skipping file minimum check")
                return True
            
            # Check current file count
            status = self.file_manager.get_current_date_folder_status()
            current_files = status['csv_count']
            
            if current_files >= self.minimum_files_required:
                self.logger.info(f"✅ Sufficient files: {current_files}/{self.minimum_files_required}")
                return True
            
            files_needed = self.minimum_files_required - current_files
            self.logger.warning(f"⚠️ Insufficient files: {current_files}/{self.minimum_files_required}, need {files_needed} more")
            
            # Trigger FAST download to meet minimum
            self.logger.info("🚀 Triggering FAST CSV download to meet 8-file minimum...")
            
            # Run the ROBUST download with retry and refresh
            result = self.wifi_app.run_robust_automation()
            
            if result and result.get("success"):
                # Get file count after download
                status_after = self.file_manager.get_current_date_folder_status()
                files_after = status_after['csv_count']
                new_files = files_after - current_files
                
                self.daily_files_downloaded += new_files
                self.last_successful_run = datetime.now()
                
                self.logger.info(f"✅ FAST download successful! Added {new_files} files (total: {files_after})")
                
                # Send download notification
                self.email_service.send_csv_download_notification(
                    slot_name="robust",
                    files_downloaded=new_files,
                    total_files=files_after,
                    success=True
                )
                
                # Check if we should generate Excel (8 files reached)
                if files_after >= self.minimum_files_required and not self.excel_generated_today:
                    self.logger.info(f"📊 {files_after} files reached, triggering Excel generation...")
                    self.generate_excel_file()
                
                return True
            else:
                error_msg = result.get("error", "Unknown error") if result else "No result returned"
                self.logger.error(f"❌ FAST download failed: {error_msg}")
                
                # Send failure notification
                status_after = self.file_manager.get_current_date_folder_status()
                self.email_service.send_csv_download_notification(
                    slot_name="robust",
                    files_downloaded=0,
                    total_files=status_after['csv_count'],
                    success=False
                )
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error ensuring minimum files: {e}")
            return False
    
    def handle_crash(self, error: Exception, context: str):
        """Handle crashes with logging and recovery"""
        self.crash_count += 1
        self.last_crash_time = datetime.now()
        
        crash_info = {
            "timestamp": self.last_crash_time.isoformat(),
            "crash_count": self.crash_count,
            "context": context,
            "error": str(error),
            "traceback": traceback.format_exc()
        }
        
        self.crash_logger.error(f"🚨 CRASH #{self.crash_count} in {context}")
        self.crash_logger.error(f"Error: {error}")
        self.crash_logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Save crash info to file
        crash_file = project_root / "EHC_Logs" / f"crash_{int(time.time())}.json"
        crash_file.parent.mkdir(exist_ok=True)
        with open(crash_file, 'w') as f:
            json.dump(crash_info, f, indent=2)
        
        # Check if we should restart
        if self.crash_count >= self.max_crashes:
            self.logger.error(f"🚨 Maximum crashes ({self.max_crashes}) reached, initiating system restart")
            self.restart_system()
        else:
            self.logger.info(f"🔄 Crash {self.crash_count}/{self.max_crashes}, attempting recovery in {self.restart_delay} seconds")
            time.sleep(self.restart_delay)
    
    def restart_system(self):
        """Restart the entire system"""
        try:
            self.logger.info("🔄 Initiating system restart...")
            
            # Save current state
            state_file = project_root / "service_state.json"
            state = {
                "last_restart": datetime.now().isoformat(),
                "crash_count": self.crash_count,
                "daily_files": self.daily_files_downloaded,
                "excel_generated": self.excel_generated_today
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Restart the service
            python_exe = sys.executable
            script_path = __file__
            
            # Start new instance
            subprocess.Popen([python_exe, script_path], 
                           cwd=str(project_root),
                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            # Exit current instance
            self.logger.info("✅ New service instance started, exiting current instance")
            sys.exit(0)
            
        except Exception as e:
            self.logger.error(f"❌ System restart failed: {e}")
            # Last resort - Windows restart
            os.system("shutdown /r /t 300 /c 'WiFi Service restart - System will restart in 5 minutes'")
    
    def load_previous_state(self):
        """Load previous service state"""
        try:
            state_file = project_root / "service_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                self.daily_files_downloaded = state.get("daily_files", 0)
                self.excel_generated_today = state.get("excel_generated", False)
                
                self.logger.info(f"📊 Loaded previous state: {self.daily_files_downloaded} files, Excel: {self.excel_generated_today}")
                
                # Clean up state file
                state_file.unlink()
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load previous state: {e}")
    
    def add_to_startup(self):
        """Add to Windows startup with enhanced registry entry"""
        try:
            # Get current script path
            script_path = Path(__file__).absolute()
            python_exe = sys.executable
            
            # Create startup command
            startup_cmd = f'"{python_exe}" "{script_path}" --startup'
            
            # Registry key for startup
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Add to startup
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(
                    reg_key,
                    "EnhancedWiFiService",
                    0,
                    winreg.REG_SZ,
                    startup_cmd
                )
            
            self.logger.info("✅ Added to Windows startup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add to startup: {e}")
            return False
    
    def health_check(self):
        """Perform health check with 8-file minimum monitoring"""
        try:
            current_time = datetime.now()
            
            # Check if health check is due
            if (current_time - self.last_health_check).total_seconds() < self.health_check_interval:
                return True
            
            self.logger.info("🏥 Performing health check...")
            
            # Check memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > 500:  # 500MB threshold
                self.logger.warning(f"⚠️ High memory usage: {memory_mb:.1f}MB")
            
            # Check disk space
            disk_usage = psutil.disk_usage(str(project_root))
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            
            if free_gb < 1:  # 1GB threshold
                self.logger.warning(f"⚠️ Low disk space: {free_gb:.1f}GB")
            
            # Check dynamic file system status
            try:
                status = self.file_manager.get_current_date_folder_status()
                current_files = status['csv_count']
                
                self.logger.info(f"📊 Health check - Files: {current_files}/{self.minimum_files_required}")
                
                # Ensure minimum files if in business hours
                if self.is_business_hours() and current_files < self.minimum_files_required:
                    self.logger.info("🚨 Health check detected insufficient files, triggering ensure_minimum_files")
                    self.ensure_minimum_files()
                    
            except Exception as e:
                self.logger.error(f"❌ File system health check failed: {e}")
            
            self.last_health_check = current_time
            self.logger.info("✅ Health check completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return False
    
    def generate_excel_file(self):
        """Generate Excel file from CSV files and trigger VBS automation"""
        try:
            self.logger.info("📊 Generating Excel file from CSV files...")
            
            # Check if we have enough files
            status = self.file_manager.get_current_date_folder_status()
            current_files = status['csv_count']
            
            if current_files < self.minimum_files_required:
                self.logger.warning(f"⚠️ Not enough files for Excel generation: {current_files}/{self.minimum_files_required}")
                return False
            
            # Generate Excel file
            from modules.excel_generator import ExcelGenerator
            excel_generator = ExcelGenerator()
            
            result = excel_generator.create_excel_from_csv_files()
            
            if result.get('success', False):
                excel_file = result.get('excel_file')
                self.logger.info(f"✅ Excel file generated: {excel_file}")
                
                # Mark Excel as generated today
                self.excel_generated_today = True
                
                # Send Excel generation notification
                self.email_service.send_excel_generation_notification(excel_file)
                
                # Trigger VBS automation if enabled
                if not self.vbs_automation_completed_today:
                    self.logger.info("🏢 Triggering VBS automation after Excel generation...")
                    self.run_vbs_automation()
                
                return True
            else:
                self.logger.error("❌ Excel generation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Excel generation error: {e}")
            return False
    
    def run_vbs_automation(self):
        """Run VBS automation with the current date folder"""
        try:
            self.logger.info("🏢 Starting VBS automation...")
            
            # Get current date folder
            date_folder = self.file_manager.get_current_date_folder()
            
            # Initialize VBS controller if not already done
            if not self.vbs_controller.is_initialized:
                init_result = self.vbs_controller.initialize()
                if not init_result["success"]:
                    self.logger.error(f"❌ VBS initialization failed: {init_result['error']}")
                    return False
            
            # Run complete VBS automation
            vbs_result = self.vbs_controller.run_complete_vbs_automation(date_folder)
            
            if vbs_result["success"]:
                self.logger.info("✅ VBS automation completed successfully")
                self.vbs_automation_completed_today = True
                
                # Send success notification with PDF
                pdf_file = vbs_result.get("pdf_file")
                if pdf_file:
                    self.email_service.send_vbs_completion_notification(pdf_file, date_folder)
                
                return True
            else:
                self.logger.error(f"❌ VBS automation failed: {vbs_result['errors']}")
                
                # Send failure notification
                self.email_service.send_vbs_failure_notification(vbs_result['errors'], date_folder)
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ VBS automation error: {e}")
            
            # Send error notification
            self.email_service.send_vbs_error_notification(str(e))
            
            return False
    
    def check_vbs_automation_status(self) -> bool:
        """Check if VBS automation is available and ready"""
        try:
            return self.vbs_controller.is_vbs_available()
        except Exception as e:
            self.logger.error(f"❌ VBS status check failed: {e}")
            return False
    
    def reset_daily_counters(self):
        """Reset daily counters at midnight"""
        try:
            self.logger.info("🔄 Resetting daily counters...")
            
            # Reset counters
            self.daily_files_downloaded = 0
            self.excel_generated_today = False
            self.vbs_automation_completed_today = False
            
            # Create new daily folder
            self.create_daily_folder()
            
            self.logger.info("✅ Daily counters reset successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Daily counter reset failed: {e}")
    
    def schedule_tasks(self):
        """Schedule regular FAST tasks - DAY ONLY (no night downloads)"""
        try:
            self.logger.info("🕐 Scheduling FAST daytime tasks only...")
            
            # Clear existing jobs
            schedule.clear()
            
            # Schedule permanent FAST tasks - DAY ONLY
            schedule.every().day.at("09:30").do(self.run_fast_wifi_download, "morning").tag('permanent')
            schedule.every().day.at("13:00").do(self.run_fast_wifi_download, "afternoon").tag('permanent')
            schedule.every().day.at("13:30").do(self.run_fast_wifi_download, "afternoon_backup").tag('permanent')
            
            # Remove evening slots - NO NIGHT DOWNLOADS
            # schedule.every().day.at("21:05").do(self.run_fast_wifi_download, "evening").tag('permanent')
            # schedule.every().day.at("21:11").do(self.run_fast_wifi_download, "evening_backup").tag('permanent')
            
            schedule.every().day.at("00:00").do(self.reset_daily_counters).tag('permanent')
            
            # Schedule health checks
            schedule.every(5).minutes.do(self.health_check).tag('health')
            
            self.logger.info("✅ FAST daytime tasks scheduled (NO NIGHT DOWNLOADS):")
            self.logger.info("   🌅 Morning slot: 09:30 (09:30 AM) - FAST")
            self.logger.info("   🌞 Afternoon slot: 13:00 (1:00 PM) - FAST")
            self.logger.info("   🌞 Afternoon backup: 13:30 (1:30 PM) - FAST")
            self.logger.info("   🚫 Evening slots: DISABLED (no night downloads)")
            self.logger.info("   🔄 Daily reset: 00:00")
            self.logger.info("   🏥 Health check: Every 5 minutes")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule tasks: {e}")
            self.handle_crash(e, "Task scheduling")
    
    def add_temporary_schedule(self, time_str: str, description: str = "temporary"):
        """Add temporary FAST schedule for testing"""
        try:
            self.logger.info(f"🧪 Adding temporary FAST schedule: {time_str} ({description})")
            
            # Parse time
            current_time = datetime.now()
            hour, minute = map(int, time_str.split(':'))
            
            # Create datetime for today
            test_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, schedule for tomorrow
            if test_time <= current_time:
                test_time += timedelta(days=1)
                self.logger.info(f"🕐 Time has passed today, scheduling for tomorrow: {test_time}")
            else:
                self.logger.info(f"🕐 Scheduling for today: {test_time}")
            
            # Add temporary FAST schedule
            schedule.every().day.at(time_str).do(self.run_fast_wifi_download, f"temporary-{description}").tag('temporary')
            
            self.logger.info(f"✅ Temporary FAST schedule added: {time_str}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add temporary schedule: {e}")
            return False
    
    def clear_temporary_schedules(self):
        """Clear all temporary schedules"""
        try:
            schedule.clear('temporary')
            self.logger.info("✅ Temporary schedules cleared")
        except Exception as e:
            self.logger.error(f"❌ Failed to clear temporary schedules: {e}")
    
    def start_service(self):
        """Start the enhanced FAST service"""
        try:
            self.logger.info("🚀 Starting Enhanced FAST WiFi Automation Service...")
            
            self.running = True
            
            # Load previous state
            self.load_previous_state()
            
            # Add to startup
            self.add_to_startup()
            
            # Schedule regular FAST tasks
            self.schedule_tasks()
            
            # Add temporary schedule for immediate testing
            current_time = datetime.now()
            # Add a test schedule 2 minutes from now
            test_time = current_time + timedelta(minutes=2)
            test_time_str = test_time.strftime("%H:%M")
            self.add_temporary_schedule(test_time_str, "immediate-test")
            self.logger.info(f"🧪 Added immediate FAST test schedule for {test_time_str}")
            
            self.logger.info("✅ Enhanced FAST WiFi Service started successfully")
            
            # Service loop
            while self.running:
                try:
                    # Run scheduled tasks
                    schedule.run_pending()
                    
                    # Sleep for a short time
                    time.sleep(10)  # Check every 10 seconds
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Keyboard interrupt received, stopping service...")
                    self.running = False
                    break
                except Exception as e:
                    self.logger.error(f"❌ Service loop error: {e}")
                    self.handle_crash(e, "Service loop")
            
            self.logger.info("✅ Enhanced FAST WiFi Service stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start service: {e}")
            self.handle_crash(e, "Service startup")
    
    def stop_service(self):
        """Stop the service"""
        try:
            self.logger.info("🛑 Stopping Enhanced FAST WiFi Service...")
            self.running = False
            
            # Clear all schedules
            schedule.clear()
            
            self.logger.info("✅ Enhanced FAST WiFi Service stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop service: {e}")
    
    def get_service_status(self):
        """Get current service status"""
        try:
            status = {
                "running": self.running,
                "crash_count": self.crash_count,
                "last_successful_run": self.last_successful_run.isoformat() if self.last_successful_run else None,
                "daily_files_downloaded": self.daily_files_downloaded,
                "excel_generated_today": self.excel_generated_today,
                "vbs_automation_completed_today": self.vbs_automation_completed_today,
                "scheduled_jobs": len(schedule.jobs),
                "file_system_status": self.file_manager.get_current_date_folder_status(),
                "business_hours": self.is_business_hours(),
                "automation_type": "FAST + VBS",
                "vbs_available": self.check_vbs_automation_status()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get service status: {e}")
            return {"error": str(e)}

def main():
    """Main function"""
    try:
        # Check for startup argument
        startup_mode = "--startup" in sys.argv
        
        if startup_mode:
            print("🚀 Starting Enhanced FAST WiFi Service in startup mode...")
        else:
            print("🚀 Starting Enhanced FAST WiFi Service in manual mode...")
        
        # Create and start service
        service = EnhancedWiFiServiceWithDynamicFiles()
        service.start_service()
        
    except KeyboardInterrupt:
        print("\n🛑 Service interrupted by user")
    except Exception as e:
        print(f"❌ Service failed to start: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 