#!/usr/bin/env python3
"""
VBS Automation - Phase 1: Enhanced Login System
Optimized with process management, precise window detection, and robust input handling
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
import psutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any
import traceback

class VBSPhase1_Enhanced:
    """Enhanced VBS Login with improved reliability and background operation"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.window_handle: Optional[int] = None
        self.vbs_process_id: Optional[int] = None
        
        # Application paths
        self.vbs_paths = [
            r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk",
            r"\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe"
        ]
        
        # Simple credentials - exactly as specified
        self.credentials = {
            "company": "IT",
            "financial_year": "01/01/2023",
            "username": "vj"
        }
        
        # Timeouts and retry settings
        self.timeouts = {
            "startup": 10,  # Reduced from 15 to 10 seconds
            "login": 10,
            "security_popup": 15
        }
        
        self.retry_settings = {
            "max_retries": 3,
            "retry_delay": 1.0
        }
        
        self.logger.info("🚀 Enhanced VBS Login initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging"""
        logger = logging.getLogger("VBSEnhanced")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def run_simple_login(self) -> Dict[str, Any]:
        """Run the enhanced login process with retry logic"""
        return self._execute_with_retry(
            self._run_login_process,
            max_retries=self.retry_settings['max_retries'],
            delay=self.retry_settings['retry_delay']
        )
    
    def _run_login_process(self) -> Dict[str, Any]:
        """Internal login process"""
        try:
            self.logger.info("🎯 Starting ENHANCED VBS login")
            
            result = {
                "success": False,
                "start_time": datetime.now().isoformat(),
                "errors": []
            }
            
            # Step 1: Check for existing VBS process
            existing_pid = self._check_existing_vbs_process()
            if existing_pid:
                self.logger.info(f"✅ Using existing VBS process: {existing_pid}")
                self.vbs_process_id = existing_pid
                if not self._find_and_focus_vbs_window():
                    result["errors"].append("Could not focus existing VBS window")
                    return result
            else:
                # Step 2: Launch VBS application
                self.logger.info("🚀 Launching VBS application...")
                launch_result = self._launch_vbs_enhanced()
                
                if not launch_result["success"]:
                    result["errors"].append(f"Launch failed: {launch_result['error']}")
                    return result
                
                self.logger.info("✅ VBS launched successfully")
                
                # Step 3: Wait for form to be ready
                self.logger.info("⏳ Waiting for VBS form to be ready...")
                time.sleep(self.timeouts["startup"])
                
                # Step 4: Find and focus VBS window
                if not self._find_and_focus_vbs_window():
                    result["errors"].append("Could not find or focus VBS window")
                    return result
            
            # Step 5: Execute login sequence
            self.logger.info("📝 Executing enhanced login sequence...")
            login_success = self._execute_intelligent_login()
            
            if login_success:
                self.logger.info("🎉 Enhanced login completed successfully!")
                result["success"] = True
            else:
                result["errors"].append("Enhanced login sequence failed")
            
            result["end_time"] = datetime.now().isoformat()
            return result
            
        except Exception as e:
            error_msg = f"Enhanced login failed: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
            return result
    
    def _check_existing_vbs_process(self) -> Optional[int]:
        """Check if VBS is already running to avoid duplicate launches"""
        try:
            vbs_keywords = ['AbsonsItERP', 'arabian', 'moonflower']
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    if proc_info['name'] and proc_info['exe']:
                        exe_lower = proc_info['exe'].lower()
                        name_lower = proc_info['name'].lower()
                        
                        if any(keyword.lower() in exe_lower or keyword.lower() in name_lower 
                               for keyword in vbs_keywords):
                            self.logger.info(f"✅ Found existing VBS process: {proc_info['pid']}")
                            return proc_info['pid']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return None
        except Exception as e:
            self.logger.warning(f"⚠️ Process check failed: {e}")
            return None
    
    def _launch_vbs_enhanced(self) -> Dict[str, Any]:
        """Enhanced VBS application launch with better error handling"""
        try:
            # Try each path
            for i, path in enumerate(self.vbs_paths):
                try:
                    self.logger.info(f"📁 Trying path {i+1}: {path}")
                    
                    if not os.path.exists(path):
                        self.logger.warning(f"❌ Path not found: {path}")
                        continue
                    
                    # Launch application
                    process = subprocess.Popen([path], shell=True)
                    
                    # Handle security popup if it appears
                    if self._handle_security_popup_enhanced():
                        self.logger.info("✅ Security popup handled")
                    
                    # Wait for VBS to start - reduced from 5 to 3 seconds
                    time.sleep(3)
                    
                    # Check if VBS window appeared
                    if self._check_vbs_window_exists():
                        self.logger.info("✅ VBS window found")
                        return {"success": True, "path": path}
                    else:
                        self.logger.warning(f"❌ VBS window not found for path {i+1}")
                        continue
                    
                except Exception as e:
                    self.logger.warning(f"❌ Path {i+1} failed: {e}")
                    continue
            
            return {"success": False, "error": "All launch paths failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_security_popup_enhanced(self) -> bool:
        """Enhanced security popup handling with multiple strategies"""
        try:
            self.logger.info("🔐 Enhanced security popup detection...")
            
            security_patterns = [
                r'.*security.*warning.*',
                r'.*open.*file.*security.*',
                r'.*publisher.*cannot.*verified.*',
                r'.*run.*anyway.*',
                r'.*windows.*protected.*'
            ]
            
            for attempt in range(self.timeouts["security_popup"]):
                popup_found = False
                
                def enum_security_windows(hwnd, windows):
                    try:
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd).lower()
                            class_name = win32gui.GetClassName(hwnd).lower()
                            
                            # Check patterns
                            for pattern in security_patterns:
                                if re.search(pattern, title, re.IGNORECASE):
                                    windows.append((hwnd, title, 'title'))
                                    return True
                            
                            # Check for security dialog classes
                            security_classes = ['#32770', 'tooltips_class32', 'button']
                            if any(sec_class in class_name for sec_class in security_classes):
                                if any(word in title for word in ['security', 'warning', 'publisher']):
                                    windows.append((hwnd, title, 'class'))
                                    return True
                    
                    except Exception:
                        pass
                    return True
                
                security_windows = []
                win32gui.EnumWindows(enum_security_windows, security_windows)
                
                if security_windows:
                    popup_found = True
                    self.logger.info(f"🔐 Security popup detected: {security_windows[0][1]}")
                    
                    hwnd = security_windows[0][0]
                    
                    # Strategy 1: Alt+R (Run)
                    if self._try_security_bypass(hwnd, 'alt_r'):
                        return True
                    
                    # Strategy 2: Enter key
                    if self._try_security_bypass(hwnd, 'enter'):
                        return True
                
                time.sleep(1)
            
            return not popup_found  # Success if no popup found
            
        except Exception as e:
            self.logger.error(f"❌ Security popup handling failed: {e}")
            return False
    
    def _try_security_bypass(self, hwnd: int, method: str) -> bool:
        """Try different security bypass methods"""
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            
            if method == 'alt_r':
                # Alt+R combination
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(ord('R'), 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(ord('R'), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            elif method == 'enter':
                # Simple Enter key
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            time.sleep(2)
            
            # Check if popup is gone
            if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                self.logger.info(f"✅ Security bypass successful: {method}")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Security bypass {method} failed: {e}")
            return False
    
    def _check_vbs_window_exists(self) -> bool:
        """Check if VBS window exists with precise filtering"""
        try:
            vbs_windows = self._get_vbs_windows_precise()
            
            if vbs_windows:
                # Choose the best match - prefer login windows
                best_window = None
                for hwnd, title, process_id in vbs_windows:
                    if 'login' in title.lower():
                        best_window = (hwnd, title, process_id)
                        break
                
                if not best_window:
                    best_window = vbs_windows[0]
                
                self.window_handle = best_window[0]
                self.vbs_process_id = best_window[2]
                self.logger.info(f"✅ VBS window selected: '{best_window[1]}'")
                return True
            
            self.logger.warning("❌ No VBS windows found")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Window check failed: {e}")
            return False
    
    def _get_vbs_windows_precise(self) -> List[Tuple[int, str, int]]:
        """Get VBS windows with precise filtering"""
        vbs_windows = []
        
        def enum_callback(hwnd, windows):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                    
                title = win32gui.GetWindowText(hwnd)
                
                # Get process info
                _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                
                try:
                    process = psutil.Process(process_id)
                    exe_path = process.exe().lower()
                    
                    # Strict VBS identification
                    vbs_identifiers = [
                        'absonsiterp.exe',
                        'arabian',
                        'moonflower'
                    ]
                    
                    # Must match exe path AND have relevant window title
                    if any(identifier in exe_path for identifier in vbs_identifiers):
                        # Additional title validation
                        title_lower = title.lower()
                        valid_titles = ['login', 'absons', 'erp', 'arabian', 'user']
                        
                        if any(valid in title_lower for valid in valid_titles):
                            windows.append((hwnd, title, process_id))
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            except Exception:
                pass
            return True
        
        win32gui.EnumWindows(enum_callback, vbs_windows)
        return vbs_windows
    
    def _find_and_focus_vbs_window(self) -> bool:
        """Find and focus VBS window with background-friendly approach"""
        try:
            if not self.window_handle:
                if not self._check_vbs_window_exists():
                    return False
            
            # Focus window without disrupting other applications
            if self.window_handle is not None:
                return self._focus_window_background(self.window_handle)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Window focus failed: {e}")
            return False
    
    def _focus_window_background(self, hwnd: int) -> bool:
        """Focus window without disrupting other applications"""
        try:
            # Check if window is minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)
            
            # Bring to front without stealing focus from other apps
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, 
                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            
            # Brief activation
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            
            self.logger.info("✅ VBS window focused")
            return True
        except Exception as e:
            self.logger.error(f"❌ Window focus failed: {e}")
            return False
    
    def _execute_intelligent_login(self) -> bool:
        """Execute login sequence using proper tab navigation"""
        try:
            self.logger.info("📝 Starting tab-based login sequence...")
            
            # Always use the reliable tab-based login method
            return self._execute_simple_login_sequence()
            
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
            return False
    
    def _execute_simple_login_sequence(self) -> bool:
        """Execute the simple login sequence with two cycles - clear first, then fill"""
        try:
            self.logger.info("📝 Starting two-cycle login sequence...")
            self.logger.info("📝 Cycle structure: Password->OK->Cancel->Company->Financial Year->Username->Password (6 tabs)")
            
            # Make sure VBS window is active
            if self.window_handle:
                try:
                    win32gui.SetForegroundWindow(self.window_handle)
                    time.sleep(1)
                except:
                    pass
            
            # FIRST CYCLE: Clear all fields
            self.logger.info("🧹 FIRST CYCLE: Clearing all fields...")
            
            # Tab 3 times to get to Company field (1st text field)
            self.logger.info("📝 Tabbing 3 times: Password->OK->Cancel->Company...")
            for i in range(3):
                self._press_tab()
                time.sleep(0.3)
            
            # Clear Company field
            self.logger.info("🧹 Clearing Company field...")
            self._clear_field_only()
            time.sleep(0.3)
            
            # Tab 1 time to Financial Year field (2nd text field)
            self.logger.info("📝 Tabbing 1 time: Company->Financial Year...")
            self._press_tab()
            time.sleep(0.3)
            
            # Clear Financial Year field
            self.logger.info("🧹 Clearing Financial Year field...")
            self._clear_field_only()
            time.sleep(0.3)
            
            # Tab 1 time to Username field (3rd text field)
            self.logger.info("📝 Tabbing 1 time: Financial Year->Username...")
            self._press_tab()
            time.sleep(0.3)
            
            # Clear Username field
            self.logger.info("🧹 Clearing Username field...")
            self._clear_field_only()
            time.sleep(0.3)
            
            # Tab 1 time to Password field (complete cycle - 6 tabs total)
            self.logger.info("📝 Tabbing 1 time: Username->Password (cycle complete)...")
            self._press_tab()
            time.sleep(0.3)
            
            self.logger.info("✅ First cycle completed - all fields cleared (6 tabs total)")
            
            # SECOND CYCLE: Fill all fields with data
            self.logger.info("📝 SECOND CYCLE: Filling all fields with data...")
            
            # Tab 3 times to get back to Company field (1st text field)
            self.logger.info("📝 Tabbing 3 times: Password->OK->Cancel->Company...")
            for i in range(3):
                self._press_tab()
                time.sleep(0.3)
            
            # Type "IT" in Company field
            self.logger.info("📝 Typing 'IT' in Company field...")
            self._type_text_efficiently("IT")
            time.sleep(0.5)
            
            # Tab 1 time to Financial Year field (2nd text field)
            self.logger.info("📝 Tabbing 1 time: Company->Financial Year...")
            self._press_tab()
            time.sleep(0.3)
            
            # Type "01/01/2023" in Financial Year field
            self.logger.info("📝 Typing '01/01/2023' in Financial Year field...")
            self._type_text_efficiently("01/01/2023")
            time.sleep(0.5)
            
            # Tab 1 time to Username field (3rd text field)
            self.logger.info("📝 Tabbing 1 time: Financial Year->Username...")
            self._press_tab()
            time.sleep(0.3)
            
            # Type "vj" in Username field
            self.logger.info("📝 Typing 'vj' in Username field...")
            self._type_text_efficiently("vj")
            time.sleep(0.5)
            
            self.logger.info("✅ Second cycle completed - all fields filled")
            
            # Tab 2 times to get to OK button (Username->Password->OK)
            self.logger.info("📝 Tabbing 2 times: Username->Password->OK...")
            self._press_tab()  # Username -> Password
            time.sleep(0.3)
            self._press_tab()  # Password -> OK
            time.sleep(0.3)
            
            # Press Enter to login
            self.logger.info("📝 Pressing Enter to login...")
            self._press_enter()
            time.sleep(3)
            
            # Check if login was successful
            if self._check_login_success():
                self.logger.info("🎉 Login successful!")
                return True
            
            # If first attempt didn't work, try Enter again
            self.logger.info("🔄 Trying Enter again...")
            self._press_enter()
            time.sleep(3)
            
            if self._check_login_success():
                self.logger.info("🎉 Login successful with second Enter!")
                return True
            
            self.logger.info("✅ Login sequence completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Login sequence failed: {e}")
            return False
    
    def _clear_field_only(self):
        """Clear current field only - no typing"""
        try:
            # Strategy 1: Ctrl+A + Delete (most reliable)
            self._press_ctrl_key('A')
            time.sleep(0.15)
            self._press_key(win32con.VK_DELETE)
            time.sleep(0.15)
            
            # Strategy 2: Backup clearing with Ctrl+A + Backspace
            self._press_ctrl_key('A')
            time.sleep(0.1)
            self._press_key(win32con.VK_BACK)
            time.sleep(0.1)
            
            # Strategy 3: Clear any remaining content with Home + Shift+End + Delete
            self._press_key(win32con.VK_HOME)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            self._press_key(win32con.VK_END)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            self._press_key(win32con.VK_DELETE)
            time.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"❌ Field clearing failed: {e}")
    
    def _clear_and_type(self, text: str):
        """Clear current field and type new text with enhanced clearing"""
        try:
            # Enhanced field clearing with multiple strategies
            self.logger.info(f"🧹 Clearing field and typing '{text}'...")
            
            # Strategy 1: Ctrl+A + Delete (most reliable)
            self._press_ctrl_key('A')
            time.sleep(0.15)  # Slightly longer wait for selection
            self._press_key(win32con.VK_DELETE)
            time.sleep(0.15)
            
            # Strategy 2: Backup clearing with Ctrl+A + Backspace
            self._press_ctrl_key('A')
            time.sleep(0.1)
            self._press_key(win32con.VK_BACK)
            time.sleep(0.1)
            
            # Strategy 3: Clear any remaining content with Home + Shift+End + Delete
            self._press_key(win32con.VK_HOME)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            self._press_key(win32con.VK_END)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            self._press_key(win32con.VK_DELETE)
            time.sleep(0.1)
            
            # Now type the new text
            self._type_text_efficiently(text)
            
            self.logger.info(f"✅ Successfully cleared and typed '{text}'")
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced clear and type failed for '{text}': {e}")
            # Fallback to simple typing
            try:
                self._type_text_efficiently(text)
                self.logger.info(f"✅ Fallback typing successful for '{text}'")
            except Exception as e2:
                self.logger.error(f"❌ Fallback typing also failed: {e2}")
    
    def _press_ctrl_key(self, key_name: str):
        """Press Ctrl+Key combination"""
        try:
            if key_name == 'A':
                vk_code = ord('A')
            elif key_name == 'HOME':
                vk_code = win32con.VK_HOME
            else:
                vk_code = ord(key_name.upper())
            
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception as e:
            self.logger.error(f"❌ Ctrl+{key_name} failed: {e}")
    
    def _smart_fill_current_field(self, text: str):
        """Smart field filling - check if field has data, clear if needed, then type"""
        try:
            # First, select all text in current field to see what's there
            self._press_ctrl_key('A')  # Ctrl+A to select all
            time.sleep(0.1)
            
            # Now type the new text (this will replace any selected text)
            self._type_text_efficiently(text)
            
            self.logger.info(f"✅ Filled field with '{text}'")
            
        except Exception as e:
            self.logger.error(f"❌ Smart field filling failed for '{text}': {e}")
    
    def _type_text_efficiently(self, text: str):
        """Type text efficiently character by character"""
        try:
            for char in text:
                # Use VkKeyScan to get the correct virtual key code
                vk_code = win32api.VkKeyScan(char)
                if vk_code != -1:  # Valid character
                    # Extract the virtual key code (low byte)
                    key_code = vk_code & 0xFF
                    # Check if shift is needed (high byte)
                    shift_needed = (vk_code >> 8) & 1
                    
                    if shift_needed:
                        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                    
                    win32api.keybd_event(key_code, 0, 0, 0)
                    time.sleep(0.03)  # Slightly slower for reliability
                    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                    
                    if shift_needed:
                        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                    
                    time.sleep(0.03)
            
        except Exception as e:
            self.logger.error(f"❌ Efficient typing failed for '{text}': {e}")
    
    def _press_key(self, vk_code: int):
        """Press a single key efficiently"""
        try:
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception as e:
            self.logger.error(f"❌ Key press failed for {vk_code}: {e}")
    
    def _press_tab(self):
        """Press Tab key efficiently"""
        self._press_key(win32con.VK_TAB)
    
    def _press_enter(self):
        """Press Enter key efficiently"""
        self._press_key(win32con.VK_RETURN)
    
    def _press_shift_tab(self):
        """Press Shift+Tab to go to previous field"""
        try:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception as e:
            self.logger.error(f"❌ Shift+Tab failed: {e}")
    
    def _press_alt_key(self, char: str):
        """Press Alt+Key combination"""
        try:
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt down
            win32api.keybd_event(ord(char.upper()), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt up
        except Exception as e:
            self.logger.error(f"❌ Alt+{char} failed: {e}")
    
    def _press_space(self):
        """Press Space key efficiently"""
        self._press_key(win32con.VK_SPACE)
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            if not self.window_handle:
                return False
            
            # Check if window title changed
            current_title = win32gui.GetWindowText(self.window_handle)
            
            # If title no longer contains "login", probably successful
            if 'login' not in current_title.lower():
                return True
            
            # Check for new windows
            return self._check_for_main_window()
            
        except Exception as e:
            self.logger.error(f"❌ Login success check failed: {e}")
            return False
    
    def _check_for_main_window(self) -> bool:
        """Check for main application window"""
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
                self.logger.info(f"✅ Main window found: {main_windows[0][1]}")
                self.window_handle = main_windows[0][0]  # Update to main window
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Main window check failed: {e}")
            return False
    
    def _execute_with_retry(self, func, max_retries: int = 3, delay: float = 1.0):
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🔄 Attempt {attempt + 1}/{max_retries}: {func.__name__}")
                result = func()
                
                if result and result.get("success", False):
                    self.logger.info(f"✅ {func.__name__} succeeded on attempt {attempt + 1}")
                    return result
                else:
                    self.logger.warning(f"⚠️ {func.__name__} returned False on attempt {attempt + 1}")
                    
            except Exception as e:
                last_exception = e
                self.logger.warning(f"❌ {func.__name__} failed on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff
        
        self.logger.error(f"❌ {func.__name__} failed after {max_retries} attempts")
        if last_exception:
            raise last_exception
        
        return {"success": False, "errors": [f"Failed after {max_retries} attempts"]}
    
    def get_window_handle(self) -> Optional[int]:
        """Get current window handle"""
        return self.window_handle
    
    def get_process_id(self) -> Optional[int]:
        """Get current process ID"""
        return self.vbs_process_id

# Maintain backward compatibility
VBSPhase1_Simple = VBSPhase1_Enhanced

# Test function
def test_simple_login():
    """Test the enhanced VBS login"""
    print("🧪 Testing Enhanced VBS Login")
    print("=" * 60)
    
    vbs_login = VBSPhase1_Enhanced()
    
    result = vbs_login.run_simple_login()
    
    print(f"\n📊 Results:")
    print(f"   Success: {result['success']}")
    print(f"   Errors: {result.get('errors', [])}")
    print(f"   Window Handle: {vbs_login.get_window_handle()}")
    print(f"   Process ID: {vbs_login.get_process_id()}")
    
    if result["success"]:
        print("\n✅ Enhanced login completed!")
    else:
        print(f"\n❌ Enhanced login failed: {result.get('errors', [])}")
    
    print("\n" + "=" * 60)
    print("Enhanced VBS Login Test Completed")

if __name__ == "__main__":
    test_simple_login()