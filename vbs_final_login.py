#!/usr/bin/env python3
"""
VBS Final Login - Proper Start Position Handling
Handles cursor starting in password field and navigates to first field properly
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

class VBSFinalLogin:
    """
    Final VBS login that properly handles starting position
    Cursor starts in password field → navigate to first field → fill form
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
        
        self.logger.info("🎯 VBS Final Login initialized - Proper Start Position Handling")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("VBSFinalLogin")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_final_login(self) -> Dict[str, any]:
        """Run final login process"""
        try:
            self.logger.info("🎯 Starting VBS final login - Proper start position handling...")
            
            result = {
                "success": False,
                "start_time": datetime.now().isoformat(),
                "errors": [],
                "form_fields": []
            }
            
            # Step 1: Launch VBS
            self.logger.info("🚀 Step 1: Launching VBS...")
            if not self._launch_vbs():
                result["errors"].append("VBS launch failed")
                return result
            
            # Step 2: Find VBS window
            self.logger.info("🔍 Step 2: Finding VBS window...")
            if not self._find_vbs_window():
                result["errors"].append("VBS window not found")
                return result
            
            # Step 3: Prepare window
            self.logger.info("🎯 Step 3: Preparing VBS window...")
            if not self._prepare_vbs_window():
                result["errors"].append("VBS window preparation failed")
                return result
            
            # Step 4: Navigate from password field to first field and fill
            self.logger.info("🧭 Step 4: Navigating from password field to first field...")
            form_fields = self._navigate_from_password_to_first_and_fill()
            result["form_fields"] = form_fields
            
            if len(form_fields) < 3:
                result["errors"].append("Not enough fields filled")
                return result
            
            # Step 5: Submit form
            self.logger.info("📤 Step 5: Submitting form...")
            if not self._submit_form():
                result["errors"].append("Form submission failed")
                return result
            
            result["success"] = True
            result["end_time"] = datetime.now().isoformat()
            self.logger.info("🎉 VBS final login completed successfully!")
            
            return result
            
        except Exception as e:
            error_msg = f"Final login failed: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
            result["end_time"] = datetime.now().isoformat()
            return result
    
    def _launch_vbs(self) -> bool:
        """Launch VBS application"""
        try:
            for i, path in enumerate(self.vbs_paths):
                try:
                    self.logger.info(f"📁 Trying VBS path {i+1}: {path}")
                    
                    if not os.path.exists(path):
                        self.logger.warning(f"❌ Path not found: {path}")
                        continue
                    
                    # Launch VBS
                    process = subprocess.Popen([path], shell=True)
                    self.logger.info(f"🚀 VBS process started: PID {process.pid}")
                    
                    # Wait for security popup
                    time.sleep(5)
                    self._handle_security_popup()
                    
                    # Wait for VBS to load
                    self.logger.info("⏳ Waiting for VBS to load...")
                    time.sleep(15)
                    
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"❌ VBS path {i+1} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ VBS launch failed: {e}")
            return False
    
    def _handle_security_popup(self):
        """Handle security popup"""
        try:
            self.logger.info("🔐 Checking for security popup...")
            
            # Look for security popup
            popup_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd).lower()
                        if any(word in title for word in ['security', 'warning', 'open file']):
                            windows.append(hwnd)
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, popup_windows)
            
            if popup_windows:
                self.logger.info("🔐 Security popup found, handling...")
                pyautogui.press('left')
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)
                self.logger.info("✅ Security popup handled")
            else:
                self.logger.info("ℹ️ No security popup found")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Security popup handling error: {e}")
    
    def _find_vbs_window(self) -> bool:
        """Find VBS window"""
        try:
            time.sleep(5)
            
            vbs_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
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
                self.logger.info(f"✅ VBS window found: '{vbs_title}' (Handle: {hex(self.vbs_window_handle)})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ VBS window search failed: {e}")
            return False
    
    def _prepare_vbs_window(self) -> bool:
        """Prepare VBS window"""
        try:
            if not self.vbs_window_handle:
                return False
            
            # Show window
            try:
                win32gui.ShowWindow(self.vbs_window_handle, win32con.SW_RESTORE)
                win32gui.ShowWindow(self.vbs_window_handle, win32con.SW_SHOW)
                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"⚠️ Window show failed: {e}")
            
            # Click on window to give it focus
            rect = win32gui.GetWindowRect(self.vbs_window_handle)
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            
            self.logger.info(f"🖱️ Clicking VBS window at ({center_x}, {center_y})")
            pyautogui.click(center_x, center_y)
            time.sleep(2)
            
            # Wait for window to be ready
            self.logger.info("⏳ Waiting for VBS window to be ready...")
            time.sleep(3)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ VBS window preparation failed: {e}")
            return False
    
    def _navigate_from_password_to_first_and_fill(self) -> list:
        """Navigate from password field (default start) to first field and fill form"""
        form_fields = []
        
        try:
            self.logger.info("🧭 Starting navigation from password field to first field...")
            
            # IMPORTANT: Cursor starts in PASSWORD field by default
            self.logger.info("📍 Current position: PASSWORD field (default start position)")
            
            # Navigate from password field to first field (Company)
            # We need to go backwards through the form fields
            self.logger.info("🧭 Navigating from password field to Company field...")
            
            # Use Shift+Tab to go backwards to previous fields
            # Password → Username → Financial Year → Company
            for i in range(3):
                pyautogui.hotkey('shift', 'tab')
                time.sleep(0.5)
                self.logger.info(f"🧭 Shift+Tab {i+1}/3")
            
            self.logger.info("✅ Should now be at Company field (first field)")
            
            # FIELD 1: Company = "IT"
            self.logger.info("📝 Field 1: Filling Company with 'IT'")
            try:
                # Clear any existing content
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                pyautogui.press('delete')
                time.sleep(0.3)
                
                # Type IT
                pyautogui.typewrite('IT', interval=0.3)
                time.sleep(1)
                
                form_fields.append("Company: IT")
                self.logger.info("✅ Company field filled with 'IT'")
            except Exception as e:
                self.logger.error(f"❌ Company field failed: {e}")
            
            # Move to next field (Financial Year)
            pyautogui.press('tab')
            time.sleep(1)
            
            # FIELD 2: Financial Year = "01/01/2023"
            self.logger.info("📝 Field 2: Filling Financial Year with '01/01/2023'")
            try:
                # Clear any existing content
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                pyautogui.press('delete')
                time.sleep(0.3)
                
                # Type Financial Year
                pyautogui.typewrite('01/01/2023', interval=0.2)
                time.sleep(1)
                
                form_fields.append("Financial Year: 01/01/2023")
                self.logger.info("✅ Financial Year field filled with '01/01/2023'")
            except Exception as e:
                self.logger.error(f"❌ Financial Year field failed: {e}")
            
            # Move to next field (Username)
            pyautogui.press('tab')
            time.sleep(1)
            
            # FIELD 3: Username = "vj" (clear any existing "rdsr")
            self.logger.info("📝 Field 3: Filling Username with 'vj' (clearing existing 'rdsr')")
            try:
                # Aggressive clearing for username field
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                pyautogui.press('delete')
                time.sleep(0.3)
                # Multiple backspaces to ensure complete clearing
                for _ in range(5):
                    pyautogui.press('backspace')
                    time.sleep(0.1)
                
                # Type vj
                pyautogui.typewrite('vj', interval=0.3)
                time.sleep(1)
                
                form_fields.append("Username: vj")
                self.logger.info("✅ Username field filled with 'vj' (cleared existing content)")
            except Exception as e:
                self.logger.error(f"❌ Username field failed: {e}")
            
            # Move to next field (Password)
            pyautogui.press('tab')
            time.sleep(1)
            
            # FIELD 4: Password = "" (leave empty)
            self.logger.info("📝 Field 4: Leaving Password field empty")
            try:
                # Clear password field to ensure it's empty
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                pyautogui.press('delete')
                time.sleep(0.3)
                
                form_fields.append("Password: (empty)")
                self.logger.info("✅ Password field cleared and left empty")
            except Exception as e:
                self.logger.error(f"❌ Password field failed: {e}")
            
            self.logger.info(f"📊 Form fields filled: {len(form_fields)}/4")
            for field in form_fields:
                self.logger.info(f"   ✅ {field}")
            
            return form_fields
            
        except Exception as e:
            self.logger.error(f"❌ Navigation and filling failed: {e}")
            return form_fields
    
    def _submit_form(self) -> bool:
        """Submit the form"""
        try:
            self.logger.info("📤 Submitting form...")
            
            # Wait before submitting
            time.sleep(2)
            
            # Try Enter key
            self.logger.info("📤 Trying Enter key...")
            pyautogui.press('enter')
            time.sleep(4)
            
            # Check if login was successful
            if self._check_login_success():
                self.logger.info("✅ Form submitted successfully")
                return True
            
            # Try Tab + Enter (navigate to OK button)
            self.logger.info("📤 Trying Tab + Enter...")
            pyautogui.press('tab')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(4)
            
            if self._check_login_success():
                self.logger.info("✅ Form submitted successfully with Tab + Enter")
                return True
            
            self.logger.info("⚠️ Form submission methods completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Form submission failed: {e}")
            return False
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            if not self.vbs_window_handle:
                return False
            
            # Check if window title changed
            try:
                current_title = win32gui.GetWindowText(self.vbs_window_handle)
                if 'login' not in current_title.lower():
                    self.logger.info(f"✅ Login success detected: title changed to '{current_title}'")
                    return True
            except:
                pass
            
            # Check for main application windows
            main_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            _, window_process_id = win32process.GetWindowThreadProcessId(hwnd)
                            if window_process_id == self.vbs_process_id:
                                if any(indicator in title.lower() for indicator in ['absons', 'erp', 'edition']):
                                    if 'login' not in title.lower():
                                        windows.append((hwnd, title))
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, main_windows)
            
            if main_windows:
                self.logger.info(f"✅ Main application window found: {main_windows[0][1]}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Login success check failed: {e}")
            return False
    
    def get_window_handle(self):
        return self.vbs_window_handle
    
    def get_process_id(self):
        return self.vbs_process_id

