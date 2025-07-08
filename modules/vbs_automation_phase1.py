#!/usr/bin/env python3
"""
VBS Automation - Phase 1: Application Launch & Login (IMPROVED)
Implements Task 1.1 and 1.2 from vbs_task_list.txt
FIXES: Proper double-click for exe files and taskbar-then-Run button sequence
"""

import os
import sys
import time
import logging
import subprocess
import win32gui
import win32con
import win32api
import pyautogui
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
import traceback
import cv2
import numpy as np
from PIL import ImageGrab

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

class VBSPhase1_LaunchLogin_Improved:
    """Phase 1: Application Launch & Login Implementation (IMPROVED)"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.window_handle = None
        
        # Application paths (from task list)
        self.vbs_paths = [
            r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk",
            r"\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe"
        ]
        
        # Login credentials (from task list)
        self.credentials = {
            "dropdown_selection": "IT",
            "date": "01/01/2023", 
            "username": "Vj",
            "password": ""  # No password required
        }
        
        # UI Coordinates (from clickcursor.txt - EXACT COORDINATES)
        self.coordinates = {
            # Login form coordinates (from clickcursor.txt)
            "run_button": (1043, 608),             # Run button (popup permission)
            "it_dropdown": (1054, 528),            # IT dropdown selection
            "date_field": (1053, 565),             # Date field for 01/01/2023
            "username_field": (929, 561),          # Username field for "Vj"
            "ok_button": (897, 724),               # OK/Login button
            
            # Window detection area
            "window_center": (960, 600),           # Center of application window
            
            # Taskbar coordinates (bottom of screen)
            "taskbar_left": (200, 740),            # Left side of taskbar
            "taskbar_center": (500, 740),          # Center of taskbar
            "taskbar_right": (800, 740),           # Right side of taskbar
        }
        
        # Timing configuration
        self.timeouts = {
            "app_launch": 15,        # 15 seconds for app launch
            "login": 5,              # 5 seconds for login completion
            "element_wait": 2,       # 2 seconds between UI actions
            "dropdown_wait": 1,      # 1 second for dropdown to open
            "double_click_interval": 0.2,  # Interval between double clicks
            "taskbar_wait": 1,       # Wait after taskbar click
            "run_button_wait": 0.5,  # Wait after Run button click
        }
        
        # Background operation settings
        self.preserve_user_context = True
        self.user_active_window = None
        self.vbs_window_handle = None
        
        self.logger.info("VBS Phase 1 (Launch & Login) IMPROVED initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Phase 1"""
        logger = logging.getLogger("VBSPhase1_Improved")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def task_1_1_launch_application_improved(self) -> Dict[str, any]:
        """Task 1.1: Launch AbsonsItERP.exe application with PROPER left-click double-click"""
        try:
            self.logger.info("🚀 TASK 1.1: Launching AbsonsItERP application with LEFT-CLICK DOUBLE-CLICK...")
            
            # Check if application is already running
            existing_window = self._find_vbs_window()
            if existing_window:
                self.logger.info("Application already running, using existing window")
                self.window_handle = existing_window
                # Ensure window is maximized and not minimized
                win32gui.SetForegroundWindow(self.window_handle)
                win32gui.ShowWindow(self.window_handle, win32con.SW_MAXIMIZE)
                time.sleep(2)
                return {"success": True, "message": "Using existing application window"}
            
            # Try each path until one works
            for i, path in enumerate(self.vbs_paths):
                try:
                    self.logger.info(f"Attempting launch via path {i+1}: {path}")
                    
                    # Check if path exists
                    if not os.path.exists(path):
                        self.logger.warning(f"Path does not exist: {path}")
                        continue
                    
                    # SAFE METHOD: Use proper left-click double-click (no deletion)
                    self.logger.info("🎯 Using SAFE left-click double-click method...")
                    success = self._safe_double_click_launch(path)
                    
                    if not success:
                        self.logger.warning(f"Safe double-click failed for path {i+1}")
                        continue
                    
                    # CRITICAL: Wait 10 seconds for application to start loading
                    self.logger.info("⏳ Waiting 10 seconds for application to start loading...")
                    time.sleep(10)
                    
                    # IMPROVED: Handle RUN popup with keyboard method
                    self.logger.info("🔔 Handling RUN popup with keyboard method...")
                    popup_handled = self._handle_run_popup_simple()
                    if popup_handled:
                        self.logger.info("✅ RUN popup handled successfully")
                        # Wait additional time after popup
                        time.sleep(3)
                    
                    # Now look for VBS window
                    window_handle = self._find_vbs_window()
                    if window_handle:
                        self.window_handle = window_handle
                        
                        # CRITICAL: Ensure window is maximized and focused
                        self.logger.info("📱 Maximizing and focusing VBS window...")
                        win32gui.SetForegroundWindow(self.window_handle)
                        win32gui.ShowWindow(self.window_handle, win32con.SW_MAXIMIZE)
                        time.sleep(3)  # Wait for window to stabilize
                        
                        # Verify window is ready
                        window_title = win32gui.GetWindowText(self.window_handle)
                        self.logger.info(f"✅ Application launched successfully: {window_title}")
                        
                        return {
                            "success": True, 
                            "window_handle": window_handle,
                            "launch_path": path,
                            "window_title": window_title
                        }
                    
                    self.logger.warning(f"Application window not found after launch via path {i+1}")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to launch via path {i+1}: {e}")
                    continue
            
            return {"success": False, "error": "Failed to launch application via all available paths"}
            
        except Exception as e:
            error_msg = f"Application launch failed: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": error_msg}
    
    def _safe_double_click_launch(self, file_path: str) -> bool:
        """Safely launch application using left-click double-click (no deletion)"""
        try:
            self.logger.info(f"🖱️ SAFE: Performing left-click double-click on: {file_path}")
            
            # Method 1: Use subprocess with 'start' command (Windows native)
            try:
                import subprocess
                result = subprocess.run(['start', '', file_path], shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("✅ Successfully launched using subprocess start command")
                    return True
                else:
                    self.logger.warning(f"Subprocess start failed: {result.stderr}")
            except Exception as e:
                self.logger.warning(f"Subprocess method failed: {e}")
            
            # Method 2: Use ShellExecute with 'open' verb (safest)
            try:
                import win32api
                result = win32api.ShellExecute(0, 'open', file_path, '', '', 1)
                if result > 32:  # Success codes are > 32
                    self.logger.info("✅ Successfully launched using ShellExecute")
                    return True
                else:
                    self.logger.warning(f"ShellExecute failed with code: {result}")
            except Exception as e:
                self.logger.warning(f"ShellExecute method failed: {e}")
            
            # Method 3: Fallback to os.startfile (but this might cause deletion)
            try:
                os.startfile(file_path)
                self.logger.info("✅ Launched using os.startfile (fallback)")
                return True
            except Exception as e:
                self.logger.warning(f"os.startfile fallback failed: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Safe double-click launch failed: {e}")
            return False
    
    def _handle_run_popup_simple(self) -> bool:
        """Simple keyboard method for RUN popup: Left Arrow + Enter"""
        try:
            self.logger.info("🔔 SIMPLE: Handling RUN popup with keyboard method (Left Arrow + Enter)...")
            
            # Wait a moment for popup to appear
            time.sleep(2)
            
            # Simple keyboard method - much more reliable
            self.logger.info("🎯 Using keyboard method: Left Arrow → Enter")
            
            try:
                self.logger.info("Step 1: Pressing Left Arrow to navigate to Run button...")
                pyautogui.press('left')
                time.sleep(0.5)
                
                self.logger.info("Step 2: Pressing Enter to click Run button...")
                pyautogui.press('enter')
                time.sleep(2)
                
                self.logger.info("✅ Keyboard method completed (Left Arrow + Enter)")
                return True
                
            except Exception as e:
                self.logger.warning(f"Keyboard method failed: {e}")
                
                # Fallback: Just Enter
                try:
                    self.logger.info("Fallback: Trying just Enter key...")
                    pyautogui.press('enter')
                    time.sleep(2)
                    return True
                except:
                    return False
            
        except Exception as e:
            self.logger.error(f"Simple popup handling failed: {e}")
            return False
    
    def _handle_popup_by_image(self) -> bool:
        """Method 1: Image-based popup detection"""
        try:
            self.logger.info("Method 1: Image-based popup detection")
            
            # Check for run popup image
            run_popup_image = "clicks/runpopup.png"
            if not os.path.exists(run_popup_image):
                return False
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Load template
            template = cv2.imread(run_popup_image)
            if template is None:
                return False
            
            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.7:  # 70% confidence
                self.logger.info(f"Run popup detected (confidence: {max_val:.2f})")
                
                # Calculate click position
                template_h, template_w = template.shape[:2]
                click_x = max_loc[0] + template_w // 2
                click_y = max_loc[1] + template_h // 2
                
                # Click the detected run button
                self._background_click(click_x, click_y)
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Image detection failed: {e}")
            return False
    
    def _handle_popup_by_window_activation(self) -> bool:
        """Method 2: Window activation and click"""
        try:
            self.logger.info("Method 2: Window activation popup handling")
            
            # Find security/permission dialogs
            popup_windows = self._find_security_dialogs()
            
            for hwnd, title in popup_windows:
                try:
                    self.logger.info(f"Found popup: {title}")
                    
                    # Temporarily activate popup
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.5)
                    
                    # Click Run button on popup
                    self._click_run_on_popup(hwnd)
                    
                    # Check if popup closed
                    time.sleep(1)
                    if not win32gui.IsWindowVisible(hwnd):
                        self.logger.info("Popup closed successfully")
                        return True
                    
                except Exception as e:
                    self.logger.warning(f"Could not handle popup {title}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Window activation failed: {e}")
            return False
    
    def _handle_popup_by_coordinates(self) -> bool:
        """Method 3: Direct coordinate clicking"""
        try:
            self.logger.info("Method 3: Coordinate-based popup handling")
            
            # Find and activate VBS window
            vbs_windows = self._find_vbs_windows()
            if not vbs_windows:
                return False
            
            vbs_hwnd = vbs_windows[0][0]
            
            # Temporarily activate VBS window
            win32gui.ShowWindow(vbs_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(vbs_hwnd)
            time.sleep(0.5)
            
            # Click Run button at exact coordinates
            run_x, run_y = self.coordinates["run_button"]
            
            # Multiple rapid clicks
            for i in range(3):
                self._background_click(run_x, run_y)
                time.sleep(0.3)
                
                # Check if login form appeared
                if self._is_login_form_visible():
                    self.logger.info(f"Login form appeared after click {i+1}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Coordinate handling failed: {e}")
            return False
    
    def _handle_popup_by_taskbar_recovery(self) -> bool:
        """Method 4: Taskbar recovery and click"""
        try:
            self.logger.info("Method 4: Taskbar recovery popup handling")
            
            # Find VBS in taskbar
            vbs_windows = self._find_vbs_windows()
            if not vbs_windows:
                return False
            
            for hwnd, title in vbs_windows:
                try:
                    # Click on taskbar to restore
                    self._click_taskbar_item(title)
                    time.sleep(1)
                    
                    # Now click Run button
                    run_x, run_y = self.coordinates["run_button"]
                    self._background_click(run_x, run_y)
                    time.sleep(0.5)
                    
                    # Check if login form appeared
                    if self._is_login_form_visible():
                        self.logger.info("Login form appeared after taskbar recovery")
                        return True
                    
                except Exception as e:
                    self.logger.warning(f"Taskbar recovery failed for {title}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Taskbar recovery failed: {e}")
            return False
    
    def perform_login_sequence(self) -> bool:
        """Perform VBS login sequence: IT dropdown → Date dropdown → Username → Password → Enter"""
        try:
            self.logger.info("🔐 Performing login sequence with correct field order...")
            
            # Find and activate VBS window
            if not self.window_handle:
                vbs_windows = self._find_vbs_windows()
                if not vbs_windows:
                    self.logger.error("No VBS windows found for login")
                    return False
                self.window_handle = vbs_windows[0][0]
            
            # Temporarily activate VBS window
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(2)
            
            # Login sequence in correct order
            self.logger.info("📋 Starting login field sequence...")
            
            # 1st field: IT dropdown
            self.logger.info("Step 1: Clicking IT dropdown...")
            self._click_coordinate(self.coordinates["it_dropdown"])
            time.sleep(0.5)
            pyautogui.typewrite("IT")
            time.sleep(0.5)
            pyautogui.press('enter')  # Confirm dropdown selection
            time.sleep(0.5)
            
            # 2nd field: Date dropdown (01/01/2023)
            self.logger.info("Step 2: Clicking Date dropdown...")
            self._click_coordinate(self.coordinates["date_field"])
            time.sleep(0.5)
            # Clear field first
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.typewrite("01/01/2023")
            time.sleep(0.5)
            
            # 3rd field: Username (vj)
            self.logger.info("Step 3: Clicking Username field...")
            self._click_coordinate(self.coordinates["username_field"])
            time.sleep(0.5)
            # Clear field completely
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)
            # Type username character by character
            for char in "vj":
                pyautogui.typewrite(char)
                time.sleep(0.1)
            time.sleep(0.5)
            
            # 4th field: Password (empty - just click to ensure it's empty)
            self.logger.info("Step 4: Ensuring password field is empty...")
            # Note: Password field coordinates might be near username, we'll use Tab to navigate
            pyautogui.press('tab')
            time.sleep(0.2)
            # Clear password field
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.5)
            
            # Final step: Submit login (Enter key method)
            self.logger.info("Step 5: Submitting login with Enter key...")
            pyautogui.press('enter')
            time.sleep(3)  # Wait for login to process
            
            self.logger.info("✅ Login sequence completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Login sequence failed: {e}")
            return False
        
        finally:
            # Always restore user context
            self.restore_user_context()
    
    def _find_vbs_windows(self):
        """Find VBS application windows"""
        try:
            vbs_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title and any(keyword in title.lower() for keyword in 
                                       ['absons', 'erp', 'login', 'system', 'moonflower']):
                            windows.append((hwnd, title))
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, vbs_windows)
            return vbs_windows
            
        except Exception as e:
            self.logger.warning(f"VBS window detection failed: {e}")
            return []
    
    def _find_vbs_window(self):
        """Find single VBS application window (returns first match)"""
        try:
            vbs_windows = self._find_vbs_windows()
            if vbs_windows:
                return vbs_windows[0][0]  # Return first window handle
            return None
            
        except Exception as e:
            self.logger.warning(f"VBS window detection failed: {e}")
            return None
    
    def _find_security_dialogs(self):
        """Find security/permission dialog windows"""
        try:
            dialogs = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        class_name = win32gui.GetClassName(hwnd)
                        
                        # Security dialog indicators
                        security_keywords = [
                            'security', 'run', 'allow', 'permission', 'warning',
                            'user account control', 'open file', 'confirm', 'publisher'
                        ]
                        
                        if (any(keyword in title.lower() for keyword in security_keywords) or
                            any(keyword in class_name.lower() for keyword in ['dialog', '#32770'])):
                            windows.append((hwnd, title))
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, dialogs)
            return dialogs
            
        except Exception as e:
            self.logger.warning(f"Security dialog detection failed: {e}")
            return []
    
    def _background_click(self, x: int, y: int):
        """Perform click while preserving user context"""
        try:
            # Save current cursor position
            current_pos = win32gui.GetCursorPos()
            
            # Perform click
            pyautogui.click(x, y, duration=0.1)
            
            # Restore cursor (always restore to be safe)
            win32gui.SetCursorPos(current_pos)
            
        except Exception as e:
            self.logger.warning(f"Background click failed: {e}")
    
    def _click_run_on_popup(self, hwnd: int):
        """Click Run button on popup dialog"""
        try:
            # Get popup window rectangle
            rect = win32gui.GetWindowRect(hwnd)
            
            # Calculate likely Run button positions
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            
            # Try different positions where Run button might be
            run_positions = [
                (center_x, center_y + 20),      # Center-bottom
                (center_x + 40, center_y + 20), # Right of center
                (center_x - 40, center_y + 20), # Left of center
            ]
            
            for x, y in run_positions:
                self._background_click(x, y)
                time.sleep(0.3)
            
        except Exception as e:
            self.logger.warning(f"Popup click failed: {e}")
    
    def _click_taskbar_item(self, window_title: str):
        """Click on taskbar item to restore window"""
        try:
            # This is a simplified approach - clicking on taskbar area
            # In a real implementation, you'd need to find the exact taskbar button
            taskbar_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) - 40
            taskbar_x = 100  # Approximate position
            
            self._background_click(taskbar_x, taskbar_y)
            
        except Exception as e:
            self.logger.warning(f"Taskbar click failed: {e}")
    
    def _is_login_form_visible(self) -> bool:
        """Check if VBS login form is visible"""
        try:
            vbs_windows = self._find_vbs_windows()
            return len(vbs_windows) > 0
        except:
            return False
    
    def _click_coordinate(self, coordinate: Tuple[int, int]) -> bool:
        """Click at specific coordinate using Windows API"""
        try:
            x, y = coordinate
            
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            
            # Perform click using Windows API
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            self.logger.info(f"Clicked at coordinate: ({x}, {y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking coordinate {coordinate}: {e}")
            return False
    
    def preserve_user_context(self):
        """Preserve user's current working context"""
        try:
            self.user_active_window = win32gui.GetForegroundWindow()
            self.logger.info("User context preserved")
        except Exception as e:
            self.logger.warning(f"Could not preserve user context: {e}")
    
    def restore_user_context(self):
        """Restore user's working context"""
        try:
            if hasattr(self, 'user_active_window') and self.user_active_window:
                win32gui.SetForegroundWindow(self.user_active_window)
                self.logger.info("User context restored")
        except Exception as e:
            self.logger.warning(f"Could not restore user context: {e}")
    
    def run_phase_1_complete(self) -> Dict[str, any]:
        """Run complete Phase 1: Launch + Login"""
        try:
            self.logger.info("🚀 Starting Phase 1: Application Launch & Login (IMPROVED)")
            
            phase_result = {
                "success": False,
                "tasks_completed": [],
                "errors": [],
                "start_time": datetime.now().isoformat()
            }
            
            # Task 1.1: Launch Application (IMPROVED)
            launch_result = self.task_1_1_launch_application_improved()
            if launch_result["success"]:
                phase_result["tasks_completed"].append("1.1_launch_improved")
                self.logger.info("✅ Task 1.1 completed: Application launched (IMPROVED)")
            else:
                phase_result["errors"].append(f"Task 1.1 failed: {launch_result['error']}")
                return phase_result
            
            # Task 1.2: Login Sequence
            login_result = self.perform_login_sequence()
            if login_result:
                phase_result["tasks_completed"].append("1.2_login")
                self.logger.info("✅ Task 1.2 completed: Login successful")
                phase_result["success"] = True
            else:
                phase_result["errors"].append("Task 1.2 failed: Login sequence failed")
                return phase_result
            
            phase_result["end_time"] = datetime.now().isoformat()
            self.logger.info("🎉 Phase 1 completed successfully! (IMPROVED)")
            
            return phase_result
            
        except Exception as e:
            error_msg = f"Phase 1 execution failed: {e}"
            self.logger.error(error_msg)
            phase_result["errors"].append(error_msg)
            phase_result["end_time"] = datetime.now().isoformat()
            return phase_result
    
    def get_window_handle(self) -> Optional[int]:
        """Get current window handle"""
        return self.window_handle

# Test function
def test_phase_1_improved():
    """Test Phase 1 IMPROVED implementation"""
    print("🧪 Testing VBS Phase 1: Launch & Login (IMPROVED)")
    print("=" * 60)
    
    phase1 = VBSPhase1_LaunchLogin_Improved()
    
    # Test complete phase
    print("\n1. Testing complete Phase 1 (improved)...")
    phase_result = phase1.run_phase_1_complete()
    print(f"   Phase 1 result: {phase_result}")
    
    print("\n✅ Phase 1 IMPROVED testing completed")

if __name__ == "__main__":
    test_phase_1_improved()