#!/usr/bin/env python3
"""
Advanced Scheduling System
Handles 2-slot daily schedule with 5-minute merge delay and background operation
"""

import os
import sys
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import schedule
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Import our modules
import sys
sys.path.append('.')
from modules.excel_generator import EnhancedExcelGenerator

class AdvancedScheduler:
    """Advanced scheduler with multi-slot support and background operation"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.scheduler = BackgroundScheduler()
        self.excel_generator = EnhancedExcelGenerator()
        
        # Scheduling configuration
        self.timezone = pytz.timezone('Asia/Kolkata')  # Adjust to your timezone
        self.time_slots = [
            {"name": "morning", "time": "09:30", "hour": 9, "minute": 30},
            {"name": "afternoon", "time": "13:00", "hour": 13, "minute": 0},
            {"name": "evening", "time": "15:30", "hour": 15, "minute": 30}
        ]
        
        # Merge delay configuration
        self.merge_delay_minutes = 5
        self.merge_timer = None
        
        # Status tracking
        self.daily_status = {
            "date": None,
            "slots_executed": [],
            "slots_completed": [],
            "merge_scheduled": False,
            "merge_completed": False,
            "csv_files_count": 0,
            "excel_generated": False
        }
        
        # Callbacks
        self.download_callback = None
        self.merge_callback = None
        
        self.logger.info("Advanced Scheduler initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for scheduler"""
        logger = logging.getLogger("AdvancedScheduler")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def set_download_callback(self, callback: Callable):
        """Set callback function for WiFi download execution"""
        self.download_callback = callback
        self.logger.info("Download callback registered")
    
    def set_merge_callback(self, callback: Callable):
        """Set callback function for Excel merge execution"""
        self.merge_callback = callback
        self.logger.info("Merge callback registered")
    
    def start_scheduler(self):
        """Start the background scheduler"""
        try:
            # Reset daily status
            self._reset_daily_status()
            
            # Schedule daily slots
            for slot in self.time_slots:
                self.scheduler.add_job(
                    func=self._execute_slot,
                    trigger=CronTrigger(
                        hour=slot["hour"],
                        minute=slot["minute"],
                        timezone=self.timezone
                    ),
                    args=[slot],
                    id=f"slot_{slot['name']}",
                    replace_existing=True
                )
                self.logger.info(f"Scheduled {slot['name']} slot at {slot['time']}")
            
            # Schedule daily reset at midnight
            self.scheduler.add_job(
                func=self._reset_daily_status,
                trigger=CronTrigger(
                    hour=0,
                    minute=0,
                    timezone=self.timezone
                ),
                id="daily_reset",
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self.logger.info("Background scheduler started successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            return False
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.logger.info("Background scheduler stopped")
            
            # Cancel merge timer if running
            if self.merge_timer:
                self.merge_timer.cancel()
                self.merge_timer = None
                self.logger.info("Merge timer cancelled")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop scheduler: {e}")
            return False
    
    def _reset_daily_status(self):
        """Reset daily status for new day"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.daily_status = {
            "date": today,
            "slots_executed": [],
            "slots_completed": [],
            "merge_scheduled": False,
            "merge_completed": False,
            "csv_files_count": 0,
            "excel_generated": False
        }
        
        self.logger.info(f"Daily status reset for {today}")
    
    def _execute_slot(self, slot: Dict[str, Any]):
        """Execute a scheduled slot"""
        try:
            slot_name = slot["name"]
            current_time = datetime.now().strftime("%H:%M")
            
            self.logger.info(f"🚀 Executing {slot_name} slot at {current_time}")
            
            # Mark slot as executed
            self.daily_status["slots_executed"].append(slot_name)
            
            # Execute WiFi download if callback is set
            if self.download_callback:
                self.logger.info(f"Starting WiFi download for {slot_name} slot")
                
                try:
                    result = self.download_callback(slot_name)
                    
                    if result and result.get("success", False):
                        self.logger.info(f"✅ {slot_name} slot completed successfully")
                        self.daily_status["slots_completed"].append(slot_name)
                        self.daily_status["csv_files_count"] += result.get("files_downloaded", 0)
                        
                        # Schedule merge if this is the last slot
                        self._check_and_schedule_merge()
                    else:
                        self.logger.error(f"❌ {slot_name} slot failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error executing {slot_name} slot: {e}")
            else:
                self.logger.warning(f"No download callback set for {slot_name} slot")
                
        except Exception as e:
            self.logger.error(f"Critical error in slot execution: {e}")
    
    def _check_and_schedule_merge(self):
        """Check if all slots are completed and schedule merge"""
        try:
            completed_slots = len(self.daily_status["slots_completed"])
            total_slots = len(self.time_slots)
            
            self.logger.info(f"Slots completed: {completed_slots}/{total_slots}")
            
            # If all slots are completed and merge not scheduled
            if completed_slots >= total_slots and not self.daily_status["merge_scheduled"]:
                self.logger.info(f"🕐 Scheduling Excel merge in {self.merge_delay_minutes} minutes")
                
                # Cancel existing timer if any
                if self.merge_timer:
                    self.merge_timer.cancel()
                
                # Schedule merge with delay
                self.merge_timer = threading.Timer(
                    self.merge_delay_minutes * 60,  # Convert to seconds
                    self._execute_merge
                )
                self.merge_timer.start()
                
                self.daily_status["merge_scheduled"] = True
                self.logger.info("✅ Merge scheduled successfully")
            
        except Exception as e:
            self.logger.error(f"Error scheduling merge: {e}")
    
    def _execute_merge(self):
        """Execute Excel merge operation"""
        try:
            self.logger.info("🔄 Starting Excel merge operation")
            
            # Get today's CSV directory
            today = datetime.now().strftime("%d%B").lower()  # e.g., "04july"
            csv_dir = Path(f"EHC_Data/{today}")
            
            if not csv_dir.exists():
                self.logger.error(f"CSV directory not found: {csv_dir}")
                return
            
            # Count CSV files
            csv_files = list(csv_dir.glob("*.csv"))
            self.logger.info(f"Found {len(csv_files)} CSV files to merge")
            
            # Generate Excel file
            result = self.excel_generator.generate_excel_from_csv_directory(csv_dir)
            
            if result.get("success", False):
                self.logger.info("✅ Excel merge completed successfully")
                self.daily_status["merge_completed"] = True
                self.daily_status["excel_generated"] = True
                
                # Log results
                self.logger.info(f"📄 Excel file: {result.get('file_path', 'N/A')}")
                self.logger.info(f"📏 File size: {result.get('file_size_mb', 0)} MB")
                self.logger.info(f"📝 Records: {result.get('rows_written', 0)}")
                
                # Execute merge callback if set
                if self.merge_callback:
                    try:
                        self.merge_callback(result)
                    except Exception as e:
                        self.logger.error(f"Error in merge callback: {e}")
                
            else:
                self.logger.error(f"❌ Excel merge failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Critical error in merge execution: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "scheduler_running": self.scheduler.running if self.scheduler else False,
            "daily_status": self.daily_status.copy(),
            "time_slots": self.time_slots,
            "merge_delay_minutes": self.merge_delay_minutes,
            "next_run_time": self._get_next_run_time()
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """Get next scheduled run time"""
        try:
            if not self.scheduler.running:
                return None
            
            jobs = self.scheduler.get_jobs()
            if not jobs:
                return None
            
            # Find next job
            next_job = min(jobs, key=lambda job: job.next_run_time)
            return next_job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            self.logger.error(f"Error getting next run time: {e}")
            return None
    
    def manual_trigger_slot(self, slot_name: str) -> Dict[str, Any]:
        """Manually trigger a specific slot"""
        try:
            # Find slot configuration
            slot = None
            for s in self.time_slots:
                if s["name"] == slot_name:
                    slot = s
                    break
            
            if not slot:
                return {"success": False, "error": f"Slot '{slot_name}' not found"}
            
            self.logger.info(f"🔧 Manually triggering {slot_name} slot")
            
            # Execute slot
            self._execute_slot(slot)
            
            return {"success": True, "message": f"Slot '{slot_name}' triggered successfully"}
            
        except Exception as e:
            error_msg = f"Failed to trigger slot '{slot_name}': {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def manual_trigger_merge(self) -> Dict[str, Any]:
        """Manually trigger Excel merge"""
        try:
            self.logger.info("🔧 Manually triggering Excel merge")
            
            # Execute merge immediately
            self._execute_merge()
            
            return {"success": True, "message": "Excel merge triggered successfully"}
            
        except Exception as e:
            error_msg = f"Failed to trigger merge: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

# Test function
def test_scheduler():
    """Test scheduler functionality"""
    scheduler = AdvancedScheduler()
    
    # Mock download callback
    def mock_download_callback(slot_name):
        print(f"🔄 Mock download for {slot_name} slot")
        time.sleep(2)  # Simulate download time
        return {"success": True, "files_downloaded": 4}
    
    # Mock merge callback
    def mock_merge_callback(result):
        print(f"🔄 Mock merge callback: {result.get('file_path', 'N/A')}")
    
    # Set callbacks
    scheduler.set_download_callback(mock_download_callback)
    scheduler.set_merge_callback(mock_merge_callback)
    
    print("\n🧪 Testing Advanced Scheduler")
    print("=" * 50)
    
    # Test manual triggers
    print("\n1. Testing manual slot trigger:")
    result = scheduler.manual_trigger_slot("morning")
    print(f"   Result: {result}")
    
    print("\n2. Testing manual merge trigger:")
    result = scheduler.manual_trigger_merge()
    print(f"   Result: {result}")
    
    print("\n3. Getting scheduler status:")
    status = scheduler.get_status()
    print(f"   Status: {status}")
    
    print("\n4. Testing scheduler start/stop:")
    start_result = scheduler.start_scheduler()
    print(f"   Start result: {start_result}")
    
    time.sleep(2)
    
    stop_result = scheduler.stop_scheduler()
    print(f"   Stop result: {stop_result}")
    
    print("\n✅ Scheduler testing completed")

if __name__ == "__main__":
    test_scheduler()