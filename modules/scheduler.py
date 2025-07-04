"""
Enhanced Scheduler for WiFi Data Automation
Implements multi-slot scheduling with hybrid scraping and file processing
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
from pathlib import Path
import json

# Local imports
from config.settings import SCHEDULE_CONFIG, WIFI_CONFIG, FILE_CONFIG
from core.logger import logger
from modules.hybrid_web_scraper import BulletproofRuckusWiFiScraper, execute_bulletproof_scraping
from modules.file_processor import WiFiDataProcessor, process_wifi_data, merge_slot_data
from modules.email_service import EmailService


class WiFiDataScheduler:
    """
    Enhanced WiFi Data Scheduler with multi-slot support
    """
    
    def __init__(self):
        self.is_running = False
        self.current_executions = {}
        self.slot_data = {}  # Store CSV files by slot
        self.execution_history = []
        self.scheduler_thread = None
        self.lock = threading.Lock()
        
        # Initialize services
        self.email_service = EmailService()
        
        # Schedule configuration
        self.slots = SCHEDULE_CONFIG['slots']
        self.merge_delay = SCHEDULE_CONFIG['merge_delay_minutes']
        self.max_execution_time = SCHEDULE_CONFIG['max_execution_time_minutes']
        
        logger.info("WiFi Data Scheduler initialized", "Scheduler", "init")
        logger.info(f"Configured slots: {[slot['time'] for slot in self.slots]}", "Scheduler", "init")
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.is_running:
            logger.warning("Scheduler is already running", "Scheduler", "start")
            return
        
        logger.info("Starting WiFi Data Scheduler", "Scheduler", "start")
        
        # Clear existing schedules
        schedule.clear()
        
        # Schedule each slot
        for slot in self.slots:
            slot_time = slot['time']
            slot_name = slot['name']
            
            schedule.every().day.at(slot_time).do(
                self._execute_slot_with_timeout,
                slot_name=slot_name
            )
            
            logger.info(f"Scheduled {slot_name} at {slot_time}", "Scheduler", "start")
        
        # Schedule merge operation (runs after the last slot + delay)
        last_slot_time = self.slots[-1]['time']
        merge_time = self._calculate_merge_time(last_slot_time)
        
        schedule.every().day.at(merge_time).do(
            self._execute_merge_operation
        )
        
        logger.info(f"Scheduled merge operation at {merge_time}", "Scheduler", "start")
        
        # Start scheduler thread
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.success("WiFi Data Scheduler started successfully", "Scheduler", "start")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running", "Scheduler", "stop")
            return
        
        logger.info("Stopping WiFi Data Scheduler", "Scheduler", "stop")
        
        self.is_running = False
        schedule.clear()
        
        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)
        
        logger.success("WiFi Data Scheduler stopped", "Scheduler", "stop")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Scheduler thread started", "Scheduler", "run")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}", "Scheduler", "run")
                time.sleep(60)  # Wait longer on error
        
        logger.info("Scheduler thread stopped", "Scheduler", "run")
    
    def _calculate_merge_time(self, last_slot_time: str) -> str:
        """Calculate merge operation time based on last slot + delay"""
        try:
            # Parse last slot time
            hour, minute = map(int, last_slot_time.split(':'))
            last_slot_dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Add merge delay
            merge_dt = last_slot_dt + timedelta(minutes=self.merge_delay)
            
            return merge_dt.strftime('%H:%M')
            
        except Exception as e:
            logger.error(f"Error calculating merge time: {e}", "Scheduler", "calc_merge")
            return "23:59"  # Default to end of day
    
    def _execute_slot_with_timeout(self, slot_name: str):
        """Execute slot with timeout protection"""
        execution_id = f"{slot_name}_{int(datetime.now().timestamp())}"
        
        try:
            logger.info(f"Starting slot execution: {slot_name}", "Scheduler", execution_id)
            
            # Check if already running
            with self.lock:
                if slot_name in self.current_executions:
                    logger.warning(f"Slot {slot_name} is already running", "Scheduler", execution_id)
                    return
                
                self.current_executions[slot_name] = {
                    'execution_id': execution_id,
                    'start_time': datetime.now(),
                    'status': 'running'
                }
            
            # Execute slot in separate thread with timeout
            slot_thread = threading.Thread(
                target=self._execute_slot,
                args=(slot_name, execution_id),
                daemon=True
            )
            
            slot_thread.start()
            slot_thread.join(timeout=self.max_execution_time * 60)  # Convert to seconds
            
            # Check if thread is still alive (timeout occurred)
            if slot_thread.is_alive():
                logger.error(f"Slot {slot_name} execution timed out after {self.max_execution_time} minutes", 
                           "Scheduler", execution_id)
                
                # Update status
                with self.lock:
                    if slot_name in self.current_executions:
                        self.current_executions[slot_name]['status'] = 'timeout'
                        self.current_executions[slot_name]['end_time'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Slot execution wrapper failed for {slot_name}: {e}", "Scheduler", execution_id)
            
            # Update status
            with self.lock:
                if slot_name in self.current_executions:
                    self.current_executions[slot_name]['status'] = 'error'
                    self.current_executions[slot_name]['error'] = str(e)
                    self.current_executions[slot_name]['end_time'] = datetime.now()
    
    def _execute_slot(self, slot_name: str, execution_id: str):
        """Execute a single slot"""
        try:
            logger.info(f"Executing slot: {slot_name}", "Scheduler", execution_id)
            
            # Execute bulletproof scraping
            scraper_result = execute_bulletproof_scraping(slot_name)
            
            # Update execution status
            with self.lock:
                if slot_name in self.current_executions:
                    self.current_executions[slot_name]['scraper_result'] = scraper_result
            
            if scraper_result['success']:
                downloaded_files = scraper_result.get('downloaded_files', [])
                
                if downloaded_files:
                    # Store files for later merging
                    with self.lock:
                        if slot_name not in self.slot_data:
                            self.slot_data[slot_name] = []
                        self.slot_data[slot_name].extend(downloaded_files)
                    
                    logger.success(f"Slot {slot_name} completed successfully: {len(downloaded_files)} files downloaded", 
                                 "Scheduler", execution_id)
                else:
                    logger.warning(f"Slot {slot_name} completed but no files downloaded", "Scheduler", execution_id)
            else:
                logger.error(f"Slot {slot_name} failed: {scraper_result.get('error', 'Unknown error')}", 
                           "Scheduler", execution_id)
            
            # Update final status
            with self.lock:
                if slot_name in self.current_executions:
                    self.current_executions[slot_name]['status'] = 'completed' if scraper_result['success'] else 'failed'
                    self.current_executions[slot_name]['end_time'] = datetime.now()
            
            # Add to execution history
            self.execution_history.append({
                'slot_name': slot_name,
                'execution_id': execution_id,
                'timestamp': datetime.now().isoformat(),
                'success': scraper_result['success'],
                'files_downloaded': len(scraper_result.get('downloaded_files', [])),
                'result': scraper_result
            })
            
        except Exception as e:
            logger.error(f"Slot execution failed for {slot_name}: {e}", "Scheduler", execution_id)
            
            # Update error status
            with self.lock:
                if slot_name in self.current_executions:
                    self.current_executions[slot_name]['status'] = 'error'
                    self.current_executions[slot_name]['error'] = str(e)
                    self.current_executions[slot_name]['end_time'] = datetime.now()
    
    def _execute_merge_operation(self):
        """Execute merge operation for all slots"""
        merge_execution_id = f"merge_{int(datetime.now().timestamp())}"
        
        try:
            logger.info("Starting merge operation", "Scheduler", merge_execution_id)
            
            # Check if we have data to merge
            with self.lock:
                slot_data_copy = self.slot_data.copy()
                self.slot_data.clear()  # Clear for next cycle
            
            if not slot_data_copy:
                logger.warning("No slot data available for merging", "Scheduler", merge_execution_id)
                return
            
            # Log slot data summary
            for slot_name, files in slot_data_copy.items():
                logger.info(f"Slot {slot_name}: {len(files)} files", "Scheduler", merge_execution_id)
            
            # Execute merge
            merge_result = merge_slot_data(slot_data_copy)
            
            if merge_result['success']:
                excel_file = merge_result['excel_file']
                record_count = merge_result['total_records']
                
                logger.success(f"Merge completed successfully: {Path(excel_file).name} with {record_count} records", 
                             "Scheduler", merge_execution_id)
                
                # Send email notification
                self._send_completion_email(merge_result)
                
                # Cleanup old files
                self._cleanup_old_files()
                
            else:
                logger.error(f"Merge operation failed: {merge_result.get('error', 'Unknown error')}", 
                           "Scheduler", merge_execution_id)
                
                # Send error email
                self._send_error_email(merge_result)
            
        except Exception as e:
            logger.error(f"Merge operation failed: {e}", "Scheduler", merge_execution_id)
            
            # Send error email
            self._send_error_email({'error': str(e), 'success': False})
    
    def _send_completion_email(self, merge_result: Dict[str, Any]):
        """Send completion email with Excel file"""
        try:
            logger.info("Sending completion email", "Scheduler", "email")
            
            excel_file = merge_result['excel_file']
            excel_filename = merge_result['excel_filename']
            record_count = merge_result['total_records']
            
            subject = f"WiFi Data Report - {datetime.now().strftime('%d/%m/%Y')}"
            
            body = f"""
            Daily WiFi User Data Report
            
            Date: {datetime.now().strftime('%d/%m/%Y')}
            Time: {datetime.now().strftime('%H:%M:%S')}
            
            Report Details:
            - Total Records: {record_count}
            - File Name: {excel_filename}
            - CSV Files Processed: {merge_result['csv_files_processed']}
            - Successful Extractions: {merge_result['successful_csv_files']}
            
            Please find the attached Excel file with the complete WiFi user data.
            
            Best regards,
            WiFi Data Automation System
            """
            
            # Send email with attachment
            email_result = self.email_service.send_email_with_attachment(
                subject=subject,
                body=body,
                attachment_path=excel_file
            )
            
            if email_result['success']:
                logger.success("Completion email sent successfully", "Scheduler", "email")
            else:
                logger.error(f"Failed to send completion email: {email_result.get('error')}", "Scheduler", "email")
                
        except Exception as e:
            logger.error(f"Error sending completion email: {e}", "Scheduler", "email")
    
    def _send_error_email(self, error_result: Dict[str, Any]):
        """Send error notification email"""
        try:
            logger.info("Sending error notification email", "Scheduler", "email")
            
            subject = f"WiFi Data Report - ERROR - {datetime.now().strftime('%d/%m/%Y')}"
            
            body = f"""
            WiFi Data Automation System - ERROR NOTIFICATION
            
            Date: {datetime.now().strftime('%d/%m/%Y')}
            Time: {datetime.now().strftime('%H:%M:%S')}
            
            An error occurred during the WiFi data extraction process:
            
            Error: {error_result.get('error', 'Unknown error')}
            
            Please check the system logs for more details.
            
            Best regards,
            WiFi Data Automation System
            """
            
            # Send error email
            email_result = self.email_service.send_email(
                subject=subject,
                body=body
            )
            
            if email_result['success']:
                logger.success("Error notification email sent successfully", "Scheduler", "email")
            else:
                logger.error(f"Failed to send error email: {email_result.get('error')}", "Scheduler", "email")
                
        except Exception as e:
            logger.error(f"Error sending error notification email: {e}", "Scheduler", "email")
    
    def _cleanup_old_files(self):
        """Clean up old files"""
        try:
            logger.info("Starting file cleanup", "Scheduler", "cleanup")
            
            processor = WiFiDataProcessor()
            cleanup_result = processor.cleanup_old_files(retention_days=30)
            
            if cleanup_result['success']:
                deleted_count = cleanup_result['deleted_count']
                logger.success(f"File cleanup completed: {deleted_count} files deleted", "Scheduler", "cleanup")
            else:
                logger.error(f"File cleanup failed: {cleanup_result.get('error')}", "Scheduler", "cleanup")
                
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}", "Scheduler", "cleanup")
    
    def execute_manual_slot(self, slot_name: str = None) -> Dict[str, Any]:
        """Execute a manual slot for testing"""
        try:
            slot_name = slot_name or f"manual_{int(datetime.now().timestamp())}"
            execution_id = f"{slot_name}_{int(datetime.now().timestamp())}"
            
            logger.info(f"Starting manual slot execution: {slot_name}", "Scheduler", execution_id)
            
            # Execute bulletproof scraping
            scraper_result = execute_bulletproof_scraping(slot_name)
            
            if scraper_result['success']:
                downloaded_files = scraper_result.get('downloaded_files', [])
                
                if downloaded_files:
                    # Process files immediately for manual execution
                    processor_result = process_wifi_data(downloaded_files, slot_name)
                    
                    result = {
                        'success': True,
                        'slot_name': slot_name,
                        'execution_id': execution_id,
                        'scraper_result': scraper_result,
                        'processor_result': processor_result,
                        'files_downloaded': len(downloaded_files),
                        'excel_created': processor_result.get('success', False)
                    }
                    
                    logger.success(f"Manual slot completed successfully: {slot_name}", "Scheduler", execution_id)
                    return result
                else:
                    return {
                        'success': False,
                        'error': 'No files downloaded',
                        'slot_name': slot_name,
                        'scraper_result': scraper_result
                    }
            else:
                return {
                    'success': False,
                    'error': scraper_result.get('error', 'Scraping failed'),
                    'slot_name': slot_name,
                    'scraper_result': scraper_result
                }
                
        except Exception as e:
            logger.error(f"Manual slot execution failed: {e}", "Scheduler", execution_id)
            return {
                'success': False,
                'error': str(e),
                'slot_name': slot_name
            }
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        with self.lock:
            return {
                'is_running': self.is_running,
                'current_executions': self.current_executions.copy(),
                'slot_data_summary': {
                    slot: len(files) for slot, files in self.slot_data.items()
                },
                'execution_history': self.execution_history[-10:],  # Last 10 executions
                'next_scheduled_runs': [
                    {
                        'slot': slot['name'],
                        'time': slot['time'],
                        'next_run': schedule.next_run()
                    } for slot in self.slots
                ]
            }
    
    def clear_slot_data(self):
        """Clear stored slot data"""
        with self.lock:
            self.slot_data.clear()
            logger.info("Slot data cleared", "Scheduler", "clear")


# Global scheduler instance
wifi_scheduler = WiFiDataScheduler()


# Convenience functions for external use
def start_wifi_scheduler():
    """Start the WiFi data scheduler"""
    wifi_scheduler.start_scheduler()


def stop_wifi_scheduler():
    """Stop the WiFi data scheduler"""
    wifi_scheduler.stop_scheduler()


def execute_manual_extraction(slot_name: str = None) -> Dict[str, Any]:
    """Execute manual data extraction"""
    return wifi_scheduler.execute_manual_slot(slot_name)


def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status"""
    return wifi_scheduler.get_scheduler_status()


def clear_scheduler_data():
    """Clear scheduler data"""
    wifi_scheduler.clear_slot_data()

if __name__ == "__main__":
    # Test the scheduler
    print("Starting automation scheduler...")
    start_wifi_scheduler()
    
    try:
        while True:
            status = get_scheduler_status()
            print(f"Scheduler status: {status}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping automation scheduler...")
        stop_wifi_scheduler()