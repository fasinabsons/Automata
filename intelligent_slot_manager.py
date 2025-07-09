#!/usr/bin/env python3
"""
Intelligent Slot Manager - Smart WiFi Automation Timing
Handles slot timing, late start detection, and Excel generation
FIXED: Excel generation timing and error handling
"""

import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json

# Import working components
from modules.dynamic_file_manager import DynamicFileManager
from modules.csv_to_excel_processor import CSVToExcelProcessor
from working_email_notifications import WorkingEmailNotifications

class IntelligentSlotManager:
    """Smart slot management with Excel generation timing - FIXED"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.file_manager = DynamicFileManager()
        self.excel_processor = CSVToExcelProcessor()
        self.email_notifier = WorkingEmailNotifications()
        
        # Slot timing configuration
        self.SLOT_TIMES = {
            'morning': {'hour': 9, 'minute': 30},
            'afternoon': {'hour': 13, 'minute': 0}
        }
        
        # Excel generation timing
        self.EXCEL_GENERATION_DELAY = 30  # seconds after slot completion
        self.MIN_FILES_FOR_EXCEL = 8
        
        # Status tracking
        self.completed_slots = []
        self.pending_slots = ['morning', 'afternoon']
        self.slot_results = {}
        
        self.logger.info("Intelligent Slot Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for slot manager"""
        logger = logging.getLogger("IntelligentSlotManager")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"slot_manager_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not logger.handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def get_current_time_info(self) -> Dict[str, Any]:
        """Get current time information"""
        now = datetime.now()
        return {
            'current_time': now,
            'hour': now.hour,
            'minute': now.minute,
            'time_string': now.strftime("%H:%M"),
            'date_string': now.strftime("%Y-%m-%d"),
            'is_business_hours': 9 <= now.hour <= 17
        }
    
    def determine_current_slot(self) -> Optional[str]:
        """Determine which slot we're currently in"""
        time_info = self.get_current_time_info()
        current_hour = time_info['hour']
        current_minute = time_info['minute']
        
        # Morning slot: 9:30 AM - 12:59 PM
        if current_hour == 9 and current_minute >= 30:
            return 'morning'
        elif 10 <= current_hour <= 12:
            return 'morning'
        
        # Afternoon slot: 1:00 PM - 5:59 PM
        elif 13 <= current_hour <= 17:
            return 'afternoon'
        
        return None
    
    def is_late_start(self) -> Dict[str, Any]:
        """Check if we're starting late in a slot"""
        time_info = self.get_current_time_info()
        current_slot = self.determine_current_slot()
        
        if not current_slot:
            return {'is_late': False, 'slot': None, 'reason': 'Not in business hours'}
        
        slot_config = self.SLOT_TIMES[current_slot]
        slot_start = datetime.now().replace(
            hour=slot_config['hour'], 
            minute=slot_config['minute'], 
            second=0, 
            microsecond=0
        )
        
        # Consider late if more than 30 minutes after slot start
        late_threshold = slot_start + timedelta(minutes=30)
        is_late = datetime.now() > late_threshold
        
        return {
            'is_late': is_late,
            'slot': current_slot,
            'slot_start': slot_start,
            'late_threshold': late_threshold,
            'current_time': datetime.now(),
            'minutes_late': (datetime.now() - slot_start).total_seconds() / 60 if is_late else 0
        }
    
    def check_file_requirements(self) -> Dict[str, Any]:
        """Check if file requirements are met"""
        try:
            csv_dir = self.file_manager.get_download_directory()
            current_files = self.file_manager.count_csv_files_today()
            
            # Check if Excel already exists
            excel_exists = self.check_excel_exists()
            
            return {
                'current_files': current_files,
                'target_files': self.MIN_FILES_FOR_EXCEL,
                'files_needed': max(0, self.MIN_FILES_FOR_EXCEL - current_files),
                'excel_exists': excel_exists,
                'should_download': current_files < self.MIN_FILES_FOR_EXCEL and not excel_exists,
                'csv_directory': str(csv_dir)
            }
        except Exception as e:
            self.logger.error(f"Error checking file requirements: {e}")
            return {
                'current_files': 0,
                'target_files': self.MIN_FILES_FOR_EXCEL,
                'files_needed': self.MIN_FILES_FOR_EXCEL,
                'excel_exists': False,
                'should_download': True,
                'error': str(e)
            }
    
    def check_excel_exists(self) -> bool:
        """Check if Excel file already exists for today"""
        try:
            today = datetime.now().strftime("%d%m%Y")
            excel_dir = Path(f"EHC_Data_Merge/{today}")
            excel_file = excel_dir / f"EHC_Upload_Mac_{today}.xls"
            
            exists = excel_file.exists()
            if exists:
                self.logger.info(f"Excel file already exists: {excel_file}")
            
            return exists
        except Exception as e:
            self.logger.error(f"Error checking Excel existence: {e}")
            return False
    
    def execute_slot_download(self, slot_name: str) -> Dict[str, Any]:
        """Execute download for a specific slot - FIXED"""
        try:
            self.logger.info(f"Starting {slot_name} slot download")
            
            # Import and run the corrected WiFi app
            from corrected_wifi_app import CorrectedWiFiApp
            
            wifi_app = CorrectedWiFiApp()
            
            # Get initial file count
            initial_files = self.file_manager.count_csv_files_today()
            
            # Run the download
            download_result = wifi_app.run_complete_automation()
            
            # Get final file count
            final_files = self.file_manager.count_csv_files_today()
            files_downloaded = final_files - initial_files
            
            # FIXED: Ensure download_result is a dictionary
            if isinstance(download_result, bool):
                download_result = {
                    'success': download_result,
                    'files_downloaded': files_downloaded,
                    'total_files': final_files
                }
            elif not isinstance(download_result, dict):
                download_result = {
                    'success': False,
                    'files_downloaded': 0,
                    'total_files': final_files,
                    'error': f"Unexpected result type: {type(download_result)}"
                }
            
            # Update result with file counts
            download_result.update({
                'slot': slot_name,
                'initial_files': initial_files,
                'final_files': final_files,
                'files_downloaded': files_downloaded,
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"{slot_name} slot completed: {files_downloaded} files downloaded")
            
            return download_result
            
        except Exception as e:
            error_msg = f"Error in {slot_name} slot: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'slot': slot_name,
                'files_downloaded': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_excel_after_slot(self, slot_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Excel file after slot completion - ENHANCED"""
        try:
            self.logger.info(f"Checking Excel generation after slot completion")
            
            # Wait for downloads to settle
            time.sleep(self.EXCEL_GENERATION_DELAY)
            
            # Check if Excel already exists
            if self.check_excel_exists():
                self.logger.info("Excel file already exists - skipping generation")
                return {'success': True, 'action': 'skipped', 'reason': 'Excel already exists'}
            
            # Check file count
            file_requirements = self.check_file_requirements()
            
            if file_requirements['current_files'] >= self.MIN_FILES_FOR_EXCEL:
                self.logger.info(f"Generating Excel from {file_requirements['current_files']} files")
                
                # Generate Excel
                excel_result = self.excel_processor.process_and_generate_excel(
                    file_requirements['csv_directory']
                )
                
                if excel_result.get('success'):
                    self.logger.info("Excel generation successful!")
                    
                    # Send email notification
                    try:
                        email_result = self.email_notifier.send_excel_notification(
                            excel_result['file_path'],
                            excel_result['records_written']
                        )
                        excel_result['email_sent'] = email_result.get('success', False)
                    except Exception as e:
                        self.logger.warning(f"Email notification failed: {e}")
                        excel_result['email_sent'] = False
                    
                    return excel_result
                else:
                    self.logger.error(f"Excel generation failed: {excel_result.get('error')}")
                    return excel_result
            else:
                self.logger.info(f"Not enough files for Excel ({file_requirements['current_files']}/{self.MIN_FILES_FOR_EXCEL})")
                return {
                    'success': False,
                    'action': 'skipped',
                    'reason': f"Not enough files ({file_requirements['current_files']}/{self.MIN_FILES_FOR_EXCEL})"
                }
                
        except Exception as e:
            error_msg = f"Error in Excel generation: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def run_intelligent_slot_management(self) -> Dict[str, Any]:
        """Run intelligent slot management - MAIN METHOD"""
        try:
            self.logger.info("Starting Intelligent Slot Management")
            
            # Get current time and slot information
            time_info = self.get_current_time_info()
            current_slot = self.determine_current_slot()
            late_info = self.is_late_start()
            file_requirements = self.check_file_requirements()
            
            self.logger.info(f"Current time: {time_info['time_string']}")
            self.logger.info(f"Current slot: {current_slot}")
            self.logger.info(f"Files: {file_requirements['current_files']}/{file_requirements['target_files']}")
            
            # Check if we should run
            if not current_slot:
                return {
                    'success': False,
                    'reason': 'Not in business hours',
                    'time_info': time_info
                }
            
            # Check if Excel already exists
            if file_requirements['excel_exists']:
                self.logger.info("Excel already exists - no action needed")
                return {
                    'success': True,
                    'action': 'skipped',
                    'reason': 'Excel already exists',
                    'excel_exists': True
                }
            
            # Check if we need to download files
            if not file_requirements['should_download']:
                self.logger.info("Sufficient files available - checking Excel generation")
                excel_result = self.generate_excel_after_slot({'slot': current_slot})
                return {
                    'success': True,
                    'action': 'excel_only',
                    'excel_result': excel_result
                }
            
            # Execute slot download
            self.logger.info(f"Executing {current_slot} slot download")
            slot_result = self.execute_slot_download(current_slot)
            
            # Update slot tracking
            if slot_result.get('success'):
                if current_slot not in self.completed_slots:
                    self.completed_slots.append(current_slot)
                if current_slot in self.pending_slots:
                    self.pending_slots.remove(current_slot)
            
            self.slot_results[current_slot] = slot_result
            
            # Generate Excel after successful download
            excel_result = None
            if slot_result.get('success'):
                excel_result = self.generate_excel_after_slot(slot_result)
            
            return {
                'success': slot_result.get('success', False),
                'slot': current_slot,
                'slot_result': slot_result,
                'excel_result': excel_result,
                'time_info': time_info,
                'late_info': late_info,
                'file_requirements': file_requirements,
                'completed_slots': self.completed_slots,
                'pending_slots': self.pending_slots
            }
            
        except Exception as e:
            error_msg = f"Error in intelligent slot management: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        try:
            time_info = self.get_current_time_info()
            current_slot = self.determine_current_slot()
            late_info = self.is_late_start()
            file_requirements = self.check_file_requirements()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'time_info': time_info,
                'current_slot': current_slot,
                'late_info': late_info,
                'file_requirements': file_requirements,
                'completed_slots': self.completed_slots,
                'pending_slots': self.pending_slots,
                'slot_results': self.slot_results,
                'excel_exists': self.check_excel_exists()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Convenience functions
def run_slot_management() -> Dict[str, Any]:
    """Run intelligent slot management"""
    manager = IntelligentSlotManager()
    return manager.run_intelligent_slot_management()

def get_slot_status() -> Dict[str, Any]:
    """Get slot status report"""
    manager = IntelligentSlotManager()
    return manager.get_status_report()

# Test function
def test_slot_manager():
    """Test slot manager functionality"""
    manager = IntelligentSlotManager()
    
    print("🧪 Testing Intelligent Slot Manager...")
    
    # Test status report
    status = manager.get_status_report()
    print(f"📊 Status: {status}")
    
    # Test slot management
    result = manager.run_intelligent_slot_management()
    print(f"🎯 Result: {result}")

if __name__ == "__main__":
    test_slot_manager() 