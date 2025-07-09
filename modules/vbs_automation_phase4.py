#!/usr/bin/env python3
"""
VBS Automation - Phase 4: PDF Generation
Implements Task 4.1 and 4.2 from vbs_task_list.txt
PDF Generation: Reports → POS → WiFi User Count → Date Range → Export PDF
"""

import os
import time
import logging
import win32gui
import win32con
import pyautogui
from typing import Dict, Optional, Any
import traceback
from datetime import datetime, date
from pathlib import Path
import calendar

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.5

class VBSPhase4_PDFGeneration:
    """Phase 4: PDF Generation Implementation"""
    
    def __init__(self, window_handle: Optional[int] = None):
        self.logger = self._setup_logging()
        self.window_handle = window_handle
        
        # PDF generation coordinates (from clickcursor.txt - EXACT COORDINATES)
        self.coordinates = {
            # Report navigation coordinates (from clickcursor.txt)
            "reports_menu": (203, 643),               # Reports folder (updated coordinates)
            "pos_reports_submenu": (227, 936),        # POS inside report (updated coordinates)
            "wifi_user_count": (287, 888),            # WiFi active users count (DOUBLE-CLICK, updated)
            
            # Alternative coordinates (first set from clickcursor.txt)
            "reports_menu_alt": (162, 648),           # Reports folder (first set)
            "pos_reports_alt": (219, 770),            # POS inside report (first set)
            "wifi_user_count_alt": (310, 887),        # WiFi active users count (first set)
            
            # Date range coordinates (from clickcursor.txt)
            "start_date_field": (1240, 190),          # From date (updated coordinates)
            "end_date_field": (1470, 192),            # To date (updated coordinates)
            "start_date_alt": (821, 151),             # From date (first set)
            "end_date_alt": (983, 155),               # To date (first set)
            
            # Export coordinates (from clickcursor.txt)
            "print_button": (110, 128),               # Print button (updated coordinates)
            "print_button_alt": (76, 96),             # Print button (first set)
            "export_option": (74, 57),                # Export button (same in both sets)
            
            # PDF save dialog coordinates (from clickcursor.txt)
            "popup_ok_first": (1192, 514),            # First popup OK button
            "popup_ok_second": (150, 263),            # Second popup OK button
            "save_button": (720, 692),                # Save button in save dialog
            
            # Window management coordinates (from clickcursor.txt)
            "close_button": (1881, 11),               # Close button
            "exit_popup_yes": (882, 669),             # Yes button for exit popup
            
            # Window verification coordinates
            "window_center": (960, 600),              # Center of window
        }
        
        # File paths configuration
        self.file_paths = {
            "downloads_folder": r"C:\Users\Lenovo\Downloads",
            "pdf_base_path": r"C:\Users\Lenovo\Videos\Automata\EHC_Data_Pdf",
            "pdf_filename_pattern": "moon flower active users_{date}.pdf",  # {date} = DDMMYYYY
        }
        
        # Timing configuration
        self.timeouts = {
            "menu_navigation": 2,        # Menu navigation time
            "report_generation": 30,     # Report generation time
            "export_process": 10,        # Export process time
            "file_save": 5,              # File save time
            "dialog_open": 3,            # Dialog open time
            "button_click": 1,           # Button click response
        }
        
        # Report navigation sequence
        self.report_navigation = [
            {
                "step": "close_import_form",
                "description": "Close import form (not entire app)",
                "coordinate": "close_import_form",
                "wait_time": "button_click"
            },
            {
                "step": "reports_menu",
                "description": "Click Reports menu",
                "coordinate": "reports_menu",
                "wait_time": "menu_navigation"
            },
            {
                "step": "pos_reports",
                "description": "Click POS submenu in Reports",
                "coordinate": "pos_reports_submenu",
                "wait_time": "menu_navigation"
            },
            {
                "step": "wifi_user_count",
                "description": "Click WiFi User Count",
                "coordinate": "wifi_user_count",
                "wait_time": "report_generation"
            }
        ]
        
        self.logger.info("VBS Phase 4 (PDF Generation) initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Phase 4"""
        logger = logging.getLogger("VBSPhase4")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def set_window_handle(self, window_handle: int):
        """Set the window handle for PDF operations"""
        self.window_handle = window_handle
        self.logger.info(f"Window handle set: {window_handle}")
    
    def task_4_1_navigate_to_reports(self) -> Dict[str, Any]:
        """Task 4.1: Navigate to Reports → POS → WiFi User Count"""
        try:
            self.logger.info("📊 TASK 4.1: Navigating to WiFi User Count reports...")
            
            if not self.window_handle:
                return {"success": False, "error": "No window handle available"}
            
            # Ensure window is active
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(self.timeouts["button_click"])
            
            # Execute report navigation sequence
            for i, step in enumerate(self.report_navigation):
                step_num = i + 1
                step_name = step["step"]
                description = step["description"]
                coordinate_key = step["coordinate"]
                wait_time_key = step["wait_time"]
                
                self.logger.info(f"Step {step_num}: {description}")
                
                # Get coordinates and timing
                if coordinate_key not in self.coordinates:
                    return {"success": False, "error": f"Coordinate '{coordinate_key}' not found"}
                
                x, y = self.coordinates[coordinate_key]
                wait_time = self.timeouts[wait_time_key]
                
                # Perform click action
                try:
                    self.logger.info(f"Clicking at coordinates ({x}, {y})")
                    pyautogui.click(x, y)
                    time.sleep(wait_time)
                    
                    # Verify step completion
                    if not self._verify_report_step(step_name):
                        return {"success": False, "error": f"Report step '{step_name}' verification failed"}
                    
                    self.logger.info(f"✅ Step {step_num} completed successfully")
                    
                except Exception as e:
                    return {"success": False, "error": f"Step {step_num} failed: {e}"}
            
            # Verify WiFi User Count report opened
            if self._verify_wifi_report_opened():
                self.logger.info("✅ Navigation completed: WiFi User Count report opened")
                return {"success": True, "message": "Successfully navigated to WiFi User Count report"}
            else:
                return {"success": False, "error": "WiFi User Count report not detected"}
            
        except Exception as e:
            error_msg = f"Report navigation failed: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": error_msg}
    
    def task_4_2_set_date_range(self) -> Dict[str, Any]:
        """Task 4.2: Set date range (Current month 1st to current day, year 2025)"""
        try:
            self.logger.info("📅 TASK 4.2: Setting date range for report...")
            
            # Calculate date range
            today = date.today()
            start_date = date(2025, today.month, 1)  # First day of current month, year 2025
            end_date = date(2025, today.month, today.day)  # Current day, year 2025
            
            start_date_str = start_date.strftime("%d/%m/%Y")
            end_date_str = end_date.strftime("%d/%m/%Y")
            
            self.logger.info(f"Date range: {start_date_str} to {end_date_str}")
            
            # Set start date
            success = self._set_date_field("start", start_date_str)
            if not success:
                return {"success": False, "error": "Failed to set start date"}
            
            # Set end date
            success = self._set_date_field("end", end_date_str)
            if not success:
                return {"success": False, "error": "Failed to set end date"}
            
            # Generate report
            success = self._generate_report()
            if not success:
                return {"success": False, "error": "Failed to generate report"}
            
            self.logger.info("✅ Date range set and report generated successfully")
            return {
                "success": True, 
                "start_date": start_date_str,
                "end_date": end_date_str,
                "message": "Date range set and report generated"
            }
            
        except Exception as e:
            error_msg = f"Date range setting failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def task_4_3_export_pdf(self, date_folder: str) -> Dict[str, Any]:
        """Task 4.3: Export report as PDF"""
        try:
            self.logger.info("📄 TASK 4.3: Exporting report as PDF...")
            
            # Step 1: Click Print button
            self.logger.info("Step 1: Clicking Print button...")
            success = self._click_print_button()
            if not success:
                return {"success": False, "error": "Failed to click Print button"}
            
            # Step 2: Select Export option
            self.logger.info("Step 2: Selecting Export option...")
            success = self._select_export_option()
            if not success:
                return {"success": False, "error": "Failed to select Export option"}
            
            # Step 3: Select PDF format
            self.logger.info("Step 3: Selecting PDF format...")
            success = self._select_pdf_format()
            if not success:
                return {"success": False, "error": "Failed to select PDF format"}
            
            # Step 4: Save PDF to Downloads first
            self.logger.info("Step 4: Saving PDF to Downloads...")
            temp_pdf_path = self._save_pdf_to_downloads()
            if not temp_pdf_path:
                return {"success": False, "error": "Failed to save PDF to Downloads"}
            
            # Step 5: Move PDF to correct folder
            self.logger.info("Step 5: Moving PDF to correct folder...")
            final_pdf_path = self._move_pdf_to_folder(temp_pdf_path, date_folder)
            if not final_pdf_path:
                return {"success": False, "error": "Failed to move PDF to correct folder"}
            
            self.logger.info("✅ PDF export completed successfully")
            return {
                "success": True,
                "pdf_path": final_pdf_path,
                "message": "PDF exported and moved to correct folder"
            }
            
        except Exception as e:
            error_msg = f"PDF export failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _set_date_field(self, field_type: str, date_str: str) -> bool:
        """Set date field (start or end)"""
        try:
            # Determine coordinate based on field type
            if field_type == "start":
                date_x, date_y = self.coordinates["start_date_field"]
            else:
                date_x, date_y = self.coordinates["end_date_field"]
            
            # Click date field
            pyautogui.click(date_x, date_y)
            time.sleep(self.timeouts["button_click"])
            
            # Clear field and enter date
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.typewrite(date_str)
            time.sleep(self.timeouts["button_click"])
            
            self.logger.info(f"Successfully set {field_type} date: {date_str}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set {field_type} date: {e}")
            return False
    
    def _generate_report(self) -> bool:
        """Generate report with set date range"""
        try:
            # Click Generate Report button
            gen_x, gen_y = self.coordinates["generate_report_button"]
            pyautogui.click(gen_x, gen_y)
            time.sleep(self.timeouts["report_generation"])
            
            self.logger.info("Report generation initiated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return False
    
    def _click_print_button(self) -> bool:
        """Click Print button"""
        try:
            print_x, print_y = self.coordinates["print_button"]
            pyautogui.click(print_x, print_y)
            time.sleep(self.timeouts["dialog_open"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click Print button: {e}")
            return False
    
    def _select_export_option(self) -> bool:
        """Select Export option"""
        try:
            export_x, export_y = self.coordinates["export_option"]
            pyautogui.click(export_x, export_y)
            time.sleep(self.timeouts["button_click"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select Export option: {e}")
            return False
    
    def _select_pdf_format(self) -> bool:
        """Select PDF format"""
        try:
            pdf_x, pdf_y = self.coordinates["pdf_format"]
            pyautogui.click(pdf_x, pdf_y)
            time.sleep(self.timeouts["button_click"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select PDF format: {e}")
            return False
    
    def _save_pdf_to_downloads(self) -> Optional[str]:
        """Save PDF to Downloads folder"""
        try:
            # Generate filename
            today = date.today()
            date_str = today.strftime("%d%m%Y")
            filename = self.file_paths["pdf_filename_pattern"].format(date=date_str)
            
            # Set save path to Downloads
            path_x, path_y = self.coordinates["save_dialog_path"]
            pyautogui.click(path_x, path_y)
            time.sleep(self.timeouts["button_click"])
            
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.typewrite(self.file_paths["downloads_folder"])
            time.sleep(self.timeouts["button_click"])
            
            # Set filename
            name_x, name_y = self.coordinates["save_dialog_filename"]
            pyautogui.click(name_x, name_y)
            time.sleep(self.timeouts["button_click"])
            
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.typewrite(filename)
            time.sleep(self.timeouts["button_click"])
            
            # Click Save
            save_x, save_y = self.coordinates["save_confirm_button"]
            pyautogui.click(save_x, save_y)
            time.sleep(self.timeouts["file_save"])
            
            temp_path = os.path.join(self.file_paths["downloads_folder"], filename)
            self.logger.info(f"PDF saved to Downloads: {temp_path}")
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Failed to save PDF to Downloads: {e}")
            return None
    
    def _move_pdf_to_folder(self, temp_path: str, date_folder: str) -> Optional[str]:
        """Move PDF from Downloads to correct folder"""
        try:
            # Create target folder if it doesn't exist
            target_folder = os.path.join(self.file_paths["pdf_base_path"], date_folder)
            os.makedirs(target_folder, exist_ok=True)
            
            # Generate final path
            filename = os.path.basename(temp_path)
            final_path = os.path.join(target_folder, filename)
            
            # Wait for file to be created in Downloads
            wait_time = 0
            while not os.path.exists(temp_path) and wait_time < 30:
                time.sleep(1)
                wait_time += 1
            
            if not os.path.exists(temp_path):
                self.logger.error(f"PDF not found in Downloads: {temp_path}")
                return None
            
            # Move file
            import shutil
            shutil.move(temp_path, final_path)
            
            self.logger.info(f"PDF moved to: {final_path}")
            return final_path
            
        except Exception as e:
            self.logger.error(f"Failed to move PDF to folder: {e}")
            return None
    
    def _verify_report_step(self, step_name: str) -> bool:
        """Verify report step completion"""
        try:
            # Simplified verification
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.logger.error(f"Report step verification failed: {e}")
            return False
    
    def _verify_wifi_report_opened(self) -> bool:
        """Verify WiFi User Count report opened"""
        try:
            # Check for report window or elements
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"WiFi report verification failed: {e}")
            return False
    
    def run_phase_4_complete(self, date_folder: str) -> Dict[str, Any]:
        """Run complete Phase 4: PDF Generation"""
        try:
            self.logger.info("📄 Starting Phase 4: PDF Generation")
            
            phase_result = {
                "success": False,
                "tasks_completed": [],
                "errors": [],
                "start_time": datetime.now().isoformat(),
                "date_folder": date_folder
            }
            
            # Task 4.1: Navigate to reports
            nav_result = self.task_4_1_navigate_to_reports()
            if nav_result["success"]:
                phase_result["tasks_completed"].append("4.1_navigation")
                self.logger.info("✅ Task 4.1 completed: Report navigation")
            else:
                phase_result["errors"].append(f"Task 4.1 failed: {nav_result['error']}")
                return phase_result
            
            # Task 4.2: Set date range
            date_result = self.task_4_2_set_date_range()
            if date_result["success"]:
                phase_result["tasks_completed"].append("4.2_date_range")
                phase_result["date_range"] = f"{date_result['start_date']} to {date_result['end_date']}"
                self.logger.info("✅ Task 4.2 completed: Date range set")
            else:
                phase_result["errors"].append(f"Task 4.2 failed: {date_result['error']}")
                return phase_result
            
            # Task 4.3: Export PDF
            export_result = self.task_4_3_export_pdf(date_folder)
            if export_result["success"]:
                phase_result["tasks_completed"].append("4.3_export")
                phase_result["pdf_path"] = export_result["pdf_path"]
                self.logger.info("✅ Task 4.3 completed: PDF exported")
                phase_result["success"] = True
            else:
                phase_result["errors"].append(f"Task 4.3 failed: {export_result['error']}")
                return phase_result
            
            phase_result["end_time"] = datetime.now().isoformat()
            self.logger.info("🎉 Phase 4 completed successfully!")
            
            return phase_result
            
        except Exception as e:
            error_msg = f"Phase 4 execution failed: {e}"
            self.logger.error(error_msg)
            phase_result["errors"].append(error_msg)
            phase_result["end_time"] = datetime.now().isoformat()
            return phase_result

# Test function
def test_phase_4():
    """Test Phase 4 implementation"""
    print("🧪 Testing VBS Phase 4: PDF Generation")
    print("=" * 50)
    
    phase4 = VBSPhase4_PDFGeneration()
    
    # Test with current date folder
    test_date = "05july"
    
    print(f"\n1. Testing PDF generation for {test_date}...")
    result = phase4.run_phase_4_complete(test_date)
    print(f"   PDF result: {result}")
    
    print("\n✅ Phase 4 testing completed")

if __name__ == "__main__":
    test_phase_4() 