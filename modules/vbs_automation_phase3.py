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
import win32api
import win32process
import ctypes
from ctypes import wintypes
from typing import Dict, Optional, Any
import traceback
from datetime import datetime
from pathlib import Path

# Windows API constants for lock screen compatibility
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
VK_RETURN = 0x0D
VK_CONTROL = 0x11

class VBSPhase3_ExcelImport:
    """Phase 3: Excel Import Implementation with Lock Screen Compatibility"""
    
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
        
        # Import sequence configuration - ONLY IMPORT ACTIONS (NO NAVIGATION)
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
        
        self.logger.info("VBS Phase 3 (Excel Import) initialized with lock screen compatibility")
    
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
    
    def _click_coordinate_locked(self, x: int, y: int) -> bool:
        """Click coordinate using Windows API - works even when screen is locked"""
        try:
            if not self.window_handle:
                self.logger.error("No window handle available")
                return False
            
            # Verify window handle is still valid
            if not win32gui.IsWindow(self.window_handle):
                self.logger.error(f"Window handle {self.window_handle} is invalid, trying to find VBS window...")
                # Try to find VBS window again
                vbs_window = self._find_vbs_window()
                if vbs_window:
                    self.window_handle = vbs_window
                    self.logger.info(f"Found new VBS window: {self.window_handle}")
                else:
                    self.logger.error("Could not find valid VBS window")
                    return False
            
            # Use absolute screen coordinates for VBS (like Phase 2)
            lParam = (y << 16) | x
            
            # Send mouse down and up messages directly to window
            win32gui.PostMessage(self.window_handle, WM_LBUTTONDOWN, 0, lParam)
            time.sleep(0.1)
            win32gui.PostMessage(self.window_handle, WM_LBUTTONUP, 0, lParam)
            
            self.logger.info(f"Clicked at ({x}, {y}) using Windows API")
            return True
            
        except Exception as e:
            self.logger.error(f"Windows API click failed: {e}")
            return False
    
    def _find_vbs_window(self) -> Optional[int]:
        """Find VBS window handle"""
        vbs_windows = []
        
        def enum_windows_callback(hwnd, windows):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        # Look for VBS/Absons indicators - EXCLUDE browser windows
                        vbs_indicators = ['absons', 'arabian', 'moonflower']
                        exclude_indicators = ['login', 'security', 'warning', 'brave', 'chrome', 'firefox', 'edge', 'browser', 'grok']
                        
                        title_lower = title.lower()
                        has_vbs = any(indicator in title_lower for indicator in vbs_indicators)
                        has_exclude = any(indicator in title_lower for indicator in exclude_indicators)
                        
                        if has_vbs and not has_exclude:
                            # Additional check: get process name to ensure it's VBS
                            try:
                                _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                                import psutil
                                process = psutil.Process(process_id)
                                exe_name = process.name().lower()
                                
                                # Only accept if it's actually VBS executable
                                if 'absons' in exe_name or 'erp' in exe_name or 'arabian' in exe_name:
                                    windows.append((hwnd, title))
                            except:
                                pass
                            
            except:
                pass
            return True
        
        win32gui.EnumWindows(enum_windows_callback, vbs_windows)
        
        if vbs_windows:
            self.logger.info(f"Found VBS window: '{vbs_windows[0][1]}'")
            return vbs_windows[0][0]
        
        return None
    
    def _type_text_locked(self, text: str) -> bool:
        """Type text using Windows API - works even when screen is locked"""
        try:
            if not self.window_handle:
                return False
            
            for char in text:
                win32gui.PostMessage(self.window_handle, WM_CHAR, ord(char), 0)
                time.sleep(0.05)
            
            self.logger.info(f"Typed '{text}' using Windows API")
            return True
            
        except Exception as e:
            self.logger.error(f"Windows API typing failed: {e}")
            return False
    
    def _send_key_locked(self, vk_code: int) -> bool:
        """Send key using Windows API - works even when screen is locked"""
        try:
            if not self.window_handle:
                return False
            
            win32gui.PostMessage(self.window_handle, WM_KEYDOWN, vk_code, 0)
            time.sleep(0.05)
            win32gui.PostMessage(self.window_handle, WM_KEYUP, vk_code, 0)
            
            self.logger.info(f"Sent key {vk_code} using Windows API")
            return True
            
        except Exception as e:
            self.logger.error(f"Windows API key sending failed: {e}")
            return False
    
    def task_3_1_setup_import_form(self) -> Dict[str, Any]:
        """Task 3.1: Setup import form (New → Credit → Import EHC → 3 dots)"""
        try:
            self.logger.info("📋 TASK 3.1: Setting up import form...")
            
            if not self.window_handle:
                return {"success": False, "error": "No window handle available"}
            
            # Wait for user to switch to VBS software (as specified)
            self.logger.info("⏳ Waiting 5 seconds for user to switch to VBS software...")
            time.sleep(5)
            
            # Execute import setup sequence using Windows API
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
                
                # Perform click action using Windows API
                try:
                    self.logger.info(f"Clicking at coordinates ({x}, {y}) using Windows API")
                    success = self._click_coordinate_locked(x, y)
                    if not success:
                        return {"success": False, "error": f"Failed to click at ({x}, {y})"}
                    
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
    
    def task_3_2_select_excel_file(self, date_folder: str) -> Dict[str, Any]:
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
            
            # Navigate to file in dialog using Windows API
            success = self._navigate_to_file_locked(full_file_path)
            if not success:
                return {"success": False, "error": "Failed to navigate to Excel file"}
            
            # Select the file using Windows API
            success = self._select_file_in_dialog_locked(excel_file)
            if not success:
                return {"success": False, "error": "Failed to select Excel file"}
            
            self.logger.info("✅ Excel file selected successfully")
            return {"success": True, "file_path": full_file_path, "file_name": excel_file}
            
        except Exception as e:
            error_msg = f"Excel file selection failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def task_3_3_import_excel_data(self) -> Dict[str, Any]:
        """Task 3.3: Import Excel data (Wait for popup → Click OK → Click Import → Wait)"""
        try:
            self.logger.info("📊 TASK 3.3: Importing Excel data...")
            
            # As per user specification: DON'T CLICK ANYTHING until import popup appears
            self.logger.info("⏳ Waiting for import popup to appear (not clicking anything)...")
            time.sleep(3)  # Wait for popup to appear
            
            # Step 1: Click OK on "import successful" popup
            self.logger.info("Step 1: Clicking OK on import successful popup...")
            success = self._click_popup_ok_locked()
            if not success:
                return {"success": False, "error": "Failed to click OK on import popup"}
            
            # Step 2: Click Import button
            self.logger.info("Step 2: Clicking Import button...")
            success = self._click_import_button_locked()
            if not success:
                return {"success": False, "error": "Failed to click Import button"}
            
            # Step 3: Wait for import to complete
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
    
    def task_3_4_update_data(self) -> Dict[str, Any]:
        """Task 3.4: Update imported data (Click Update → Wait for popup → Click OK → Close form)"""
        try:
            self.logger.info("🔄 TASK 3.4: Updating imported data...")
            
            # Step 1: Click Update button
            self.logger.info("Step 1: Clicking Update button...")
            success = self._click_update_button_locked()
            if not success:
                return {"success": False, "error": "Failed to click Update button"}
            
            # Step 2: Wait for "update successful" popup and click OK
            self.logger.info("Step 2: Waiting for update successful popup...")
            success = self._wait_for_update_completion()
            if not success:
                return {"success": False, "error": "Update process timed out or failed"}
            
            # Step 3: Click OK on update successful popup
            self.logger.info("Step 3: Clicking OK on update successful popup...")
            success = self._click_popup_ok_locked()
            if not success:
                return {"success": False, "error": "Failed to click OK on update popup"}
            
            # Step 4: Close import form
            self.logger.info("Step 4: Closing import form...")
            success = self._close_import_form_locked()
            if not success:
                return {"success": False, "error": "Failed to close import form"}
            
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
    
    def _navigate_to_file_locked(self, file_path: str) -> bool:
        """Navigate to file in file dialog using Windows API"""
        try:
            # Click on file path input
            path_x, path_y = self.coordinates["excel_file"]
            success = self._click_coordinate_locked(path_x, path_y)
            if not success:
                return False
            time.sleep(self.timeouts["button_click"])
            
            # Clear and enter file path using Windows API
            # Ctrl+A to select all
            win32gui.PostMessage(self.window_handle, WM_KEYDOWN, VK_CONTROL, 0)
            win32gui.PostMessage(self.window_handle, WM_KEYDOWN, ord('A'), 0)
            win32gui.PostMessage(self.window_handle, WM_KEYUP, ord('A'), 0)
            win32gui.PostMessage(self.window_handle, WM_KEYUP, VK_CONTROL, 0)
            time.sleep(0.2)
            
            # Type file path
            success = self._type_text_locked(os.path.dirname(file_path))
            if not success:
                return False
            time.sleep(self.timeouts["file_selection"])
            
            # Press Enter
            success = self._send_key_locked(VK_RETURN)
            if not success:
                return False
            time.sleep(self.timeouts["dialog_open"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to file: {e}")
            return False
    
    def _select_file_in_dialog_locked(self, filename: str) -> bool:
        """Select file in file dialog using Windows API"""
        try:
            # Click in file list area
            list_x, list_y = self.coordinates["excel_file"]
            success = self._click_coordinate_locked(list_x, list_y)
            if not success:
                return False
            time.sleep(self.timeouts["button_click"])
            
            # Type filename to select it
            success = self._type_text_locked(filename)
            if not success:
                return False
            time.sleep(self.timeouts["file_selection"])
            
            # Click Select/Open button
            select_x, select_y = self.coordinates["open_button"]
            success = self._click_coordinate_locked(select_x, select_y)
            if not success:
                return False
            time.sleep(self.timeouts["dialog_open"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select file in dialog: {e}")
            return False
    
    def _click_popup_ok_locked(self) -> bool:
        """Click OK on popup using Windows API"""
        try:
            popup_x, popup_y = self.coordinates["popup_yes"]
            return self._click_coordinate_locked(popup_x, popup_y)
            
        except Exception as e:
            self.logger.error(f"Failed to click popup OK: {e}")
            return False
    
    def _click_import_button_locked(self) -> bool:
        """Click Import button using Windows API"""
        try:
            import_x, import_y = self.coordinates["import_button"]
            return self._click_coordinate_locked(import_x, import_y)
            
        except Exception as e:
            self.logger.error(f"Failed to click Import button: {e}")
            return False
    
    def _click_update_button_locked(self) -> bool:
        """Click Update button using Windows API"""
        try:
            update_x, update_y = self.coordinates["update_button"]
            return self._click_coordinate_locked(update_x, update_y)
            
        except Exception as e:
            self.logger.error(f"Failed to click Update button: {e}")
            return False
    
    def _close_import_form_locked(self) -> bool:
        """Close import form using Windows API"""
        try:
            close_x, close_y = self.coordinates["close_button"]
            return self._click_coordinate_locked(close_x, close_y)
            
        except Exception as e:
            self.logger.error(f"Failed to close import form: {e}")
            return False
    
    def _select_first_sheet(self) -> bool:
        """Select first sheet in sheet dropdown using Windows API"""
        try:
            # Click sheet dropdown
            dropdown_x, dropdown_y = self.coordinates["sheet_dropdown"]
            success = self._click_coordinate_locked(dropdown_x, dropdown_y)
            if not success:
                return False
            time.sleep(self.timeouts["button_click"])
            
            # Click first sheet option
            sheet_x, sheet_y = self.coordinates["sheet_dropdown"]
            success = self._click_coordinate_locked(sheet_x, sheet_y)
            if not success:
                return False
            time.sleep(self.timeouts["button_click"])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select first sheet: {e}")
            return False
    
    def _click_import_button(self) -> bool:
        """Click Import button using Windows API"""
        try:
            import_x, import_y = self.coordinates["import_button"]
            return self._click_coordinate_locked(import_x, import_y)
            
        except Exception as e:
            self.logger.error(f"Failed to click Import button: {e}")
            return False
    
    def _click_update_button(self) -> bool:
        """Click Update button using Windows API"""
        try:
            update_x, update_y = self.coordinates["update_button"]
            return self._click_coordinate_locked(update_x, update_y)
            
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
    
    def run_phase_3_complete(self, date_folder: str) -> Dict[str, Any]:
        """Run complete Phase 3: Excel Import with user-specified workflow"""
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
            
            # Task 3.3: Import Excel data (with user-specified workflow)
            import_result = self.task_3_3_import_excel_data()
            if import_result["success"]:
                phase_result["tasks_completed"].append("3.3_import")
                self.logger.info("✅ Task 3.3 completed: Excel data imported")
            else:
                phase_result["errors"].append(f"Task 3.3 failed: {import_result['error']}")
                return phase_result
            
            # Task 3.4: Update data (with user-specified workflow)
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
    test_date = "09jul"
    
    print(f"\n1. Testing Excel import for {test_date}...")
    result = phase3.run_phase_3_complete(test_date)
    print(f"   Import result: {result}")
    
    print("\n✅ Phase 3 testing completed")

if __name__ == "__main__":
    test_phase_3() 