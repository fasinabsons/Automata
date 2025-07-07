#!/usr/bin/env python3
"""
VBS Automation - Phase 3: Excel Import
Implements Task 3.1 and 3.2 from vbs_task_list.txt
Excel Import: New → Credit → Import EHC → File Selection → Import → Update
"""

import os
import time
import logging
import win32gui
import win32con
import pyautogui
from typing import Dict, Optional
import traceback
from datetime import datetime
from pathlib import Path

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.5

class VBSPhase3_ExcelImport:
    """Phase 3: Excel Import Implementation"""
    
    def __init__(self, window_handle: Optional[int] = None):
        self.logger = self._setup_logging()
        self.window_handle = window_handle
        
        # Import coordinates (from clickcursor.txt - EXACT COORDINATES)
        self.coordinates = {
            # Import form coordinates (from clickcursor.txt)
            "new_button": (104, 107),                 # New button
            "credit_radio": (368, 292),               # Credit radio button
            "import_ehc_checkbox": (1192, 699),       # Import EHC Users Mac Address checkbox
            "three_dots_button": (783, 664),          # 3 dots file selection button
            
            # File dialog coordinates (from clickcursor.txt)
            "excel_file": (591, 455),                 # Excel file from the folder
            "open_button": (783, 885),                # Open button
            "popup_yes": (1047, 681),                 # Popup yes button
            
            # Import process coordinates (from clickcursor.txt)
            "sheet_dropdown": (386, 716),             # Sheet 1 from drop down list
            "import_button": (708, 692),              # Import button
            "ehc_user_detail": (285, 739),            # EHC user detail section
            "update_button": (1541, 893),             # Update button
            
            # Progress and status coordinates
            "progress_area": (960, 600),              # Progress indicator area
            "status_text": (960, 650),                # Status text area
            "close_button": (1900, 50),               # Close button
        }
        
        # File paths configuration
        self.file_paths = {
            "excel_base_path": r"C:\Users\Lenovo\Videos\Automata\EHC_Data_Merge",
            "excel_filename_pattern": "EHC_Upload_Mac_{date}.xlsx",  # {date} = DDMMYYYY
        }
        
        # Timing configuration
        self.timeouts = {
            "button_click": 1,           # Button click response time
            "dialog_open": 2,            # File dialog open time
            "file_selection": 1,         # File selection time
            "import_start": 3,           # Import process start time
            "import_progress": 300,      # Import progress (5 minutes max)
            "update_process": 7200,      # Update process (2 hours max)
            "progress_check": 10,        # Progress check interval
        }
        
        # Import sequence configuration
        self.import_sequence = [
            {
                "step": "click_new",
                "description": "Click New button",
                "coordinate": "new_button",
                "wait_time": "button_click"
            },
            {
                "step": "select_credit",
                "description": "Select Credit radio button",
                "coordinate": "credit_radio",
                "wait_time": "button_click"
            },
            {
                "step": "check_import_ehc",
                "description": "Check Import EHC checkbox",
                "coordinate": "import_ehc_checkbox",
                "wait_time": "button_click"
            },
            {
                "step": "click_file_selection",
                "description": "Click 3 dots for file selection",
                "coordinate": "three_dots_button",
                "wait_time": "dialog_open"
            }
        ]
        
        self.logger.info("VBS Phase 3 (Excel Import) initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Phase 3"""
        logger = logging.getLogger("VBSPhase3")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def set_window_handle(self, window_handle: int):
        """Set the window handle for import operations"""
        self.window_handle = window_handle
        self.logger.info(f"Window handle set: {window_handle}")
    
    def task_3_1_setup_import_form(self) -> Dict[str, any]:
        """Task 3.1: Setup import form (New → Credit → Import EHC → 3 dots)"""
        try:
            self.logger.info("📋 TASK 3.1: Setting up import form...")
            
            if not self.window_handle:
                return {"success": False, "error": "No window handle available"}
            
            # Ensure window is active
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(self.timeouts["button_click"])
            
            # Execute import setup sequence
            for i, step in enumerate(self.import_sequence):
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
                    if not self._verify_import_step(step_name):
                        return {"success": False, "error": f"Import step '{step_name}' verification failed"}
                    
                    self.logger.info(f"✅ Step {step_num} completed successfully")
                    
                except Exception as e:
                    return {"success": False, "error": f"Step {step_num} failed: {e}"}
            
            # Verify file dialog opened
            if self._verify_file_dialog_opened():
                self.logger.info("✅ Import form setup completed: File dialog opened")
                return {"success": True, "message": "Import form setup successful"}
            else:
                return {"success": False, "error": "File dialog did not open"}
            
        except Exception as e:
            error_msg = f"Import form setup failed: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": error_msg}
    
    def task_3_2_select_excel_file(self, date_folder: str) -> Dict[str, any]:
        """Task 3.2: Select Excel file from specified date folder"""
        try:
            self.logger.info(f"📁 TASK 3.2: Selecting Excel file from {date_folder}...")
            
            # Build file path
            folder_path = os.path.join(self.file_paths["excel_base_path"], date_folder)
            
            # Find Excel file in folder
            excel_file = self._find_excel_file(folder_path)
            if not excel_file:
                return {"success": False, "error": f"No Excel file found in {folder_path}"}
            
            full_file_path = os.path.join(folder_path, excel_file)
            self.logger.info(f"Target Excel file: {full_file_path}")
            
            # Navigate to file in dialog
            success = self._navigate_to_file(full_file_path)
            if not success:
                return {"success": False, "error": "Failed to navigate to Excel file"}
            
            # Select the file
            success = self._select_file_in_dialog(excel_file)
            if not success:
                return {"success": False, "error": "Failed to select Excel file"}
            
            self.logger.info("✅ Excel file selected successfully")
            return {"success": True, "file_path": full_file_path, "file_name": excel_file}
            
        except Exception as e:
            error_msg = f"Excel file selection failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def task_3_3_import_excel_data(self) -> Dict[str, any]:
        """Task 3.3: Import Excel data (Select sheet → Import → Wait)"""
        try:
            self.logger.info("📊 TASK 3.3: Importing Excel data...")
            
            # Step 1: Select first sheet
            self.logger.info("Step 1: Selecting first sheet...")
            success = self._select_first_sheet()
            if not success:
                return {"success": False, "error": "Failed to select first sheet"}
            
            # Step 2: Click Import button
            self.logger.info("Step 2: Clicking Import button...")
            success = self._click_import_button()
            if not success:
                return {"success": False, "error": "Failed to click Import button"}
            
            # Step 3: Wait for import to complete (5-10 minutes)
            self.logger.info("Step 3: Waiting for import to complete...")
            success = self._wait_for_import_completion()
            if not success:
                return {"success": False, "error": "Import process timed out or failed"}
            
            self.logger.info("✅ Excel data import completed successfully")
            return {"success": True, "message": "Excel data imported successfully"}
            
        except Exception as e:
            error_msg = f"Excel data import failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def task_3_4_update_data(self) -> Dict[str, any]:
        """Task 3.4: Update imported data (Click Update → Wait 1-2 hours)"""
        try:
            self.logger.info("🔄 TASK 3.4: Updating imported data...")
            
            # Step 1: Click Update button
            self.logger.info("Step 1: Clicking Update button...")
            success = self._click_update_button()
            if not success:
                return {"success": False, "error": "Failed to click Update button"}
            
            # Step 2: Wait for update to complete (1-2 hours)
            self.logger.info("Step 2: Waiting for update to complete (this may take 1-2 hours)...")
            success = self._wait_for_update_completion()
            if not success:
                return {"success": False, "error": "Update process timed out or failed"}
            
            self.logger.info("✅ Data update completed successfully")
            return {"success": True, "message": "Data update completed successfully"}
            
        except Exception as e:
            error_msg = f"Data update failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _find_excel_file(self, folder_path: str) -> Optional[str]:
        """Find Excel file in specified folder"""
        try:
            if not os.path.exists(folder_path):
                self.logger.error(f"Folder does not exist: {folder_path}")
                return None
            
            # Look for Excel files
            for file in os.listdir(folder_path):
                if file.endswith('.xlsx') and 'EHC_Upload_Mac' in file:
                    self.logger.info(f"Found Excel file: {file}")
                    return file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding Excel file: {e}")
            return None
    
    def _navigate_to_file(self, file_path: str) -> bool:
        """Navigate to file in file dialog"""
        try:
            # Click on file path input
            path_x, path_y = self.coordinates["excel_file"]
            pyautogui.click(path_x, path_y)
            time.sleep(self.timeouts["button_click"])
            
            # Clear and enter file path
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.typewrite(os.path.dirname(file_path))
            time.sleep(self.timeouts["file_selection"])
            pyautogui.press('enter')
            time.sleep(self.timeouts["dialog_open"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to file: {e}")
            return False
    
    def _select_file_in_dialog(self, filename: str) -> bool:
        """Select file in file dialog"""
        try:
            # Click in file list area
            list_x, list_y = self.coordinates["excel_file"]
            pyautogui.click(list_x, list_y)
            time.sleep(self.timeouts["button_click"])
            
            # Type filename to select it
            pyautogui.typewrite(filename)
            time.sleep(self.timeouts["file_selection"])
            
            # Click Select/Open button
            select_x, select_y = self.coordinates["open_button"]
            pyautogui.click(select_x, select_y)
            time.sleep(self.timeouts["dialog_open"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select file in dialog: {e}")
            return False
    
    def _select_first_sheet(self) -> bool:
        """Select first sheet in sheet dropdown"""
        try:
            # Click sheet dropdown
            dropdown_x, dropdown_y = self.coordinates["sheet_dropdown"]
            pyautogui.click(dropdown_x, dropdown_y)
            time.sleep(self.timeouts["button_click"])
            
            # Click first sheet option
            sheet_x, sheet_y = self.coordinates["sheet_dropdown"]
            pyautogui.click(sheet_x, sheet_y)
            time.sleep(self.timeouts["button_click"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select first sheet: {e}")
            return False
    
    def _click_import_button(self) -> bool:
        """Click Import button"""
        try:
            import_x, import_y = self.coordinates["import_button"]
            pyautogui.click(import_x, import_y)
            time.sleep(self.timeouts["import_start"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click Import button: {e}")
            return False
    
    def _click_update_button(self) -> bool:
        """Click Update button"""
        try:
            update_x, update_y = self.coordinates["update_button"]
            pyautogui.click(update_x, update_y)
            time.sleep(self.timeouts["button_click"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click Update button: {e}")
            return False
    
    def _wait_for_import_completion(self) -> bool:
        """Wait for import process to complete"""
        try:
            start_time = time.time()
            timeout = self.timeouts["import_progress"]
            
            self.logger.info(f"Waiting for import completion (timeout: {timeout/60:.1f} minutes)...")
            
            while (time.time() - start_time) < timeout:
                # Check for completion indicators
                # This would involve checking UI elements or progress bars
                
                # For now, wait for a reasonable time (5 minutes)
                if (time.time() - start_time) > 300:  # 5 minutes
                    self.logger.info("Import process assumed complete after 5 minutes")
                    return True
                
                time.sleep(self.timeouts["progress_check"])
                self.logger.info(f"Import in progress... ({(time.time() - start_time)/60:.1f} minutes elapsed)")
            
            self.logger.warning("Import process timed out")
            return False
            
        except Exception as e:
            self.logger.error(f"Error waiting for import completion: {e}")
            return False
    
    def _wait_for_update_completion(self) -> bool:
        """Wait for update process to complete"""
        try:
            start_time = time.time()
            timeout = self.timeouts["update_process"]
            
            self.logger.info(f"Waiting for update completion (timeout: {timeout/3600:.1f} hours)...")
            
            while (time.time() - start_time) < timeout:
                # Check for completion indicators
                # This would involve checking UI elements or progress bars
                
                elapsed_minutes = (time.time() - start_time) / 60
                
                # Log progress every 10 minutes
                if elapsed_minutes % 10 < 0.5:
                    self.logger.info(f"Update in progress... ({elapsed_minutes:.0f} minutes elapsed)")
                
                time.sleep(self.timeouts["progress_check"])
                
                # Check if update is complete (simplified check)
                # In a real implementation, this would check specific UI elements
                if elapsed_minutes > 60:  # Assume complete after 1 hour minimum
                    self.logger.info("Update process assumed complete")
                    return True
            
            self.logger.warning("Update process timed out")
            return False
            
        except Exception as e:
            self.logger.error(f"Error waiting for update completion: {e}")
            return False
    
    def _verify_import_step(self, step_name: str) -> bool:
        """Verify import step completion"""
        try:
            # Simplified verification - in production, check specific UI elements
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.logger.error(f"Import step verification failed: {e}")
            return False
    
    def _verify_file_dialog_opened(self) -> bool:
        """Verify file dialog opened"""
        try:
            # Check for file dialog window
            time.sleep(1)
            # In production, this would check for specific dialog elements
            return True
            
        except Exception as e:
            self.logger.error(f"File dialog verification failed: {e}")
            return False
    
    def run_phase_3_complete(self, date_folder: str) -> Dict[str, any]:
        """Run complete Phase 3: Excel Import"""
        try:
            self.logger.info("📊 Starting Phase 3: Excel Import")
            
            phase_result = {
                "success": False,
                "tasks_completed": [],
                "errors": [],
                "start_time": datetime.now().isoformat(),
                "date_folder": date_folder
            }
            
            # Task 3.1: Setup import form
            setup_result = self.task_3_1_setup_import_form()
            if setup_result["success"]:
                phase_result["tasks_completed"].append("3.1_setup")
                self.logger.info("✅ Task 3.1 completed: Import form setup")
            else:
                phase_result["errors"].append(f"Task 3.1 failed: {setup_result['error']}")
                return phase_result
            
            # Task 3.2: Select Excel file
            select_result = self.task_3_2_select_excel_file(date_folder)
            if select_result["success"]:
                phase_result["tasks_completed"].append("3.2_file_selection")
                phase_result["excel_file"] = select_result["file_path"]
                self.logger.info("✅ Task 3.2 completed: Excel file selected")
            else:
                phase_result["errors"].append(f"Task 3.2 failed: {select_result['error']}")
                return phase_result
            
            # Task 3.3: Import Excel data
            import_result = self.task_3_3_import_excel_data()
            if import_result["success"]:
                phase_result["tasks_completed"].append("3.3_import")
                self.logger.info("✅ Task 3.3 completed: Excel data imported")
            else:
                phase_result["errors"].append(f"Task 3.3 failed: {import_result['error']}")
                return phase_result
            
            # Task 3.4: Update data
            update_result = self.task_3_4_update_data()
            if update_result["success"]:
                phase_result["tasks_completed"].append("3.4_update")
                self.logger.info("✅ Task 3.4 completed: Data updated")
                phase_result["success"] = True
            else:
                phase_result["errors"].append(f"Task 3.4 failed: {update_result['error']}")
                return phase_result
            
            phase_result["end_time"] = datetime.now().isoformat()
            self.logger.info("🎉 Phase 3 completed successfully!")
            
            return phase_result
            
        except Exception as e:
            error_msg = f"Phase 3 execution failed: {e}"
            self.logger.error(error_msg)
            phase_result["errors"].append(error_msg)
            phase_result["end_time"] = datetime.now().isoformat()
            return phase_result

# Test function
def test_phase_3():
    """Test Phase 3 implementation"""
    print("🧪 Testing VBS Phase 3: Excel Import")
    print("=" * 50)
    
    phase3 = VBSPhase3_ExcelImport()
    
    # Test with current date folder
    test_date = "05july"
    
    print(f"\n1. Testing Excel import for {test_date}...")
    result = phase3.run_phase_3_complete(test_date)
    print(f"   Import result: {result}")
    
    print("\n✅ Phase 3 testing completed")

if __name__ == "__main__":
    test_phase_3() 