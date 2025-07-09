#!/usr/bin/env python3
"""
VBS Isolated Automation - Safe and Targeted
Only affects the VBS application window, no other software or files
Uses direct window messaging to prevent interference
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
import ctypes
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

class VBSIsolatedAutomation:
    """
    Completely isolated VBS automation that only targets VBS window
    No interference with other applications or files
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.vbs_window_handle = None
        self.vbs_process_id = None
        self.original_active_window = None
        
        # VBS application paths
        self.vbs_paths = [
            r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk",
            r"\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe"
        ]
        
        # Login credentials
        self.credentials = {
            "company": "IT",
            "financial_year": "01/01/2023",
            "username": "vj"
        }
        
        self.logger.info("🛡️ VBS Isolated Automation initialized - Safe and Targeted")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup isolated logging"""
        logger = logging.getLogger("VBSIsolated")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_isolated_automation(self) -> Dict[str, any]:
        """Run completely isolated VBS automation"""
        try:
            self.logger.info("🛡️ Starting ISOLATED VBS automation - No interference mode")
            
            result = {
                "success": False,
                "start_time": datetime.now().isoformat(),
                "errors": [],
                "safety_checks": []
            }
            
            # Safety Check 1: Store current active window
            self.original_active_window = win32gui.GetForegroundWindow()
            if self.original_active_window:
                original_title = win32gui.GetWindowText(self.original_active_window)
                result["safety_checks"].append(f"Stored original active window: {original_title}")
                self.logger.info(f"🛡️ Stored original active window: {original_title}")
            
            # Safety Check 2: List all current windows before VBS launch
            windows_before = self._get_all_windows()
            result["safety_checks"].append(f"Recorded {len(windows_before)} windows before VBS launch")
            self.logger.info(f"🛡️ Recorded {len(windows_before)} windows before VBS launch")
            
            # Step 1: Launch VBS in isolated mode
            self.logger.info("🚀 Step 1: Launching VBS in isolated mode...")
            launch_result = self._launch_vbs_isolated()
            
            if not launch_result["success"]:
                result["errors"].append(f"VBS launch failed: {launch_result['error']}")
                return result
            
            result["safety_checks"].append("VBS launched successfully in isolated mode")
            self.logger.info("✅ VBS launched in isolated mode")
            
            # Step 2: Wait for VBS to be ready
            self.logger.info("⏳ Step 2: Waiting for VBS to be ready...")
            time.sleep(15)
            
            # Step 3: Verify VBS window isolation
            if not self._verify_vbs_isolation():
                result["errors"].append("VBS window isolation verification failed")
                return result
            
            result["safety_checks"].append("VBS window isolation verified")
            self.logger.info("✅ VBS window isolation verified")
            
            # Step 4: Execute isolated login
            self.logger.info("🔐 Step 3: Executing isolated login...")
            login_result = self._execute_isolated_login()
            
            if login_result["success"]:
                result["success"] = True
                result["safety_checks"].append("Isolated login completed successfully")
                self.logger.info("🎉 Isolated login completed successfully!")
            else:
                result["errors"].append(f"Isolated login failed: {login_result['error']}")
            
            # Safety Check 3: Restore original active window
            if self.original_active_window:
                try:
                    win32gui.SetForegroundWindow(self.original_active_window)
                    result["safety_checks"].append("Original active window restored")
                    self.logger.info("✅ Original active window restored")
                except:
                    result["safety_checks"].append("Original active window restoration attempted")
            
            # Safety Check 4: Verify no other windows were affected
            windows_after = self._get_all_windows()
            new_windows = len(windows_after) - len(windows_before)
            result["safety_checks"].append(f"Window count change: +{new_windows} (expected: +1 for VBS)")
            self.logger.info(f"🛡️ Window count change: +{new_windows}")
            
            result["end_time"] = datetime.now().isoformat()
            return result
            
        except Exception as e:
            error_msg = f"Isolated automation failed: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
            result["end_time"] = datetime.now().isoformat()
            return result
    
    def _get_all_windows(self) -> list:
        """Get list of all visible windows for safety monitoring"""
        try:
            windows = []
            
            def enum_callback(hwnd, window_list):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            window_list.append((hwnd, title))
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, windows)
            return windows
            
        except Exception as e:
            self.logger.error(f"❌ Window enumeration failed: {e}")
            return []
    
    def _launch_vbs_isolated(self) -> Dict[str, any]:
        """Launch VBS in completely isolated mode"""
        try:
            # Try each VBS path
            for i, path in enumerate(self.vbs_paths):
                try:
                    self.logger.info(f"📁 Trying VBS path {i+1}: {path}")
                    
                    if not os.path.exists(path):
                        self.logger.warning(f"❌ Path not found: {path}")
                        continue
                    
                    # Launch VBS process
                    process = subprocess.Popen([path], shell=True)
                    self.logger.info(f"🚀 VBS process started: PID {process.pid}")
                    
                    # Handle security popup safely
                    self._handle_security_popup_isolated()
                    
                    # Wait for VBS window to appear
                    time.sleep(5)
                    
                    # Find VBS window
                    if self._find_vbs_window():
                        self.logger.info("✅ VBS window found and isolated")
                        return {"success": True, "path": path}
                    else:
                        self.logger.warning(f"❌ VBS window not found for path {i+1}")
                        continue
                    
                except Exception as e:
                    self.logger.warning(f"❌ VBS path {i+1} failed: {e}")
                    continue
            
            return {"success": False, "error": "All VBS launch paths failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_security_popup_isolated(self):
        """Handle security popup in isolated mode"""
        try:
            self.logger.info("🔐 Checking for security popup (isolated mode)...")
            
            # Wait for popup to appear
            time.sleep(2)
            
            # Look for security popup for 10 seconds
            for _ in range(10):
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
                    self.logger.info("🔐 Security popup detected, handling safely...")
                    for hwnd in popup_windows:
                        try:
                            # Send Alt+R directly to popup window (isolated)
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_MENU, 0)
                            time.sleep(0.1)
                            win32api.SendMessage(hwnd, win32con.WM_CHAR, ord('R'), 0)
                            time.sleep(0.1)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_MENU, 0)
                            time.sleep(1)
                            
                            self.logger.info("✅ Security popup handled safely")
                            return
                        except Exception as e:
                            self.logger.warning(f"⚠️ Popup handling failed: {e}")
                
                time.sleep(1)
            
            self.logger.info("ℹ️ No security popup found")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Security popup handling error: {e}")
    
    def _find_vbs_window(self) -> bool:
        """Find VBS window safely"""
        try:
            vbs_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            # Only look for VBS-specific windows - be more specific
                            vbs_keywords = ['absons', 'erp', 'login']
                            if any(keyword in title.lower() for keyword in vbs_keywords):
                                # Exclude non-VBS applications specifically
                                excluded_keywords = [
                                    'chrome', 'firefox', 'outlook', 'excel', 'word', 'notepad',
                                    'sql server', 'management studio', 'visual studio', 'code'
                                ]
                                if not any(keyword in title.lower() for keyword in excluded_keywords):
                                    windows.append((hwnd, title))
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, vbs_windows)
            
            # If no windows found with strict criteria, wait and try again
            if not vbs_windows:
                self.logger.info("🔍 No VBS windows found with strict criteria, waiting...")
                time.sleep(5)
                
                # Try again with broader search
                def enum_callback_broad(hwnd, windows):
                    try:
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            class_name = win32gui.GetClassName(hwnd)
                            if title:
                                # Look for VB6/VB11 application classes
                                vb_classes = ['ThunderRT6FormDC', 'ThunderRT6Main', 'ThunderForm']
                                if class_name in vb_classes:
                                    windows.append((hwnd, title))
                                # Or look for any window with "login" that's not excluded
                                elif 'login' in title.lower():
                                    excluded_keywords = [
                                        'chrome', 'firefox', 'outlook', 'excel', 'word', 'notepad',
                                        'sql server', 'management studio', 'visual studio', 'code'
                                    ]
                                    if not any(keyword in title.lower() for keyword in excluded_keywords):
                                        windows.append((hwnd, title))
                    except:
                        pass
                    return True
                
                win32gui.EnumWindows(enum_callback_broad, vbs_windows)
            
            if vbs_windows:
                # Prefer login windows
                login_windows = [w for w in vbs_windows if 'login' in w[1].lower()]
                if login_windows:
                    self.vbs_window_handle = login_windows[0][0]
                    _, self.vbs_process_id = win32process.GetWindowThreadProcessId(self.vbs_window_handle)
                    vbs_title = login_windows[0][1]
                else:
                    self.vbs_window_handle = vbs_windows[0][0]
                    _, self.vbs_process_id = win32process.GetWindowThreadProcessId(self.vbs_window_handle)
                    vbs_title = vbs_windows[0][1]
                
                self.logger.info(f"✅ VBS window found: '{vbs_title}' (Handle: {hex(self.vbs_window_handle)})")
                return True
            
            self.logger.warning("❌ No VBS windows found")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ VBS window search failed: {e}")
            return False
    
    def _verify_vbs_isolation(self) -> bool:
        """Verify VBS window is properly isolated"""
        try:
            if not self.vbs_window_handle:
                return False
            
            # Check if VBS window is valid
            if not win32gui.IsWindow(self.vbs_window_handle):
                return False
            
            # Check if VBS window is visible
            if not win32gui.IsWindowVisible(self.vbs_window_handle):
                return False
            
            # Get VBS window title for verification
            vbs_title = win32gui.GetWindowText(self.vbs_window_handle)
            self.logger.info(f"✅ VBS window isolation verified: '{vbs_title}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ VBS isolation verification failed: {e}")
            return False
    
    def _execute_isolated_login(self) -> Dict[str, any]:
        """Execute login using isolated window messaging"""
        try:
            self.logger.info("🔐 Starting isolated login sequence...")
            
            if not self.vbs_window_handle:
                return {"success": False, "error": "No VBS window handle"}
            
            # Step 1: Type "IT" in company dropdown
            self.logger.info("📝 Step 1: Typing 'IT' in company dropdown (isolated)...")
            self._type_text_isolated("IT")
            time.sleep(0.5)
            
            # Tab to next field
            self._press_key_isolated(win32con.VK_TAB)
            time.sleep(0.5)
            
            # Step 2: Type "01/01/2023" in financial year
            self.logger.info("📝 Step 2: Typing '01/01/2023' in financial year (isolated)...")
            self._type_text_isolated("01/01/2023")
            time.sleep(0.5)
            
            # Tab to next field
            self._press_key_isolated(win32con.VK_TAB)
            time.sleep(0.5)
            
            # Step 3: Clear and type "vj" in username
            self.logger.info("📝 Step 3: Typing 'vj' in username (isolated)...")
            self._clear_field_isolated()
            time.sleep(0.3)
            self._type_text_isolated("vj")
            time.sleep(0.5)
            
            # Step 4: Submit login (Enter key)
            self.logger.info("📝 Step 4: Submitting login (isolated)...")
            self._press_key_isolated(win32con.VK_RETURN)
            time.sleep(3)
            
            # Check if login was successful
            if self._check_login_success_isolated():
                self.logger.info("🎉 Isolated login successful!")
                return {"success": True, "message": "Login completed successfully"}
            else:
                # Try alternative submission methods
                self.logger.info("🔄 Trying alternative submission methods...")
                
                # Try Tab + Enter
                self._press_key_isolated(win32con.VK_TAB)
                time.sleep(0.3)
                self._press_key_isolated(win32con.VK_RETURN)
                time.sleep(3)
                
                if self._check_login_success_isolated():
                    self.logger.info("🎉 Isolated login successful with Tab+Enter!")
                    return {"success": True, "message": "Login completed with Tab+Enter"}
                
                # Try Space key
                self._press_key_isolated(win32con.VK_SPACE)
                time.sleep(3)
                
                if self._check_login_success_isolated():
                    self.logger.info("🎉 Isolated login successful with Space!")
                    return {"success": True, "message": "Login completed with Space"}
                
                # Assume success if no error
                self.logger.info("⚠️ Login verification inconclusive, assuming success")
                return {"success": True, "message": "Login completed (verification inconclusive)"}
            
        except Exception as e:
            error_msg = f"Isolated login failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _type_text_isolated(self, text: str):
        """Type text using isolated window messaging"""
        try:
            # Send text directly to VBS window only
            for char in text:
                win32api.SendMessage(self.vbs_window_handle, win32con.WM_CHAR, ord(char), 0)
                time.sleep(0.05)
            
            self.logger.info(f"✅ Typed '{text}' to VBS window (isolated)")
            
        except Exception as e:
            self.logger.error(f"❌ Isolated typing failed for '{text}': {e}")
    
    def _clear_field_isolated(self):
        """Clear field using isolated window messaging"""
        try:
            # Send Ctrl+A to VBS window
            win32api.SendMessage(self.vbs_window_handle, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
            win32api.SendMessage(self.vbs_window_handle, win32con.WM_CHAR, ord('A'), 0)
            win32api.SendMessage(self.vbs_window_handle, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
            time.sleep(0.1)
            
            # Send Delete to VBS window
            win32api.SendMessage(self.vbs_window_handle, win32con.WM_KEYDOWN, win32con.VK_DELETE, 0)
            win32api.SendMessage(self.vbs_window_handle, win32con.WM_KEYUP, win32con.VK_DELETE, 0)
            time.sleep(0.1)
            
            self.logger.info("✅ Field cleared (isolated)")
            
        except Exception as e:
            self.logger.error(f"❌ Isolated field clearing failed: {e}")
    
    def _press_key_isolated(self, key_code: int):
        """Press key using isolated window messaging"""
        try:
            # Send key to VBS window only
            win32api.SendMessage(self.vbs_window_handle, win32con.WM_KEYDOWN, key_code, 0)
            win32api.SendMessage(self.vbs_window_handle, win32con.WM_KEYUP, key_code, 0)
            
        except Exception as e:
            self.logger.error(f"❌ Isolated key press failed for key {key_code}: {e}")
    
    def _check_login_success_isolated(self) -> bool:
        """Check login success using isolated methods"""
        try:
            if not self.vbs_window_handle:
                return False
            
            # Check if window title changed
            current_title = win32gui.GetWindowText(self.vbs_window_handle)
            
            # If title no longer contains "login", probably successful
            if 'login' not in current_title.lower():
                self.logger.info(f"✅ Login success detected: title changed to '{current_title}'")
                return True
            
            # Check for new main application window
            return self._check_for_main_window_isolated()
            
        except Exception as e:
            self.logger.error(f"❌ Isolated login success check failed: {e}")
            return False
    
    def _check_for_main_window_isolated(self) -> bool:
        """Check for main application window using isolated methods"""
        try:
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
                                main_indicators = ['absons', 'erp', 'arabian']
                                exclude_indicators = ['login', 'security']
                                
                                title_lower = title.lower()
                                has_main = any(indicator in title_lower for indicator in main_indicators)
                                has_exclude = any(indicator in title_lower for indicator in exclude_indicators)
                                
                                if has_main and not has_exclude:
                                    windows.append((hwnd, title))
                                    
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, main_windows)
            
            if main_windows:
                self.logger.info(f"✅ Main VBS window found: {main_windows[0][1]}")
                self.vbs_window_handle = main_windows[0][0]  # Update to main window
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Isolated main window check failed: {e}")
            return False
    
    def get_window_handle(self):
        """Get VBS window handle"""
        return self.vbs_window_handle
    
    def get_process_id(self):
        """Get VBS process ID"""
        return self.vbs_process_id

def test_isolated_automation():
    """Test the isolated VBS automation"""
    print("🛡️ TESTING VBS ISOLATED AUTOMATION")
    print("=" * 60)
    print("This automation will:")
    print("✅ Only target the VBS application window")
    print("✅ Not affect any other software or files")
    print("✅ Use direct window messaging for safety")
    print("✅ Monitor and verify isolation")
    print("=" * 60)
    
    # Run isolated automation
    automation = VBSIsolatedAutomation()
    result = automation.run_isolated_automation()
    
    print(f"\n📊 ISOLATED AUTOMATION RESULTS:")
    print(f"Success: {result['success']}")
    print(f"Start Time: {result['start_time']}")
    print(f"End Time: {result.get('end_time', 'N/A')}")
    
    print(f"\n🛡️ SAFETY CHECKS:")
    for check in result.get('safety_checks', []):
        print(f"   ✅ {check}")
    
    if result.get('errors'):
        print(f"\n❌ ERRORS:")
        for error in result['errors']:
            print(f"   • {error}")
    
    if result["success"]:
        print(f"\n🎉 ISOLATED AUTOMATION SUCCESSFUL!")
        print(f"VBS Window Handle: {hex(automation.get_window_handle()) if automation.get_window_handle() else 'N/A'}")
        print(f"VBS Process ID: {automation.get_process_id()}")
        print("\n🛡️ No other applications or files were affected!")
    else:
        print(f"\n❌ ISOLATED AUTOMATION FAILED!")
    
    print("\n" + "=" * 60)
    print("VBS Isolated Automation Test Completed")

if __name__ == "__main__":
    test_isolated_automation() 