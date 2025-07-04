#!/usr/bin/env python3
"""
WiFi Data Automation System - Main Application
Complete system with interactive user input loop
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Local imports
from config.settings import (
    WIFI_CONFIG, SCHEDULE_CONFIG, FILE_CONFIG, 
    CHROME_CONFIG, ERROR_CONFIG, DEBUG_CONFIG
)
from core.logger import logger
from modules.scheduler import (
    start_wifi_scheduler, stop_wifi_scheduler, 
    execute_manual_extraction, get_scheduler_status,
    clear_scheduler_data
)
from modules.hybrid_web_scraper import execute_bulletproof_scraping
from modules.file_processor import process_wifi_data, merge_slot_data
from modules.email_service import EmailService


class WiFiAutomationSystem:
    """
    Complete WiFi Data Automation System
    """
    
    def __init__(self):
        self.system_status = {
            'initialized': False,
            'scheduler_running': False,
            'last_execution': None,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0
        }
        
        # Initialize directories
        self._initialize_directories()
        
        # Initialize services
        self.email_service = EmailService()
        
        logger.info("WiFi Automation System initialized", "MainSystem", "init")
        self.system_status['initialized'] = True
    
    def _initialize_directories(self):
        """Initialize all required directories"""
        try:
            logger.info("Initializing directory structure", "MainSystem", "init")
            
            # Create base directories
            base_dirs = [
                Path("EHC_Data"),
                Path("EHC_Data_Merge"),
                Path("EHC_Data_Pdf"),
                Path("logs"),
                Path("downloads"),
                Path("temp")
            ]
            
            for directory in base_dirs:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory created/verified: {directory}", "MainSystem", "init")
            
            # Create date-based subdirectories for current month
            current_date = datetime.now()
            date_folder = current_date.strftime(FILE_CONFIG['date_folder_format'])
            
            date_dirs = [
                Path(f"EHC_Data/{date_folder}"),
                Path(f"EHC_Data_Merge/{date_folder}"),
                Path(f"EHC_Data_Pdf/{date_folder}")
            ]
            
            for directory in date_dirs:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Date directory created: {directory}", "MainSystem", "init")
            
            logger.success("Directory structure initialized successfully", "MainSystem", "init")
            
        except Exception as e:
            logger.error(f"Failed to initialize directories: {e}", "MainSystem", "init")
            raise
    
    def start_system(self):
        """Start the complete automation system"""
        try:
            logger.info("Starting WiFi Automation System", "MainSystem", "start")
            
            # Start scheduler
            start_wifi_scheduler()
            self.system_status['scheduler_running'] = True
            
            logger.success("WiFi Automation System started successfully", "MainSystem", "start")
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}", "MainSystem", "start")
            raise
    
    def stop_system(self):
        """Stop the automation system"""
        try:
            logger.info("Stopping WiFi Automation System", "MainSystem", "stop")
            
            # Stop scheduler
            stop_wifi_scheduler()
            self.system_status['scheduler_running'] = False
            
            logger.success("WiFi Automation System stopped successfully", "MainSystem", "stop")
            
        except Exception as e:
            logger.error(f"Failed to stop system: {e}", "MainSystem", "stop")
    
    def execute_manual_test(self, test_type: str = "full") -> Dict[str, Any]:
        """Execute manual test of the system"""
        try:
            test_id = f"test_{int(datetime.now().timestamp())}"
            logger.info(f"Starting manual test: {test_type}", "MainSystem", test_id)
            
            if test_type == "scraping":
                # Test scraping only
                result = execute_bulletproof_scraping(f"test_scraping_{test_id}")
                
            elif test_type == "processing":
                # Test file processing (requires existing CSV files)
                csv_files = list(Path("EHC_Data").rglob("*.csv"))
                if csv_files:
                    result = process_wifi_data(csv_files[:3], f"test_processing_{test_id}")
                else:
                    result = {
                        'success': False,
                        'error': 'No CSV files found for processing test'
                    }
                    
            elif test_type == "full":
                # Test complete workflow
                result = execute_manual_extraction(f"test_full_{test_id}")
                
            else:
                result = {
                    'success': False,
                    'error': f'Unknown test type: {test_type}'
                }
            
            # Update statistics
            self.system_status['total_executions'] += 1
            if result.get('success', False):
                self.system_status['successful_executions'] += 1
            else:
                self.system_status['failed_executions'] += 1
            
            self.system_status['last_execution'] = {
                'timestamp': datetime.now().isoformat(),
                'type': f'manual_test_{test_type}',
                'success': result.get('success', False),
                'result': result
            }
            
            logger.success(f"Manual test completed: {test_type}", "MainSystem", test_id)
            return result
            
        except Exception as e:
            logger.error(f"Manual test failed: {e}", "MainSystem", test_id)
            self.system_status['failed_executions'] += 1
            return {
                'success': False,
                'error': str(e),
                'test_type': test_type
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        try:
            # Get scheduler status
            scheduler_status = get_scheduler_status()
            
            # Get file system status
            file_status = self._get_file_system_status()
            
            # Combine all status information
            complete_status = {
                'system': self.system_status,
                'scheduler': scheduler_status,
                'files': file_status,
                'configuration': {
                    'target_url': WIFI_CONFIG['target_url'],
                    'networks_configured': len(WIFI_CONFIG['networks_to_extract']),
                    'slots_configured': len(SCHEDULE_CONFIG['slots']),
                    'chrome_headless': CHROME_CONFIG['headless']
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return complete_status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}", "MainSystem", "status")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_file_system_status(self) -> Dict[str, Any]:
        """Get file system status"""
        try:
            # Count files in various directories
            csv_files = list(Path("EHC_Data").rglob("*.csv"))
            excel_files = list(Path("EHC_Data_Merge").rglob("*.xlsx"))
            pdf_files = list(Path("EHC_Data_Pdf").rglob("*.pdf"))
            
            # Get recent files
            recent_csv = sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            recent_excel = sorted(excel_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            
            return {
                'csv_files_count': len(csv_files),
                'excel_files_count': len(excel_files),
                'pdf_files_count': len(pdf_files),
                'recent_csv_files': [str(f) for f in recent_csv],
                'recent_excel_files': [str(f) for f in recent_excel],
                'disk_usage': self._get_disk_usage()
            }
            
        except Exception as e:
            logger.error(f"Failed to get file system status: {e}", "MainSystem", "files")
            return {'error': str(e)}
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            import shutil
            
            # Get disk usage for main directories
            ehc_data_usage = shutil.disk_usage("EHC_Data")
            
            return {
                'total_space_gb': round(ehc_data_usage.total / (1024**3), 2),
                'used_space_gb': round(ehc_data_usage.used / (1024**3), 2),
                'free_space_gb': round(ehc_data_usage.free / (1024**3), 2),
                'usage_percentage': round((ehc_data_usage.used / ehc_data_usage.total) * 100, 2)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_system(self):
        """Clean up system files and data"""
        try:
            logger.info("Starting system cleanup", "MainSystem", "cleanup")
            
            # Clear scheduler data
            clear_scheduler_data()
            
            # Clean up temporary files
            temp_dir = Path("temp")
            if temp_dir.exists():
                for file in temp_dir.rglob("*"):
                    if file.is_file():
                        try:
                            file.unlink()
                        except:
                            pass
            
            # Clean up old log files
            log_dir = Path("logs")
            if log_dir.exists():
                log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime)
                if len(log_files) > 10:  # Keep only last 10 log files
                    for old_log in log_files[:-10]:
                        try:
                            old_log.unlink()
                        except:
                            pass
            
            logger.success("System cleanup completed", "MainSystem", "cleanup")
            
        except Exception as e:
            logger.error(f"System cleanup failed: {e}", "MainSystem", "cleanup")
    
    def interactive_menu(self):
        """Interactive menu for system control"""
        while True:
            print("\n" + "="*60)
            print("WiFi Data Automation System - Interactive Menu")
            print("="*60)
            print("1. Start Scheduler")
            print("2. Stop Scheduler")
            print("3. Execute Manual Test (Full)")
            print("4. Execute Manual Test (Scraping Only)")
            print("5. Execute Manual Test (Processing Only)")
            print("6. View System Status")
            print("7. View Recent Files")
            print("8. Send Test Email")
            print("9. Clean Up System")
            print("10. View Configuration")
            print("11. Exit")
            print("="*60)
            
            try:
                choice = input("\nEnter your choice (1-11): ").strip()
                
                if choice == "1":
                    print("\nStarting scheduler...")
                    self.start_system()
                    print("✅ Scheduler started successfully!")
                    
                elif choice == "2":
                    print("\nStopping scheduler...")
                    self.stop_system()
                    print("✅ Scheduler stopped successfully!")
                    
                elif choice == "3":
                    print("\nExecuting full system test...")
                    result = self.execute_manual_test("full")
                    if result['success']:
                        print("✅ Full test completed successfully!")
                        print(f"Files downloaded: {result.get('files_downloaded', 0)}")
                    else:
                        print(f"❌ Full test failed: {result.get('error', 'Unknown error')}")
                        
                elif choice == "4":
                    print("\nExecuting scraping test...")
                    result = self.execute_manual_test("scraping")
                    if result['success']:
                        print("✅ Scraping test completed successfully!")
                        print(f"Files downloaded: {len(result.get('downloaded_files', []))}")
                    else:
                        print(f"❌ Scraping test failed: {result.get('error', 'Unknown error')}")
                        
                elif choice == "5":
                    print("\nExecuting processing test...")
                    result = self.execute_manual_test("processing")
                    if result['success']:
                        print("✅ Processing test completed successfully!")
                        print(f"Records processed: {result.get('total_records', 0)}")
                    else:
                        print(f"❌ Processing test failed: {result.get('error', 'Unknown error')}")
                        
                elif choice == "6":
                    print("\nSystem Status:")
                    print("-" * 40)
                    status = self.get_system_status()
                    
                    # System status
                    sys_status = status.get('system', {})
                    print(f"System Initialized: {sys_status.get('initialized', False)}")
                    print(f"Scheduler Running: {sys_status.get('scheduler_running', False)}")
                    print(f"Total Executions: {sys_status.get('total_executions', 0)}")
                    print(f"Successful: {sys_status.get('successful_executions', 0)}")
                    print(f"Failed: {sys_status.get('failed_executions', 0)}")
                    
                    # File status
                    file_status = status.get('files', {})
                    print(f"CSV Files: {file_status.get('csv_files_count', 0)}")
                    print(f"Excel Files: {file_status.get('excel_files_count', 0)}")
                    
                    # Disk usage
                    disk_usage = file_status.get('disk_usage', {})
                    if 'free_space_gb' in disk_usage:
                        print(f"Free Space: {disk_usage['free_space_gb']} GB")
                    
                elif choice == "7":
                    print("\nRecent Files:")
                    print("-" * 40)
                    status = self.get_system_status()
                    file_status = status.get('files', {})
                    
                    print("Recent CSV Files:")
                    for file in file_status.get('recent_csv_files', []):
                        print(f"  📄 {Path(file).name}")
                    
                    print("\nRecent Excel Files:")
                    for file in file_status.get('recent_excel_files', []):
                        print(f"  📊 {Path(file).name}")
                        
                elif choice == "8":
                    print("\nSending test email...")
                    result = self.email_service.send_test_email()
                    if result['success']:
                        print("✅ Test email sent successfully!")
                    else:
                        print(f"❌ Test email failed: {result.get('error', 'Unknown error')}")
                        
                elif choice == "9":
                    print("\nCleaning up system...")
                    self.cleanup_system()
                    print("✅ System cleanup completed!")
                    
                elif choice == "10":
                    print("\nSystem Configuration:")
                    print("-" * 40)
                    print(f"Target URL: {WIFI_CONFIG['target_url']}")
                    print(f"Networks to Extract: {len(WIFI_CONFIG['networks_to_extract'])}")
                    for net in WIFI_CONFIG['networks_to_extract']:
                        print(f"  - {net['name']} (Page {net['page']})")
                    
                    print(f"\nScheduled Slots: {len(SCHEDULE_CONFIG['slots'])}")
                    for slot in SCHEDULE_CONFIG['slots']:
                        print(f"  - {slot['name']}: {slot['time']}")
                    
                    print(f"\nChrome Headless: {CHROME_CONFIG['headless']}")
                    print(f"Max Execution Time: {SCHEDULE_CONFIG['max_execution_time_minutes']} minutes")
                    
                elif choice == "11":
                    print("\nExiting system...")
                    self.stop_system()
                    print("👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid choice. Please enter a number between 1-11.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting system...")
                self.stop_system()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.error(f"Interactive menu error: {e}", "MainSystem", "menu")


def main():
    """Main function with user input loop"""
    print("🚀 WiFi Data Automation System Starting...")
    print("=" * 60)
    
    try:
        # Initialize system
        system = WiFiAutomationSystem()
        
        # Check if userinput.py exists
        userinput_path = Path("userinput.py")
        if not userinput_path.exists():
            print("Creating userinput.py...")
            with open("userinput.py", "w") as f:
                f.write('user_input = input("prompt: ")\n')
            print("✅ userinput.py created successfully!")
        
        print("✅ System initialized successfully!")
        print("\nStarting interactive user input loop...")
        print("Available commands:")
        print("  - 'menu': Open interactive menu")
        print("  - 'start': Start scheduler")
        print("  - 'stop': Stop scheduler")
        print("  - 'test': Run manual test")
        print("  - 'status': Show system status")
        print("  - 'exit' or 'stop': Exit the system")
        print("\n" + "=" * 60)
        
        # Main user input loop
        while True:
            try:
                # Run userinput.py to get user input
                print("\nRunning userinput.py...")
                os.system("python userinput.py")
                
                # Read the user input (in a real implementation, this would be captured from the subprocess)
                # For now, we'll use direct input
                user_input = input("prompt: ").strip().lower()
                
                print(f"\nUser input received: '{user_input}'")
                
                if user_input == "stop" or user_input == "exit":
                    print("🛑 Stopping system...")
                    system.stop_system()
                    print("👋 System stopped. Goodbye!")
                    break
                
                elif user_input == "menu":
                    system.interactive_menu()
                    
                elif user_input == "start":
                    print("🚀 Starting scheduler...")
                    system.start_system()
                    print("✅ Scheduler started!")
                    
                elif user_input == "stop":
                    print("🛑 Stopping scheduler...")
                    system.stop_system()
                    print("✅ Scheduler stopped!")
                    
                elif user_input == "test":
                    print("🧪 Running manual test...")
                    result = system.execute_manual_test("full")
                    if result['success']:
                        print("✅ Test completed successfully!")
                    else:
                        print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
                        
                elif user_input == "status":
                    print("📊 System Status:")
                    status = system.get_system_status()
                    sys_status = status.get('system', {})
                    print(f"  Scheduler Running: {sys_status.get('scheduler_running', False)}")
                    print(f"  Total Executions: {sys_status.get('total_executions', 0)}")
                    print(f"  Success Rate: {sys_status.get('successful_executions', 0)}/{sys_status.get('total_executions', 0)}")
                    
                elif user_input == "help":
                    print("📋 Available commands:")
                    print("  - 'menu': Open interactive menu")
                    print("  - 'start': Start scheduler")
                    print("  - 'stop': Stop scheduler")
                    print("  - 'test': Run manual test")
                    print("  - 'status': Show system status")
                    print("  - 'help': Show this help")
                    print("  - 'exit' or 'stop': Exit the system")
                    
                else:
                    print(f"❓ Unknown command: '{user_input}'")
                    print("Type 'help' for available commands or 'menu' for interactive menu")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user. Stopping system...")
                system.stop_system()
                break
            except Exception as e:
                print(f"❌ Error processing command: {e}")
                logger.error(f"Command processing error: {e}", "MainSystem", "loop")
                
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.error(f"Critical system error: {e}", "MainSystem", "main")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())