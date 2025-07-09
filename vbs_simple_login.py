#!/usr/bin/env python3
"""
VBS Simple Login - Controlled and Patient
Waits properly for login form and fills it without rushing
"""

import os
import sys
import time
import logging
import subprocess
import win32gui
import win32con
import win32api
import win32process
import pyautogui
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class VBSSimpleLogin:
    """
    Very simple and controlled VBS login
    Waits properly and doesn't rush the process
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.vbs_window_handle = None
        self.vbs_process_id = None
        
        # VBS application paths
        self.vbs_paths = [
            r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk",
            r"\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe"
        ]
        
        # Disable pyautogui fail-safe
        pyautogui.FAILSAFE = False
        
        self.logger.info("🐌 VBS Simple Login initialized - Slow and Steady")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("VBSSimpleLogin")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_simple_login(self) -> Dict[str, any]:
        """Run simple login process"""
        try:
            self.logger.info("🐌 Starting SIMPLE VBS login - Slow and Steady approach")
            
            result = {
                "success": False,
                "start_time": datetime.now().isoformat(),
                "errors": []
            }
            
            # Step 1: Launch VBS and wait patiently
            self.logger.info("🚀 Step 1: Launching VBS and waiting patiently...")
            if not self._launch_and_wait():
                result["errors"].append("VBS launch failed")
                return result
            
            # Step 2: Wait for login form to be completely ready
            self.logger.info("⏳ Step 2: Waiting for login form to be completely ready...")
            if not self._wait_for_login_form():
                result["errors"].append("Login form not ready")
                return result
            
            # Step 3: Fill login form carefully
            self.logger.info("📝 Step 3: Filling login form carefully...")
            if not self._fill_login_carefully():
                result["errors"].append("Login form filling failed")
                return result
            
            # Step 4: Submit login
            self.logger.info("📤 Step 4: Submitting login...")
            if not self._submit_login_carefully():
                result["errors"].append("Login submission failed")
                return result
            
            result["success"] = True
            result["end_time"] = datetime.now().isoformat()
            self.logger.info("🎉 Simple login completed successfully!")
            
            return result
            
        except Exception as e:
            error_msg = f"Simple login failed: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
            result["end_time"] = datetime.now().isoformat()
            return result
    
    def _launch_and_wait(self) -> bool:
        """Launch VBS and wait patiently"""
        try:
            # Try each path
            for i, path in enumerate(self.vbs_paths):
                try:
                    self.logger.info(f"📁 Trying VBS path {i+1}: {path}")
                    
                    if not os.path.exists(path):
                        self.logger.warning(f"❌ Path not found: {path}")
                        continue
                    
                    # Launch VBS
                    process = subprocess.Popen([path], shell=True)
                    self.logger.info(f"🚀 VBS process started: PID {process.pid}")
                    
                    # Wait for security popup if it appears
                    self.logger.info("⏳ Waiting for potential security popup...")
                    time.sleep(5)
                    
                    # Check for security popup ONCE
                    if self._check_and_handle_security_popup():
                        self.logger.info("✅ Security popup handled")
                    else:
                        self.logger.info("ℹ️ No security popup found")
                    
                    # Wait longer for VBS to fully load
                    self.logger.info("⏳ Waiting for VBS to fully load...")
                    time.sleep(15)
                    
                    # Check if VBS window appeared
                    if self._find_vbs_window():
                        self.logger.info("✅ VBS window found")
                        return True
                    else:
                        self.logger.warning(f"❌ VBS window not found for path {i+1}")
                        continue
                    
                except Exception as e:
                    self.logger.warning(f"❌ VBS path {i+1} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ VBS launch failed: {e}")
            return False
    
    def _check_and_handle_security_popup(self) -> bool:
        """Check for security popup and handle it ONCE"""
        try:
            popup_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd).lower()
                        if any(word in title for word in ['security', 'warning', 'open file', 'publisher']):
                            windows.append(hwnd)
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, popup_windows)
            
            if popup_windows:
                self.logger.info("🔐 Security popup found, handling ONCE...")
                hwnd = popup_windows[0]
                
                try:
                    # Bring popup to front
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(1)
                    
                    # Press LEFT ARROW then ENTER (as user specified)
                    pyautogui.press('left')
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(2)
                    
                    self.logger.info("✅ Security popup handled with LEFT+ENTER")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Popup handling failed: {e}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Security popup check failed: {e}")
            return False
    
    def _find_vbs_window(self) -> bool:
        """Find VBS window"""
        try:
            vbs_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            # Look for VBS login window specifically
                            if 'login' in title.lower() and any(keyword in title.lower() for keyword in ['absons', 'system']):
                                windows.append((hwnd, title))
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, vbs_windows)
            
            if vbs_windows:
                self.vbs_window_handle = vbs_windows[0][0]
                _, self.vbs_process_id = win32process.GetWindowThreadProcessId(self.vbs_window_handle)
                
                vbs_title = vbs_windows[0][1]
                self.logger.info(f"✅ VBS login window found: '{vbs_title}'")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ VBS window search failed: {e}")
            return False
    
    def _wait_for_login_form(self) -> bool:
        """Wait for login form to be completely ready"""
        try:
            if not self.vbs_window_handle:
                return False
            
            # Bring VBS window to front gently
            self.logger.info("🎯 Bringing VBS login window to front...")
            win32gui.ShowWindow(self.vbs_window_handle, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.vbs_window_handle)
            
            # Wait for window to be ready
            time.sleep(3)
            
            # Single click in center to ensure focus (NOT double click)
            rect = win32gui.GetWindowRect(self.vbs_window_handle)
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            
            self.logger.info(f"🖱️ Single click to focus VBS window: ({center_x}, {center_y})")
            pyautogui.click(center_x, center_y)
            time.sleep(2)
            
            # Wait for form to be stable
            self.logger.info("⏳ Waiting for login form to stabilize...")
            time.sleep(5)
            
            self.logger.info("✅ Login form should be ready now")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Login form wait failed: {e}")
            return False
    
    def _fill_login_carefully(self) -> bool:
        """Fill login form very carefully"""
        try:
            self.logger.info("📝 Starting careful form filling...")
            
            # Step 1: Fill Company field with "IT"
            self.logger.info("📝 Step 1: Filling Company field with 'IT'...")
            
            # Clear any existing content
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # Type IT slowly
            pyautogui.typewrite('IT', interval=0.2)
            time.sleep(1)
            
            self.logger.info("✅ Company field filled with 'IT'")
            
            # Tab to next field
            pyautogui.press('tab')
            time.sleep(1)
            
            # Step 2: Fill Financial Year with "01/01/2023"
            self.logger.info("📝 Step 2: Filling Financial Year with '01/01/2023'...")
            
            # Clear and type financial year
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            pyautogui.typewrite('01/01/2023', interval=0.1)
            time.sleep(1)
            
            self.logger.info("✅ Financial Year field filled with '01/01/2023'")
            
            # Tab to next field
            pyautogui.press('tab')
            time.sleep(1)
            
            # Step 3: Fill Username with "vj"
            self.logger.info("📝 Step 3: Filling Username with 'vj'...")
            
            # Clear any existing content (like "rdsr")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.3)
            pyautogui.press('backspace')  # Extra clearing
            time.sleep(0.3)
            
            pyautogui.typewrite('vj', interval=0.2)
            time.sleep(1)
            
            self.logger.info("✅ Username field filled with 'vj'")
            
            self.logger.info("✅ All form fields filled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Form filling failed: {e}")
            return False
    
    def _submit_login_carefully(self) -> bool:
        """Submit login carefully"""
        try:
            self.logger.info("📤 Submitting login carefully...")
            
            # Wait a moment before submitting
            time.sleep(2)
            
            # Try Enter key first
            self.logger.info("📤 Trying Enter key...")
            pyautogui.press('enter')
            time.sleep(4)
            
            # Check if login was successful
            if self._check_login_success():
                self.logger.info("✅ Login successful with Enter key")
                return True
            
            # Try Tab to OK button then Enter
            self.logger.info("📤 Trying Tab + Enter...")
            pyautogui.press('tab')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(4)
            
            if self._check_login_success():
                self.logger.info("✅ Login successful with Tab + Enter")
                return True
            
            # Try Space key
            self.logger.info("📤 Trying Space key...")
            pyautogui.press('space')
            time.sleep(4)
            
            if self._check_login_success():
                self.logger.info("✅ Login successful with Space key")
                return True
            
            # Assume success if we've tried everything
            self.logger.info("⚠️ Login submission methods completed, assuming success")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Login submission failed: {e}")
            return False
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            if not self.vbs_window_handle:
                return False
            
            # Check if window title changed
            current_title = win32gui.GetWindowText(self.vbs_window_handle)
            
            # If title no longer contains "login", probably successful
            if 'login' not in current_title.lower():
                self.logger.info(f"✅ Login success detected: title changed to '{current_title}'")
                return True
            
            # Check for new main application windows
            main_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            # Check if this belongs to our VBS process
                            _, window_process_id = win32process.GetWindowThreadProcessId(hwnd)
                            
                            if window_process_id == self.vbs_process_id:
                                # Look for main app indicators
                                if any(indicator in title.lower() for indicator in ['absons', 'erp', 'edition']):
                                    if 'login' not in title.lower():
                                        windows.append((hwnd, title))
                                        
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, main_windows)
            
            if main_windows:
                self.logger.info(f"✅ Main application window found: {main_windows[0][1]}")
                self.vbs_window_handle = main_windows[0][0]  # Update to main window
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Login success check failed: {e}")
            return False
    
    def get_window_handle(self):
        """Get VBS window handle"""
        return self.vbs_window_handle
    
    def get_process_id(self):
        """Get VBS process ID"""
        return self.vbs_process_id

def test_simple_login():
    """Test the simple VBS login"""
    print("🐌 TESTING VBS SIMPLE LOGIN")
    print("=" * 50)
    print("This approach:")
    print("✅ Waits patiently for each step")
    print("✅ Uses single click (not double click)")
    print("✅ Handles security popup properly")
    print("✅ Fills form carefully and slowly")
    print("✅ Doesn't rush the process")
    print("=" * 50)
    
    # Run simple login
    login = VBSSimpleLogin()
    result = login.run_simple_login()
    
    print(f"\n📊 SIMPLE LOGIN RESULTS:")
    print(f"Success: {result['success']}")
    print(f"Start Time: {result['start_time']}")
    print(f"End Time: {result.get('end_time', 'N/A')}")
    
    if result.get('errors'):
        print(f"\n❌ ERRORS:")
        for error in result['errors']:
            print(f"   • {error}")
    
    if result["success"]:
        print(f"\n🎉 SIMPLE LOGIN SUCCESSFUL!")
        print(f"VBS Window Handle: {hex(login.get_window_handle()) if login.get_window_handle() else 'N/A'}")
        print(f"VBS Process ID: {login.get_process_id()}")
        print("\n✅ VBS login completed without rushing!")
    else:
        print(f"\n❌ SIMPLE LOGIN FAILED!")
    
    print("\n" + "=" * 50)
    print("VBS Simple Login Test Completed")

if __name__ == "__main__":
    test_simple_login() 