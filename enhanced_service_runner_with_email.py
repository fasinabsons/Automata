#!/usr/bin/env python3
"""
Enhanced WiFi Service Runner with Email Notifications
Includes crash prevention, auto-restart, health monitoring, and email notifications
"""

import os
import sys
import time
import json
import winreg
import psutil
import schedule
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.logger import logger
from corrected_wifi_app import CorrectedWiFiApp

class EnhancedWiFiServiceWithEmail:
    """
    Enhanced WiFi Service with comprehensive crash prevention and email notifications
    """
    
    def __init__(self):
        self.running = False
        self.crash_count = 0
        self.max_crashes = 5
        self.last_restart_time = None
        self.restart_delay = 300  # 5 minutes
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = datetime.now()
        
        # Daily tracking
        self.daily_files_downloaded = 0
        self.excel_generated_today = False
        self.last_successful_run = None
        
        # Setup logging
        self.setup_logging()
        
        # Setup components
        self.setup_components()
        
        self.logger.info("🚀 Enhanced WiFi Service with Email Notifications initialized")
    
    def setup_logging(self):
        """Setup enhanced logging"""
        self.logger = logger
        self.logger.info("📋 Enhanced service logging initialized")
    
    def setup_components(self):
        """Setup service components"""
        try:
            # Initialize WiFi app
            self.wifi_app = CorrectedWiFiApp()
            self.logger.info("✅ WiFi automation app initialized")
            
            # Initialize working email service
            try:
                from working_email_notifications import WorkingEmailNotifications
                self.email_service = WorkingEmailNotifications()
                self.logger.info("✅ Working email service initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Working email service initialization failed: {e}")
                self.email_service = None
            
            # Create directories
            directories = [
                "logs", "EHC_Data", "EHC_Data_Merge", 
                "EHC_Data_Pdf", "downloads"
            ]
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            self.logger.info("✅ Service components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    def send_download_notification(self, slot_name: str, files_downloaded: int, success: bool = True):
        """Send email notification for download completion"""
        try:
            if not self.email_service:
                self.logger.warning("Email service not available for notifications")
                return
            
            # Get total files count
            total_files = self.daily_files_downloaded
            
            # Send notification using working email service
            email_success = self.email_service.send_csv_download_notification(
                slot_name=slot_name,
                files_downloaded=files_downloaded,
                total_files=total_files,
                success=success
            )
            
            if email_success:
                self.logger.info(f"📧 Download notification sent successfully for {slot_name}")
            else:
                self.logger.warning(f"📧 Failed to send download notification for {slot_name}")
                
        except Exception as e:
            self.logger.error(f"Error sending download notification: {e}")
            # Don't fail the entire process for email issues
    
    def handle_crash(self, error: Exception, context: str):
        """Handle system crashes with recovery"""
        self.crash_count += 1
        
        self.logger.error(f"💥 CRASH #{self.crash_count}: {context}")
        self.logger.error(f"💥 Error: {error}")
        
        # Send crash notification email
        try:
            if self.email_service:
                subject = f"🚨 System Crash Alert - {context}"
                body = f"""URGENT: WiFi Automation System Crash

Crash Details:
📅 Date: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
💥 Context: {context}
❌ Error: {str(error)}
🔄 Crash Count: {self.crash_count}/{self.max_crashes}

The system has encountered an error and is attempting automatic recovery.

System will restart automatically if crash count is below threshold.

Please check system logs for detailed information.

Best regards,
WiFi Automation System
"""
                self.email_service.send_email(subject=subject, body=body)
        except:
            pass  # Don't fail on email notification errors
        
        if self.crash_count >= self.max_crashes:
            self.logger.critical(f"🛑 MAX CRASHES REACHED ({self.max_crashes})")
            self.logger.critical("🛑 Service will stop to prevent infinite restart loop")
            self.running = False
            return
        
        self.logger.info(f"🔄 Initiating restart in {self.restart_delay} seconds...")
        time.sleep(self.restart_delay)
        
        try:
            self.restart_system()
        except Exception as restart_error:
            self.logger.error(f"❌ Restart failed: {restart_error}")
            self.crash_count += 1
    
    def restart_system(self):
        """Restart system components"""
        try:
            self.logger.info("🔄 Restarting system components...")
            
            # Cleanup old components
            if hasattr(self, 'wifi_app'):
                try:
                    self.wifi_app.cleanup()
                except:
                    pass
            
            # Reinitialize components
            self.setup_components()
            
            self.last_restart_time = datetime.now()
            self.logger.info("✅ System restart completed")
            
        except Exception as e:
            self.logger.error(f"❌ System restart failed: {e}")
            raise
    
    def run_wifi_download(self, slot_name="scheduled"):
        """Run WiFi download and check for 8-file Excel trigger"""
        self.logger.info(f"🔄 Starting WiFi download - {slot_name}")
        
        try:
            # Check if already generated Excel today
            if self.excel_generated_today:
                self.logger.info("📊 Excel already generated today, skipping additional generation")
                return True
            
            # Run WiFi automation
            result = self.wifi_app.run_corrected_automation()
            
            if result.get('success', False):
                files_downloaded = result.get('files_downloaded', 0)
                self.daily_files_downloaded += files_downloaded
                
                self.logger.info(f"✅ WiFi download completed: {files_downloaded} files downloaded")
                self.logger.info(f"📊 Total files today: {self.daily_files_downloaded}")
                
                # Send download notification
                self.send_download_notification(slot_name, files_downloaded, success=True)
                
                # Check if we have 8 files total (2 downloads × 4 files each)
                if self.daily_files_downloaded >= 8:
                    self.logger.info("🎯 Reached 8 files - triggering Excel generation!")
                    
                    # Generate Excel file
                    excel_success = self.generate_excel_file()
                    
                    if excel_success:
                        self.logger.info("✅ Excel generation completed after 8 files")
                        self.excel_generated_today = True
                    else:
                        self.logger.error("❌ Excel generation failed after 8 files")
                else:
                    self.logger.info(f"📊 Need {8 - self.daily_files_downloaded} more files for Excel generation")
                
                return True
            else:
                self.logger.error(f"❌ WiFi download failed for {slot_name}")
                
                # Send failure notification
                self.send_download_notification(slot_name, 0, success=False)
                return False
                
        except Exception as e:
            self.logger.error(f"❌ WiFi download error: {e}")
            self.handle_crash(e, "WiFi download")
            
            # Send failure notification
            self.send_download_notification(slot_name, 0, success=False)
            return False
    
    def generate_excel_file(self):
        """Generate Excel file using 8-file trigger logic"""
        try:
            self.logger.info("📊 Checking for Excel generation...")
            
            # Import the new processor
            from modules.csv_to_excel_processor import CSVToExcelProcessor
            
            # Get today's CSV directory
            today = datetime.now().strftime("%d%b").lower()
            csv_dir = Path(f"EHC_Data/{today}")
            
            if not csv_dir.exists():
                self.logger.error(f"CSV directory not found: {csv_dir}")
                return False
            
            # Use the new processor
            processor = CSVToExcelProcessor()
            
            # Check if we should generate Excel (8 files)
            if not processor.should_generate_excel(csv_dir):
                file_count = processor.count_csv_files(csv_dir)
                self.logger.info(f"📊 Not enough files for Excel generation. Have {file_count}, need 8")
                return False
            
            # Process and generate Excel
            result = processor.process_and_generate_excel(csv_dir)
            
            if result.get('success', False):
                excel_file = result.get('file_path')
                records_written = result.get('records_written', 0)
                
                self.logger.info(f"✅ Excel file generated: {excel_file}")
                self.logger.info(f"📊 Records processed: {records_written}")
                
                # Send Excel generation notification
                try:
                    if self.email_service:
                        email_success = self.email_service.send_excel_generation_notification(
                            excel_file=excel_file,
                            records_count=records_written
                        )
                        if email_success:
                            self.logger.info("📧 Excel generation notification sent")
                        else:
                            self.logger.warning("📧 Excel generation notification failed")
                except Exception as e:
                    self.logger.warning(f"Email notification failed: {e}")
                
                return True
            else:
                self.logger.error(f"❌ Excel generation failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Excel generation error: {e}")
            self.handle_crash(e, "Excel generation")
            return False
    
    def ensure_minimum_files(self):
        """Ensure we have minimum 8 files by triggering downloads if needed"""
        try:
            self.logger.info("📊 Checking for minimum 8 files requirement...")
            
            # Import dynamic file manager
            from modules.dynamic_file_manager import DynamicFileManager
            file_manager = DynamicFileManager()
            
            # Count CSV files in today's folder
            current_files = file_manager.count_csv_files_today()
            
            if current_files >= 8:
                self.logger.info(f"✅ Sufficient files found: {current_files}/8")
                return True
            
            files_needed = 8 - current_files
            self.logger.info(f"⚠️ Insufficient files: {current_files}/8 (need {files_needed} more)")
            self.logger.info("🚀 Triggering additional downloads to reach 8 files minimum...")
            
            # Trigger downloads to reach 8 files
            downloads_triggered = 0
            max_attempts = 3  # Maximum 3 download attempts
            
            for attempt in range(max_attempts):
                if current_files >= 8:
                    break
                    
                self.logger.info(f"📥 Download attempt {attempt + 1}/{max_attempts}")
                
                # Trigger a download
                download_success = self.run_wifi_download(f"minimum_files_attempt_{attempt + 1}")
                
                if download_success:
                    downloads_triggered += 1
                    # Re-count files
                    current_files = file_manager.count_csv_files_today()
                    self.logger.info(f"📊 Files after download: {current_files}/8")
                else:
                    self.logger.warning(f"❌ Download attempt {attempt + 1} failed")
                
                # Wait between attempts
                if current_files < 8 and attempt < max_attempts - 1:
                    self.logger.info("⏳ Waiting 30 seconds before next attempt...")
                    time.sleep(30)
            
            # Final check
            final_count = file_manager.count_csv_files_today()
            
            if final_count >= 8:
                self.logger.info(f"✅ Minimum files achieved: {final_count}/8")
                self.logger.info(f"📥 Downloads triggered: {downloads_triggered}")
                return True
            else:
                self.logger.warning(f"⚠️ Could not reach 8 files: {final_count}/8")
                self.logger.warning(f"📥 Downloads triggered: {downloads_triggered}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error ensuring minimum files: {e}")
            return False
    
    def health_check(self):
        """Perform health check and ensure minimum files"""
        try:
            current_time = datetime.now()
            
            # Check if health check is due
            if (current_time - self.last_health_check).total_seconds() < self.health_check_interval:
                return True
            
            self.logger.info("[HEALTH] Performing health check...")
            
            # Check memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > 500:  # 500MB threshold
                self.logger.warning(f"[WARNING] High memory usage: {memory_mb:.1f}MB")
            
            # Check disk space
            disk_usage = psutil.disk_usage(str(project_root))
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            
            if free_gb < 1:  # 1GB threshold
                self.logger.warning(f"[WARNING] Low disk space: {free_gb:.1f}GB")
            
            # Check if WiFi app is responsive and count CSV files in today's folder
            try:
                # Import dynamic file manager
                from modules.dynamic_file_manager import DynamicFileManager
                file_manager = DynamicFileManager()
                
                # Create daily folders if needed (at 12:00 AM)
                file_manager.create_daily_folders_if_needed()
                
                # Count CSV files in TODAY'S folder (not yesterday's)
                test_result = file_manager.count_csv_files_today()
                self.logger.info(f"[SEARCH] Health check passed - CSV files: {test_result}")
                
                # Ensure minimum 8 files (only during business hours)
                current_hour = datetime.now().hour
                if 9 <= current_hour <= 17:  # Business hours 9 AM - 5 PM
                    if test_result < 8:
                        self.logger.info(f"[PROCESS] Insufficient files during business hours: {test_result}/8")
                        self.ensure_minimum_files()
                
            except Exception as e:
                self.logger.error(f"[ERROR] WiFi app health check failed: {e}")
                # Reinitialize WiFi app
                self.wifi_app = CorrectedWiFiApp()
                self.logger.info("[PROCESS] WiFi app reinitialized")
            
            self.last_health_check = current_time
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Health check failed: {e}")
            return False
    
    def schedule_tasks(self):
        """Schedule regular tasks - DAY ONLY (no night downloads) + Monthly cleanup"""
        try:
            self.logger.info("🕐 Scheduling daytime tasks only...")
            
            # Clear existing jobs
            schedule.clear()
            
            # Schedule permanent tasks - DAY ONLY
            schedule.every().day.at("09:30").do(self.run_wifi_download, "morning").tag('permanent')
            schedule.every().day.at("13:00").do(self.run_wifi_download, "afternoon").tag('permanent')
            schedule.every().day.at("13:30").do(self.run_wifi_download, "afternoon_backup").tag('permanent')
            
            # Remove evening slots - NO NIGHT DOWNLOADS
            # schedule.every().day.at("21:05").do(self.run_wifi_download, "evening").tag('permanent')
            # schedule.every().day.at("21:11").do(self.run_wifi_download, "evening_backup").tag('permanent')
            
            schedule.every().day.at("00:00").do(self.reset_daily_counters).tag('permanent')
            
            # Schedule monthly cleanup (1st of each month at 2:00 AM)
            schedule.every().month.do(self.run_monthly_cleanup).tag('cleanup')
            
            # Schedule health checks
            schedule.every(5).minutes.do(self.health_check).tag('health')
            
            self.logger.info("✅ Daytime tasks scheduled (NO NIGHT DOWNLOADS):")
            self.logger.info("   🌅 Morning slot: 09:30 (09:30 AM)")
            self.logger.info("   🌞 Afternoon slot: 13:00 (1:00 PM)")
            self.logger.info("   🌞 Afternoon backup: 13:30 (1:30 PM)")
            self.logger.info("   🚫 Evening slots: DISABLED (no night downloads)")
            self.logger.info("   🔄 Daily reset: 00:00")
            self.logger.info("   🧹 Monthly cleanup: 1st of each month (2-month retention)")
            self.logger.info("   🏥 Health check: Every 5 minutes")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule tasks: {e}")
            self.handle_crash(e, "Task scheduling")
    
    def reset_daily_counters(self):
        """Reset daily counters at midnight"""
        try:
            self.logger.info("🔄 Resetting daily counters...")
            self.daily_files_downloaded = 0
            self.excel_generated_today = False
            self.crash_count = 0  # Reset crash count daily
            self.logger.info("✅ Daily counters reset")
        except Exception as e:
            self.logger.error(f"❌ Failed to reset counters: {e}")
    
    def run_monthly_cleanup(self):
        """Run monthly cleanup to remove files older than 2 months"""
        try:
            self.logger.info("🧹 Starting monthly cleanup (2-month retention)...")
            
            # Import dynamic file manager
            from modules.dynamic_file_manager import DynamicFileManager
            file_manager = DynamicFileManager()
            
            # Run cleanup
            result = file_manager.cleanup_old_files(days_to_keep=60)  # 2 months
            
            if result.get('success'):
                stats = result.get('statistics', {})
                self.logger.info(f"✅ Monthly cleanup completed:")
                self.logger.info(f"   📁 Directories removed: {stats.get('directories_removed', 0)}")
                self.logger.info(f"   📄 CSV files deleted: {stats.get('csv_files_deleted', 0)}")
                self.logger.info(f"   📊 Excel files deleted: {stats.get('excel_files_deleted', 0)}")
                self.logger.info(f"   📋 PDF files deleted: {stats.get('pdf_files_deleted', 0)}")
                self.logger.info(f"   💾 Space freed: {stats.get('total_space_freed_mb', 0):.1f}MB")
                
                # Send cleanup notification email
                try:
                    if self.email_service:
                        subject = f"🧹 Monthly Cleanup Completed - {datetime.now().strftime('%d/%m/%Y')}"
                        body = f"""Monthly file cleanup has been completed successfully!

Cleanup Summary:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🗓️ Retention Period: 2 months (60 days)
📁 Directories Removed: {stats.get('directories_removed', 0)}
📄 CSV Files Deleted: {stats.get('csv_files_deleted', 0)}
📊 Excel Files Deleted: {stats.get('excel_files_deleted', 0)}
📋 PDF Files Deleted: {stats.get('pdf_files_deleted', 0)}
💾 Space Freed: {stats.get('total_space_freed_mb', 0):.1f}MB

This automatic cleanup ensures your system stays organized while giving you 2 months to backup important files to your external hard disk.

Reminder: Please backup any important files to your external hard disk before they are automatically cleaned up.

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department
"""
                        self.email_service.send_email(subject, body)
                        self.logger.info("📧 Cleanup notification sent")
                except Exception as e:
                    self.logger.warning(f"Cleanup notification failed: {e}")
                    
            else:
                error_msg = result.get('error', 'Unknown error')
                self.logger.error(f"❌ Monthly cleanup failed: {error_msg}")
                
                # Send failure notification
                try:
                    if self.email_service:
                        subject = f"❌ Monthly Cleanup Failed - {datetime.now().strftime('%d/%m/%Y')}"
                        body = f"""Monthly file cleanup has failed!

Error Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
❌ Error: {error_msg}

Please check the system logs and run manual cleanup if needed.

Best regards,
WiFi Automation System
"""
                        self.email_service.send_email(subject, body)
                except Exception as e:
                    self.logger.warning(f"Cleanup failure notification failed: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ Monthly cleanup error: {e}")
            self.handle_crash(e, "Monthly cleanup")
    
    def start_service(self):
        """Start the enhanced WiFi service with email notifications"""
        try:
            self.logger.info("🚀 Starting Enhanced WiFi Service with Email Notifications...")
            
            # Set running flag
            self.running = True
            
            # Send startup notification
            try:
                if self.email_service:
                    startup_success = self.email_service.send_startup_notification()
                    if startup_success:
                        self.logger.info("📧 Startup notification sent successfully")
                    else:
                        self.logger.warning("📧 Startup notification failed")
            except Exception as e:
                self.logger.warning(f"Startup notification error: {e}")
            
            # Initialize dynamic file manager
            from modules.dynamic_file_manager import DynamicFileManager
            file_manager = DynamicFileManager()
            
            # Create daily folders if needed
            file_manager.create_daily_folders_if_needed()
            
            # Check current file status
            current_files = file_manager.count_csv_files_today()
            self.logger.info(f"📊 Current files in today's folder: {current_files}/8")
            
            # Ensure minimum 8 files on startup
            if current_files < 8:
                self.logger.info("🚀 Startup: Ensuring minimum 8 files...")
                self.ensure_minimum_files()
            else:
                self.logger.info("✅ Startup: Sufficient files already available")
            
            # Schedule tasks
            self.schedule_tasks()
            
            # Start the service loop
            self.logger.info("✅ Service started successfully")
            self.logger.info("🛡️ Crash prevention active")
            self.logger.info("🔄 Auto-restart enabled")
            self.logger.info("🏥 Health monitoring active")
            self.logger.info("📅 Permanent schedule active")
            self.logger.info("📧 Email notifications enabled")
            self.logger.info("🔄 Service is running... Press Ctrl+C to stop")
            
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(30)  # Check every 30 seconds
                except KeyboardInterrupt:
                    self.logger.info("🛑 Keyboard interrupt received")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Service loop error: {e}")
                    self.handle_crash(e, "Service loop")
                    time.sleep(60)  # Wait 1 minute before retrying
            
        except Exception as e:
            self.logger.error(f"❌ Service startup failed: {e}")
            self.handle_crash(e, "Service startup")
        finally:
            self.stop_service()
    
    def stop_service(self):
        """Stop the service"""
        self.logger.info("🛑 Stopping Enhanced WiFi Service...")
        self.running = False
        
        # Send shutdown notification
        try:
            if self.email_service:
                subject = f"🛑 WiFi Service Stopped - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                body = "WiFi Automation Service has been stopped.\n\nBest regards,\nWiFi Automation System"
                self.email_service.send_email(subject=subject, body=body)
        except:
            pass

def main():
    """Main function"""
    try:
        service = EnhancedWiFiServiceWithEmail()
        service.start_service()
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Service failed: {e}")
        logger.error(f"Service failed: {e}")

if __name__ == "__main__":
    main() 