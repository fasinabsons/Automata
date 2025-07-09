#!/usr/bin/env python3
"""
Complete Working System - Integration of ALL Proven Working Ideas
Ensures nothing is missed from the successful implementations
FIXED: Consistent folder naming (08jul, 09jul, 08aug)
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import ALL working components
from modules.dynamic_file_manager import DynamicFileManager
from modules.csv_to_excel_processor import CSVToExcelProcessor
from corrected_wifi_app import CorrectedWiFiApp
from working_email_notifications import WorkingEmailNotifications

class CompleteWorkingSystem:
    """Complete working system with consistent folder naming - FIXED"""
    
    def __init__(self):
        print("🚀 Initializing Complete Working System with consistent folder naming...")
        
        # Initialize dynamic file manager for consistent folder naming
        self.file_manager = DynamicFileManager()
        
        # Initialize components
        self.wifi_app = CorrectedWiFiApp()
        self.csv_processor = CSVToExcelProcessor()
        self.email_service = WorkingEmailNotifications()
        
        # Get consistent folder paths
        self.folders = self.file_manager.create_date_directories()
        self.csv_dir = self.folders['csv']
        self.merge_dir = self.folders['merge']
        self.date_folder = self.folders['date_folder']
        
        print(f"📅 Using consistent date folder: {self.date_folder}")
        print(f"📁 CSV Directory: {self.csv_dir}")
        print(f"📊 Excel Directory: {self.merge_dir}")
        
        # Minimum files for Excel generation
        self.minimum_files = 8
        
        print("✅ Complete Working System initialized with consistent folder naming!")
    
    def check_current_status(self) -> Dict[str, Any]:
        """Check current file status with consistent folder naming"""
        try:
            print(f"\n📊 Checking current status for {self.date_folder}...")
            
            # Count CSV files in consistent folder
            csv_count = self.file_manager.count_csv_files_today()
            
            # Check if Excel exists in consistent merge folder
            excel_files = list(self.merge_dir.glob("*.xls"))
            excel_exists = len(excel_files) > 0
            
            # Get file details
            csv_files = list(self.csv_dir.glob("*.csv"))
            
            status = {
                "date_folder": self.date_folder,
                "csv_count": csv_count,
                "csv_files": [f.name for f in csv_files],
                "excel_exists": excel_exists,
                "excel_files": [f.name for f in excel_files],
                "needs_more_files": csv_count < self.minimum_files,
                "files_needed": max(0, self.minimum_files - csv_count),
                "can_generate_excel": csv_count >= self.minimum_files and not excel_exists
            }
            
            print(f"📁 Current status for {self.date_folder}:")
            print(f"  📄 CSV files: {csv_count}/{self.minimum_files}")
            print(f"  📊 Excel exists: {excel_exists}")
            print(f"  🎯 Can generate Excel: {status['can_generate_excel']}")
            
            return status
            
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            return {"error": str(e)}
    
    def run_wifi_download(self) -> Dict[str, Any]:
        """Run WiFi download with consistent folder naming"""
        try:
            print(f"\n🌐 Starting WiFi download for {self.date_folder}...")
            
            # Get initial file count
            initial_count = self.file_manager.count_csv_files_today()
            print(f"📊 Initial CSV files: {initial_count}")
            
            # Run WiFi automation
            result = self.wifi_app.run_robust_automation()
            
            if result and result.get("success"):
                # Get final file count
                final_count = self.file_manager.count_csv_files_today()
                new_files = final_count - initial_count
                
                print(f"✅ WiFi download successful!")
                print(f"📊 Files downloaded: {new_files}")
                print(f"📊 Total files now: {final_count}")
                
                return {
                    "success": True,
                    "files_downloaded": new_files,
                    "total_files": final_count,
                    "date_folder": self.date_folder
                }
            else:
                error_msg = result.get("error", "Unknown error") if result else "No result returned"
                print(f"❌ WiFi download failed: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            print(f"❌ WiFi download error: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_excel_if_ready(self) -> Dict[str, Any]:
        """Generate Excel file if 8+ files are available"""
        try:
            print(f"\n📊 Checking Excel generation for {self.date_folder}...")
            
            # Check current status
            status = self.check_current_status()
            
            if status.get("can_generate_excel"):
                print(f"🎯 Generating Excel for {self.date_folder}...")
                
                # Generate Excel using consistent folder naming
                result = self.csv_processor.process_and_generate_excel()
                
                if result.get("success"):
                    excel_file = result.get("file_path")
                    records_count = result.get("records_written", 0)
                    
                    print(f"✅ Excel generated successfully!")
                    print(f"📊 File: {excel_file}")
                    print(f"📊 Records: {records_count}")
                    
                    # Send email notification
                    try:
                        self.email_service.send_excel_generation_notification(
                            excel_file=excel_file,
                            records_count=records_count
                        )
                        print("📧 Email notification sent!")
                    except Exception as e:
                        print(f"⚠️ Email notification failed: {e}")
                    
                    return {
                        "success": True,
                        "excel_file": excel_file,
                        "records_count": records_count,
                        "date_folder": self.date_folder
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    print(f"❌ Excel generation failed: {error_msg}")
                    return {"success": False, "error": error_msg}
            else:
                csv_count = status.get("csv_count", 0)
                files_needed = status.get("files_needed", 0)
                excel_exists = status.get("excel_exists", False)
                
                if excel_exists:
                    print(f"ℹ️ Excel already exists for {self.date_folder}")
                    return {"success": True, "message": "Excel already exists"}
                else:
                    print(f"ℹ️ Need {files_needed} more files for Excel generation ({csv_count}/{self.minimum_files})")
                    return {"success": False, "message": f"Need {files_needed} more files"}
                    
        except Exception as e:
            print(f"❌ Excel generation error: {e}")
            return {"success": False, "error": str(e)}
    
    def ensure_minimum_files(self) -> Dict[str, Any]:
        """Ensure minimum 8 files by downloading if needed"""
        try:
            print(f"\n🎯 Ensuring minimum {self.minimum_files} files for {self.date_folder}...")
            
            status = self.check_current_status()
            current_files = status.get("csv_count", 0)
            
            if current_files >= self.minimum_files:
                print(f"✅ Already have sufficient files: {current_files}/{self.minimum_files}")
                return {"success": True, "message": "Sufficient files already available"}
            
            files_needed = self.minimum_files - current_files
            print(f"📥 Need to download {files_needed} more files...")
            
            # Calculate how many download cycles needed (4 files per cycle)
            files_per_cycle = 4
            cycles_needed = (files_needed + files_per_cycle - 1) // files_per_cycle  # Ceiling division
            
            print(f"🔄 Will run {cycles_needed} download cycle(s) to reach {self.minimum_files} files")
            
            total_downloaded = 0
            
            for cycle in range(cycles_needed):
                print(f"\n🔄 Download cycle {cycle + 1}/{cycles_needed}...")
                
                download_result = self.run_wifi_download()
                
                if download_result.get("success"):
                    files_downloaded = download_result.get("files_downloaded", 0)
                    total_downloaded += files_downloaded
                    
                    current_total = download_result.get("total_files", 0)
                    print(f"✅ Cycle {cycle + 1} completed: +{files_downloaded} files (total: {current_total})")
                    
                    if current_total >= self.minimum_files:
                        print(f"🎉 Reached minimum files: {current_total}/{self.minimum_files}")
                        break
                else:
                    print(f"❌ Cycle {cycle + 1} failed: {download_result.get('error', 'Unknown error')}")
                
                # Wait between cycles
                if cycle < cycles_needed - 1:
                    print("⏳ Waiting 30 seconds before next cycle...")
                    time.sleep(30)
            
            # Final status check
            final_status = self.check_current_status()
            final_count = final_status.get("csv_count", 0)
            
            return {
                "success": final_count >= self.minimum_files,
                "total_downloaded": total_downloaded,
                "final_count": final_count,
                "minimum_reached": final_count >= self.minimum_files,
                "date_folder": self.date_folder
            }
            
        except Exception as e:
            print(f"❌ Error ensuring minimum files: {e}")
            return {"success": False, "error": str(e)}
    
    def run_complete_cycle(self) -> Dict[str, Any]:
        """Run complete automation cycle with consistent folder naming"""
        try:
            print("=" * 70)
            print("🚀 COMPLETE WORKING SYSTEM - CONSISTENT FOLDER NAMING")
            print("=" * 70)
            print(f"📅 Date folder: {self.date_folder}")
            print(f"📁 CSV folder: {self.csv_dir}")
            print(f"📊 Excel folder: {self.merge_dir}")
            
            # Step 1: Check current status
            print("\n📊 Step 1: Checking current status...")
            status = self.check_current_status()
            
            if status.get("error"):
                return {"success": False, "error": status["error"]}
            
            # Step 2: Ensure minimum files
            print(f"\n📥 Step 2: Ensuring minimum {self.minimum_files} files...")
            ensure_result = self.ensure_minimum_files()
            
            if not ensure_result.get("success"):
                print(f"❌ Failed to ensure minimum files: {ensure_result.get('error', 'Unknown error')}")
                return ensure_result
            
            # Step 3: Generate Excel if ready
            print(f"\n📊 Step 3: Generating Excel for {self.date_folder}...")
            excel_result = self.generate_excel_if_ready()
            
            # Final summary
            final_status = self.check_current_status()
            
            result = {
                "success": True,
                "date_folder": self.date_folder,
                "csv_folder": str(self.csv_dir),
                "excel_folder": str(self.merge_dir),
                "csv_count": final_status.get("csv_count", 0),
                "excel_generated": excel_result.get("success", False),
                "excel_file": excel_result.get("excel_file"),
                "total_downloaded": ensure_result.get("total_downloaded", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            print("\n" + "=" * 70)
            print("✅ COMPLETE CYCLE FINISHED!")
            print(f"📅 Date folder: {result['date_folder']}")
            print(f"📄 CSV files: {result['csv_count']}")
            print(f"📊 Excel generated: {result['excel_generated']}")
            print(f"📥 Files downloaded: {result['total_downloaded']}")
            print("=" * 70)
            
            return result
            
        except Exception as e:
            print(f"❌ Complete cycle error: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Main function"""
    try:
        system = CompleteWorkingSystem()
        result = system.run_complete_cycle()
        
        if result.get("success"):
            print("\n🎉 SUCCESS! Complete working system executed successfully!")
            print(f"📂 Consistent folder structure maintained: {result.get('date_folder')}")
        else:
            print(f"\n❌ FAILED! Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ System error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    main() 