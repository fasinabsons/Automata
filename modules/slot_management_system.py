#!/usr/bin/env python3
"""
Slot Management System
Handles missed slots, file counting, and ensures proper file download logic
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import glob

# Add project root to path
project_root = Path(__file__).parent.pareT  nt
sys.path.insert(0, str(project_root))

from core.logger import logger

class SlotManagementSystem:
    """
    Comprehensive slot management system for handling missed slots and file counting
    """
    
    def __init__(self):
        """Initialize Slot Management System"""
        self.config = {
            "target_files_per_day": 8,  # Target 8 files per day
            "files_per_slot": 4,        # 4 files per slot
            "slots_per_day": 2,         # 2 slots per day
            "slot_times": {
                "slot1": "14:00",       # 2:00 PM
                "slot2": "18:00"        # 6:00 PM
            },
            "data_folder": "EHC_Data",
            "merge_folder": "EHC_Data_Merge",
            "pdf_folder": "EHC_Data_Pdf",
            "logs_folder": "EHC_Logs"
        }
        
        # Create folders if they don't exist
        self._ensure_folders_exist()
        
        logger.info("Slot Management System initialized", "SlotManager")
    
    def _ensure_folders_exist(self):
        """Ensure all required folders exist"""
        try:
            for folder in [self.config["data_folder"], self.config["merge_folder"], 
                          self.config["pdf_folder"], self.config["logs_folder"]]:
                Path(folder).mkdir(exist_ok=True)
            
            logger.info("All required folders verified/created", "SlotManager")
            
        except Exception as e:
            logger.error(f"Error creating folders: {e}", "SlotManager")
    
    def analyze_current_day_status(self, date_folder: str) -> Dict[str, any]:
        """
        Analyze current day's file status and determine what needs to be done
        
        Args:
            date_folder: Date folder name (e.g., "04july", "05july")
            
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info(f"📊 Analyzing status for {date_folder}", "SlotManager")
            
            # Get current file count
            current_files = self._count_current_files(date_folder)
            
            # Determine current time and slot status
            current_time = datetime.now().strftime("%H:%M")
            slot_status = self._determine_slot_status(current_time)
            
            # Calculate what's needed
            analysis = {
                "date_folder": date_folder,
                "current_time": current_time,
                "current_file_count": current_files,
                "target_file_count": self.config["target_files_per_day"],
                "files_needed": max(0, self.config["target_files_per_day"] - current_files),
                "slot_status": slot_status,
                "missed_slots": self._identify_missed_slots(current_time, current_files),
                "action_required": self._determine_action_required(current_files, slot_status),
                "next_slot_time": self._get_next_slot_time(current_time),
                "can_download_now": self._can_download_now(current_time, current_files)
            }
            
            logger.info(f"📋 Analysis complete: {analysis['action_required']}", "SlotManager")
            return analysis
            
        except Exception as e:
            error_msg = f"Error analyzing day status: {e}"
            logger.error(error_msg, "SlotManager")
            return {"error": error_msg}
    
    def _count_current_files(self, date_folder: str) -> int:
        """Count current files in the date folder"""
        try:
            folder_path = Path(self.config["data_folder"]) / date_folder
            
            if not folder_path.exists():
                logger.info(f"Folder {folder_path} doesn't exist yet", "SlotManager")
                return 0
            
            # Count CSV files
            csv_files = list(folder_path.glob("*.csv"))
            file_count = len(csv_files)
            
            logger.info(f"📁 Found {file_count} files in {date_folder}", "SlotManager")
            return file_count
            
        except Exception as e:
            logger.error(f"Error counting files: {e}", "SlotManager")
            return 0
    
    def _determine_slot_status(self, current_time: str) -> Dict[str, any]:
        """Determine current slot status based on time"""
        try:
            current_hour_min = datetime.strptime(current_time, "%H:%M").time()
            slot1_time = datetime.strptime(self.config["slot_times"]["slot1"], "%H:%M").time()
            slot2_time = datetime.strptime(self.config["slot_times"]["slot2"], "%H:%M").time()
            
            status = {
                "current_slot": None,
                "slot1_passed": current_hour_min >= slot1_time,
                "slot2_passed": current_hour_min >= slot2_time,
                "in_slot1_window": False,
                "in_slot2_window": False
            }
            
            # Check if we're in a slot window (within 2 hours of slot time)
            slot1_end = (datetime.combine(datetime.today(), slot1_time) + timedelta(hours=2)).time()
            slot2_end = (datetime.combine(datetime.today(), slot2_time) + timedelta(hours=2)).time()
            
            if slot1_time <= current_hour_min <= slot1_end:
                status["current_slot"] = "slot1"
                status["in_slot1_window"] = True
            elif slot2_time <= current_hour_min <= slot2_end:
                status["current_slot"] = "slot2"
                status["in_slot2_window"] = True
            
            return status
            
        except Exception as e:
            logger.error(f"Error determining slot status: {e}", "SlotManager")
            return {"error": str(e)}
    
    def _identify_missed_slots(self, current_time: str, current_files: int) -> List[str]:
        """Identify which slots have been missed"""
        try:
            missed_slots = []
            slot_status = self._determine_slot_status(current_time)
            
            # If slot1 time has passed but we have less than 4 files, slot1 was missed
            if slot_status["slot1_passed"] and current_files < 4:
                missed_slots.append("slot1")
            
            # If slot2 time has passed but we have less than 8 files, slot2 was missed
            if slot_status["slot2_passed"] and current_files < 8:
                missed_slots.append("slot2")
            
            logger.info(f"🎯 Missed slots identified: {missed_slots}", "SlotManager")
            return missed_slots
            
        except Exception as e:
            logger.error(f"Error identifying missed slots: {e}", "SlotManager")
            return []
    
    def _determine_action_required(self, current_files: int, slot_status: Dict[str, any]) -> str:
        """Determine what action is required"""
        try:
            target_files = self.config["target_files_per_day"]
            
            if current_files >= target_files:
                return "complete"  # All files downloaded
            
            if slot_status.get("in_slot1_window") or slot_status.get("in_slot2_window"):
                return "download_now"  # In slot window, download now
            
            if current_files < target_files:
                return "wait_for_slot"  # Wait for next slot
            
            return "monitor"  # Just monitor
            
        except Exception as e:
            logger.error(f"Error determining action: {e}", "SlotManager")
            return "error"
    
    def _get_next_slot_time(self, current_time: str) -> Optional[str]:
        """Get the next slot time"""
        try:
            current_hour_min = datetime.strptime(current_time, "%H:%M").time()
            slot1_time = datetime.strptime(self.config["slot_times"]["slot1"], "%H:%M").time()
            slot2_time = datetime.strptime(self.config["slot_times"]["slot2"], "%H:%M").time()
            
            if current_hour_min < slot1_time:
                return self.config["slot_times"]["slot1"]
            elif current_hour_min < slot2_time:
                return self.config["slot_times"]["slot2"]
            else:
                # Next day's slot1
                return f"Tomorrow {self.config['slot_times']['slot1']}"
            
        except Exception as e:
            logger.error(f"Error getting next slot time: {e}", "SlotManager")
            return None
    
    def _can_download_now(self, current_time: str, current_files: int) -> bool:
        """Determine if we can download now"""
        try:
            slot_status = self._determine_slot_status(current_time)
            
            # Can download if we're in a slot window and don't have all files
            if slot_status.get("in_slot1_window") or slot_status.get("in_slot2_window"):
                return current_files < self.config["target_files_per_day"]
            
            # Can download if we have missed slots
            missed_slots = self._identify_missed_slots(current_time, current_files)
            if missed_slots:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking download permission: {e}", "SlotManager")
            return False
    
    def calculate_files_to_download(self, date_folder: str) -> Dict[str, any]:
        """
        Calculate how many files need to be downloaded
        
        Args:
            date_folder: Date folder name
            
        Returns:
            Dictionary with download calculation
        """
        try:
            analysis = self.analyze_current_day_status(date_folder)
            
            if "error" in analysis:
                return analysis
            
            current_files = analysis["current_file_count"]
            target_files = self.config["target_files_per_day"]
            files_needed = max(0, target_files - current_files)
            
            calculation = {
                "date_folder": date_folder,
                "current_files": current_files,
                "target_files": target_files,
                "files_needed": files_needed,
                "should_download": files_needed > 0 and analysis["can_download_now"],
                "download_reason": self._get_download_reason(analysis),
                "priority": self._get_download_priority(analysis)
            }
            
            logger.info(f"📊 Download calculation: Need {files_needed} files", "SlotManager")
            return calculation
            
        except Exception as e:
            error_msg = f"Error calculating files to download: {e}"
            logger.error(error_msg, "SlotManager")
            return {"error": error_msg}
    
    def _get_download_reason(self, analysis: Dict[str, any]) -> str:
        """Get reason for download"""
        try:
            if analysis["missed_slots"]:
                return f"Missed slots: {', '.join(analysis['missed_slots'])}"
            
            if analysis["slot_status"].get("in_slot1_window"):
                return "In Slot 1 window"
            
            if analysis["slot_status"].get("in_slot2_window"):
                return "In Slot 2 window"
            
            return "Regular download"
            
        except Exception as e:
            return f"Error determining reason: {e}"
    
    def _get_download_priority(self, analysis: Dict[str, any]) -> str:
        """Get download priority"""
        try:
            if analysis["missed_slots"]:
                return "high"  # High priority for missed slots
            
            if analysis["slot_status"].get("in_slot1_window") or analysis["slot_status"].get("in_slot2_window"):
                return "normal"  # Normal priority for slot windows
            
            return "low"  # Low priority otherwise
            
        except Exception as e:
            return "unknown"
    
    def should_run_automation(self, date_folder: str) -> Dict[str, any]:
        """
        Determine if automation should run now
        
        Args:
            date_folder: Date folder name
            
        Returns:
            Dictionary with decision and reasoning
        """
        try:
            logger.info(f"🤔 Checking if automation should run for {date_folder}", "SlotManager")
            
            analysis = self.analyze_current_day_status(date_folder)
            
            if "error" in analysis:
                return analysis
            
            decision = {
                "should_run": False,
                "reason": "",
                "priority": "low",
                "wait_time": 0,
                "analysis": analysis
            }
            
            # Decision logic
            if analysis["action_required"] == "complete":
                decision["reason"] = "All files already downloaded"
                decision["should_run"] = False
                
            elif analysis["action_required"] == "download_now":
                decision["reason"] = "In slot window - download now"
                decision["should_run"] = True
                decision["priority"] = "normal"
                
            elif analysis["missed_slots"]:
                decision["reason"] = f"Missed slots need to be filled: {', '.join(analysis['missed_slots'])}"
                decision["should_run"] = True
                decision["priority"] = "high"
                
            elif analysis["action_required"] == "wait_for_slot":
                decision["reason"] = f"Waiting for next slot: {analysis['next_slot_time']}"
                decision["should_run"] = False
                decision["wait_time"] = self._calculate_wait_time(analysis["next_slot_time"])
            
            logger.info(f"🎯 Decision: {decision['should_run']} - {decision['reason']}", "SlotManager")
            return decision
            
        except Exception as e:
            error_msg = f"Error determining automation run: {e}"
            logger.error(error_msg, "SlotManager")
            return {"error": error_msg}
    
    def _calculate_wait_time(self, next_slot_time: str) -> int:
        """Calculate wait time until next slot in minutes"""
        try:
            if not next_slot_time or "Tomorrow" in next_slot_time:
                return 60  # Default 1 hour wait
            
            current_time = datetime.now().strftime("%H:%M")
            current_dt = datetime.strptime(current_time, "%H:%M")
            next_dt = datetime.strptime(next_slot_time, "%H:%M")
            
            # If next slot is tomorrow, add 24 hours
            if next_dt <= current_dt:
                next_dt += timedelta(days=1)
            
            wait_minutes = int((next_dt - current_dt).total_seconds() / 60)
            return max(15, wait_minutes)  # Minimum 15 minutes
            
        except Exception as e:
            logger.error(f"Error calculating wait time: {e}", "SlotManager")
            return 60  # Default 1 hour
    
    def log_slot_activity(self, date_folder: str, activity: str, details: Dict[str, any]):
        """Log slot-related activity"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "date_folder": date_folder,
                "activity": activity,
                "details": details
            }
            
            # Log to file
            log_file = Path(self.config["logs_folder"]) / f"slot_activity_{date_folder}.log"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{log_entry}\n")
            
            logger.info(f"📝 Logged activity: {activity} for {date_folder}", "SlotManager")
            
        except Exception as e:
            logger.error(f"Error logging slot activity: {e}", "SlotManager")
    
    def get_daily_summary(self, date_folder: str) -> Dict[str, any]:
        """Get daily summary of slot activities"""
        try:
            analysis = self.analyze_current_day_status(date_folder)
            
            summary = {
                "date_folder": date_folder,
                "generated_at": datetime.now().isoformat(),
                "file_status": {
                    "current_files": analysis.get("current_file_count", 0),
                    "target_files": self.config["target_files_per_day"],
                    "completion_percentage": (analysis.get("current_file_count", 0) / self.config["target_files_per_day"]) * 100
                },
                "slot_status": analysis.get("slot_status", {}),
                "missed_slots": analysis.get("missed_slots", []),
                "next_action": analysis.get("action_required", "unknown"),
                "next_slot_time": analysis.get("next_slot_time"),
                "recommendations": self._generate_recommendations(analysis)
            }
            
            return summary
            
        except Exception as e:
            error_msg = f"Error generating daily summary: {e}"
            logger.error(error_msg, "SlotManager")
            return {"error": error_msg}
    
    def _generate_recommendations(self, analysis: Dict[str, any]) -> List[str]:
        """Generate recommendations based on analysis"""
        try:
            recommendations = []
            
            if analysis.get("missed_slots"):
                recommendations.append("🚨 Missed slots detected - run automation immediately to catch up")
            
            if analysis.get("current_file_count", 0) < self.config["target_files_per_day"]:
                recommendations.append(f"📊 Need {analysis.get('files_needed', 0)} more files to reach daily target")
            
            if analysis.get("action_required") == "wait_for_slot":
                recommendations.append(f"⏰ Wait for next slot at {analysis.get('next_slot_time')}")
            
            if analysis.get("action_required") == "complete":
                recommendations.append("✅ Daily target achieved - no further action needed")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}", "SlotManager")
            return ["⚠️ Error generating recommendations"]

# Integration function for existing system
def check_slot_status_and_run(date_folder: str) -> Dict[str, any]:
    """
    Main integration function to check slot status and determine if automation should run
    
    Args:
        date_folder: Date folder name
        
    Returns:
        Dictionary with decision and details
    """
    try:
        slot_manager = SlotManagementSystem()
        
        # Get automation decision
        decision = slot_manager.should_run_automation(date_folder)
        
        if decision.get("should_run"):
            # Log the decision
            slot_manager.log_slot_activity(
                date_folder, 
                "automation_triggered", 
                {"reason": decision.get("reason"), "priority": decision.get("priority")}
            )
            
            # Get download calculation
            download_calc = slot_manager.calculate_files_to_download(date_folder)
            decision["download_calculation"] = download_calc
        
        return decision
        
    except Exception as e:
        error_msg = f"Error in slot status check: {e}"
        logger.error(error_msg, "SlotManager")
        return {"error": error_msg}

# Test function
def test_slot_management():
    """Test slot management system"""
    print("🧪 Testing Slot Management System")
    print("=" * 50)
    
    slot_manager = SlotManagementSystem()
    
    # Test with current date
    today = datetime.now()
    test_date_folder = f"{today.day:02d}{today.strftime('%B').lower()}"
    
    print(f"\n📅 Testing with date folder: {test_date_folder}")
    
    # Test analysis
    print("\n1. Analyzing current day status...")
    analysis = slot_manager.analyze_current_day_status(test_date_folder)
    print(f"   Analysis: {analysis}")
    
    # Test automation decision
    print("\n2. Checking automation decision...")
    decision = slot_manager.should_run_automation(test_date_folder)
    print(f"   Decision: {decision}")
    
    # Test download calculation
    print("\n3. Calculating download requirements...")
    download_calc = slot_manager.calculate_files_to_download(test_date_folder)
    print(f"   Download calculation: {download_calc}")
    
    # Test daily summary
    print("\n4. Generating daily summary...")
    summary = slot_manager.get_daily_summary(test_date_folder)
    print(f"   Summary: {summary}")
    
    print("\n✅ Slot Management System testing completed")

if __name__ == "__main__":
    test_slot_management() 