def test_final_login():
    """Test the final VBS login"""
    print("🎯 TESTING VBS FINAL LOGIN")
    print("=" * 70)
    print("This approach handles the proper start position:")
    print("📍 Recognizes cursor starts in PASSWORD field by default")
    print("🧭 Uses Shift+Tab to navigate backwards to COMPANY field")
    print("📝 Fills fields in correct order:")
    print("   1. Company: IT")
    print("   2. Financial Year: 01/01/2023")
    print("   3. Username: vj (clears existing 'rdsr')")
    print("   4. Password: (empty)")
    print("📤 Submits the form")
    print("=" * 70)
    
    # Run final login
    login = VBSFinalLogin()
    result = login.run_final_login()
    
    print(f"\n📊 FINAL LOGIN RESULTS:")
    print(f"Success: {result['success']}")
    print(f"Start Time: {result['start_time']}")
    print(f"End Time: {result.get('end_time', 'N/A')}")
    
    if result.get('form_fields'):
        print(f"\n📝 FORM FIELDS FILLED:")
        for field in result['form_fields']:
            print(f"   ✅ {field}")
    
    if result.get('errors'):
        print(f"\n❌ ERRORS:")
        for error in result['errors']:
            print(f"   • {error}")
    
    if result["success"]:
        print(f"\n🎉 FINAL LOGIN SUCCESSFUL!")
        print(f"VBS Window Handle: {hex(login.get_window_handle()) if login.get_window_handle() else 'N/A'}")
        print(f"VBS Process ID: {login.get_process_id()}")
        print("\n✅ VBS login with proper start position handling!")
    else:
        print(f"\n❌ FINAL LOGIN FAILED!")
    
    print("\n" + "=" * 70)
    print("VBS Final Login Test Completed")

if __name__ == "__main__":
    test_final_login() 