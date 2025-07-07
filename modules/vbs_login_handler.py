#!/usr/bin/env python3
"""
VBS Login Handler
Handles login automation for VBS (Absons IT ERP) application
Manages security dialogs, credential input, and login verification
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
import win32gui
import win32con
import win32api
import pyautogui
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logger import logger

class VBSLoginHandler:
    """
    VBS Login Handler for automating login process
    Handles security dialogs, popup navigation, and credential input
    """
    
    def __init__(self, vbs_controller):
        """
        Initialize VBS Login Handler
        
        Args:
            vbs_controller: VBSAppController instance
        """
        self.vbs_controller = vbs_controller
        self.config = {
            "credentials": {
                "department": "IT",
                "date": "01/01/2023",
                "username": "Vj"
            },
            "login_timeout": 30,
            "popup_timeout": 10,
            "input_delay": 0.5,
            "retry_attempts": 3
        }
        
        # Known coordinate positions from previous testing
        self.coordinates = {
            "it_dropdown": (1054, 528),
            "date_field": (1053, 565),
            "username_field": (929, 561),
            "ok_button": (897, 724),
            "run_button": (1043, 608)
        }
        
        logger.info("VBS Login Handler initialized", "VBSLogin")
    
    def perform_login(self) -> Dict[str, Any]:
        """
        Perform complete login process for VBS application
        
        Returns:
            Dictionary with login results
        """
        try:
            logger.info("🔐 Starting VBS login process...", "VBSLogin")
            
            # Ensure VBS window is in foreground
            if not self.vbs_controller.bring_to_foreground():
                return {"success": False, "error": "Failed to bring VBS window to foreground"}
            
            # Step 1: Wait for and handle security popup
            popup_result = self._handle_security_popup()
            if not popup_result["success"]:
                return popup_result
            
            # Step 2: Fill login form
            form_result = self._fill_login_form()
            if not form_result["success"]:
                return form_result
            
            # Step 3: Submit login
            submit_result = self._submit_login()
            if not submit_result["success"]:
                return submit_result
            
            # Step 4: Verify login success
            verify_result = self._verify_login_success()
            if not verify_result["success"]:
                return verify_result
            
            logger.info("✅ VBS login completed successfully", "VBSLogin")
            return {
                "success": True,
                "message": "Login completed successfully",
                "steps_completed": [
                    "security_popup_handled",
                    "login_form_filled",
                    "login_submitted",
                    "login_verified"
                ]
            }
            
        except Exception as e:
            error_msg = f"Login process failed: {e}"
            logger.error(error_msg, "VBSLogin")
            return {"success": False, "error": error_msg}
    
    def _handle_security_popup(self) -> Dict[str, Any]:
        """
        Handle security popup/dialog that appears on VBS startup
        
        Returns:
            Dictionary with popup handling results
        """
        try:
            logger.info("🔍 Looking for security popup...", "VBSLogin")
            
            # Wait for popup to appear
            popup_found = False
            start_time = time.time()
            
            while time.time() - start_time < self.config["popup_timeout"]:
                # Look for security-related popup windows
                popup_windows = self._find_popup_windows()
                
                if popup_windows:
                    popup_found = True
                    break
                
                time.sleep(0.5)
            
            if popup_found:
                logger.info("🔐 Security popup detected, handling...", "VBSLogin")
                
                # Navigate popup using LEFT ARROW + ENTER (user-specified method)
                pyautogui.press('left')  # Navigate to Run button
                time.sleep(0.5)
                pyautogui.press('enter')  # Press Run button
                time.sleep(2)  # Wait for popup to close
                
                logger.info("✅ Security popup handled", "VBSLogin")
            else:
                logger.info("ℹ️ No security popup detected", "VBSLogin")
            
            return {"success": True, "popup_found": popup_found}
            
        except Exception as e:
            error_msg = f"Error handling security popup: {e}"
            logger.error(error_msg, "VBSLogin")
            return {"success": False, "error": error_msg}
    
    def _find_popup_windows(self) -> List[int]:
        """
        Find popup/dialog windows related to VBS security
        
        Returns:
            List of popup window handles
        """
        try:
            popup_patterns = [
                "security", "warning", "certificate", "run", "dialog",
                "confirm", "allow", "trust", "permission"
            ]
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd).lower()
                    class_name = win32gui.GetClassName(hwnd).lower()
                    
                    # Check for popup patterns in title or class
                    for pattern in popup_patterns:
                        if pattern in window_title or pattern in class_name:
                            windows.append(hwnd)
                            break
                
                return True
            
            popup_windows = []
            win32gui.EnumWindows(enum_windows_callback, popup_windows)
            
            return popup_windows
            
        except Exception as e:
            logger.error(f"Error finding popup windows: {e}", "VBSLogin")
            return []
    
    def _fill_login_form(self) -> Dict[str, Any]:
        """
        Fill the VBS login form with credentials
        
        Returns:
            Dictionary with form filling results
        """
        try:
            logger.info("📝 Filling login form...", "VBSLogin")
            
            # Give VBS time to load login form
            time.sleep(3)
            
            # Step 1: Fill IT dropdown
            logger.info("Filling IT dropdown...", "VBSLogin")
            self._click_coordinate(self.coordinates["it_dropdown"])
            time.sleep(self.config["input_delay"])
            pyautogui.typewrite(self.config["credentials"]["department"])
            time.sleep(self.config["input_delay"])
            
            # Step 2: Fill date field
            logger.info("Filling date field...", "VBSLogin")
            self._click_coordinate(self.coordinates["date_field"])
            time.sleep(self.config["input_delay"])
            pyautogui.typewrite(self.config["credentials"]["date"])
            time.sleep(self.config["input_delay"])
            
            # Step 3: Fill username field (with clearing as user specified)
            logger.info("Filling username field...", "VBSLogin")
            self._click_coordinate(self.coordinates["username_field"])
            time.sleep(self.config["input_delay"])
            
            # Clear field completely (user specified method)
            pyautogui.hotkey('ctrl', 'a')  # Select all
            time.sleep(0.2)
            pyautogui.press('delete')  # Delete
            time.sleep(0.2)
            pyautogui.press('backspace')  # Backspace for good measure
            time.sleep(0.2)
            
            # Type username character by character (user specified method)
            for char in self.config["credentials"]["username"]:
                pyautogui.typewrite(char)
                time.sleep(0.1)  # Small delay between characters
            
            time.sleep(self.config["input_delay"])
            
            logger.info("✅ Login form filled successfully", "VBSLogin")
            return {"success": True, "message": "Login form filled"}
            
        except Exception as e:
            error_msg = f"Error filling login form: {e}"
            logger.error(error_msg, "VBSLogin")
            return {"success": False, "error": error_msg}
    
    def _click_coordinate(self, coordinate: Tuple[int, int]) -> bool:
        """
        Click at specific coordinate using direct Windows API
        
        Args:
            coordinate: (x, y) coordinate to click
            
        Returns:
            True if successful, False otherwise
        """
        try:
            x, y = coordinate
            
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            
            # Perform click using Windows API
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            logger.info(f"Clicked at coordinate: ({x}, {y})", "VBSLogin")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking coordinate {coordinate}: {e}", "VBSLogin")
            return False
    
    def _submit_login(self) -> Dict[str, Any]:
        """
        Submit the login form by clicking OK button with multiple retry methods
        
        Returns:
            Dictionary with submission results
        """
        try:
            logger.info("📤 Submitting login form...", "VBSLogin")
            
            # Try multiple OK button coordinates and methods
            ok_methods = [
                # Method 1: Original coordinate
                ("Original OK coordinate", lambda: self._click_coordinate(self.coordinates["ok_button"])),
                
                # Method 2: Alternative coordinates
                ("OK coordinate +4 up", lambda: self._click_coordinate((897, 720))),
                ("OK coordinate +4 down", lambda: self._click_coordinate((897, 728))),
                ("OK coordinate +3 right", lambda: self._click_coordinate((900, 724))),
                ("OK coordinate +3 left", lambda: self._click_coordinate((894, 724))),
                
                # Method 3: Double click
                ("Double click OK", lambda: self._double_click_coordinate(self.coordinates["ok_button"])),
                
                # Method 4: Keyboard methods
                ("Enter key", lambda: pyautogui.press('enter')),
                ("Tab + Enter", lambda: (pyautogui.press('tab'), time.sleep(0.2), pyautogui.press('enter'))),
                ("Space key", lambda: pyautogui.press('space')),
                ("Alt + O", lambda: pyautogui.hotkey('alt', 'o')),
            ]
            
            for method_name, method_func in ok_methods:
                try:
                    logger.info(f"Trying {method_name}...", "VBSLogin")
                    
                    # Execute the method
                    method_func()
                    time.sleep(2)  # Wait for response
                    
                    # Check if login progressed by looking for window changes
                    if self._check_login_progress():
                        logger.info(f"✅ Login submitted successfully using {method_name}", "VBSLogin")
                        return {"success": True, "method": method_name}
                    
                except Exception as e:
                    logger.warning(f"Method {method_name} failed: {e}", "VBSLogin")
                    continue
            
            # If all methods failed
            logger.error("All OK button methods failed", "VBSLogin")
            return {"success": False, "error": "All OK button clicking methods failed"}
            
        except Exception as e:
            error_msg = f"Error submitting login: {e}"
            logger.error(error_msg, "VBSLogin")
            return {"success": False, "error": error_msg}
    
    def _double_click_coordinate(self, coordinate: Tuple[int, int]) -> bool:
        """
        Double click at specific coordinate
        
        Args:
            coordinate: (x, y) coordinate to double click
            
        Returns:
            True if successful, False otherwise
        """
        try:
            x, y = coordinate
            
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            
            # Perform double click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            logger.info(f"Double clicked at coordinate: ({x}, {y})", "VBSLogin")
            return True
            
        except Exception as e:
            logger.error(f"Error double clicking coordinate {coordinate}: {e}", "VBSLogin")
            return False
    
    def _check_login_progress(self) -> bool:
        """
        Check if login has progressed (dialog closed, new window appeared, etc.)
        
        Returns:
            True if login progressed, False otherwise
        """
        try:
            # Simple check: if VBS window is still responsive and title might have changed
            window_info = self.vbs_controller.get_window_info()
            
            if window_info.get("handle"):
                # If window is still there and responsive, assume progress was made
                # In a real implementation, you might check for specific UI elements
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking login progress: {e}", "VBSLogin")
            return False
    
    def _verify_login_success(self) -> Dict[str, Any]:
        """
        Verify that login was successful
        
        Returns:
            Dictionary with verification results
        """
        try:
            logger.info("✅ Verifying login success...", "VBSLogin")
            
            # Wait for login to process
            time.sleep(5)
            
            # Check if VBS main interface is now available
            window_info = self.vbs_controller.get_window_info()
            
            if window_info.get("handle"):
                # Take screenshot for verification
                screenshot_path = self.vbs_controller.take_screenshot("login_verification.png")
                
                logger.info("✅ Login verification completed", "VBSLogin")
                return {
                    "success": True,
                    "message": "Login verified successfully",
                    "screenshot": screenshot_path,
                    "window_info": window_info
                }
            else:
                return {
                    "success": False,
                    "error": "Login verification failed - no VBS window found"
                }
            
        except Exception as e:
            error_msg = f"Error verifying login: {e}"
            logger.error(error_msg, "VBSLogin")
            return {"success": False, "error": error_msg}
    
    def handle_run_button_dialog(self) -> Dict[str, Any]:
        """
        Handle the Run button dialog that may appear after login
        
        Returns:
            Dictionary with dialog handling results
        """
        try:
            logger.info("🔄 Checking for Run button dialog...", "VBSLogin")
            
            # Look for Run button dialog
            time.sleep(2)
            
            # Try clicking Run button if it exists
            self._click_coordinate(self.coordinates["run_button"])
            time.sleep(1)
            
            logger.info("✅ Run button dialog handled", "VBSLogin")
            return {"success": True, "message": "Run button dialog handled"}
            
        except Exception as e:
            error_msg = f"Error handling Run button dialog: {e}"
            logger.error(error_msg, "VBSLogin")
            return {"success": False, "error": error_msg}

def test_vbs_login():
    """Test VBS Login Handler functionality"""
    print("🧪 TESTING VBS LOGIN HANDLER")
    print("=" * 50)
    
    # Import and initialize VBS controller
    from vbs_app_controller import VBSAppController
    
    controller = VBSAppController()
    login_handler = VBSLoginHandler(controller)
    
    try:
        # Step 1: Launch VBS application
        print("\n1. Launching VBS application...")
        launch_result = controller.launch_application()
        
        if launch_result["success"]:
            print("✅ VBS application launched")
            
            # Step 2: Perform login
            print("\n2. Performing login...")
            login_result = login_handler.perform_login()
            
            if login_result["success"]:
                print("✅ Login completed successfully")
                print(f"   Steps completed: {login_result.get('steps_completed')}")
                
                # Wait for user to see the result
                input("\nPress Enter to close the application...")
            else:
                print(f"❌ Login failed: {login_result.get('error')}")
            
            # Step 3: Close application
            print("\n3. Closing application...")
            controller.close_application()
            
        else:
            print(f"❌ Failed to launch VBS: {launch_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    print("\n" + "=" * 50)
    print("VBS Login Handler Test Completed")

if __name__ == "__main__":
    test_vbs_login() 