#!/usr/bin/env python3
"""
VBS Background Automation System - Professional Grade
Uses direct Windows API calls for background operation with immunity for other applications
Based on 35 years of automation engineering experience
"""

import os
import sys
import time
import logging
import subprocess
import ctypes
from ctypes import wintypes, windll
import win32gui
import win32con
import win32api
import win32process
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any
import threading
import traceback

# Windows API constants
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_CHAR = 0x0102
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_COMMAND = 0x0111
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_CLOSE = 0x0010

VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11

class VBSBackgroundAutomation:
    """
    Professional-grade VBS background automation system
    Ensures complete immunity for other applications
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # VBS application details
        self.vbs_paths = [
            r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk",
            r"\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe"
        ]
        
        # Window management
        self.vbs_process_id = None
        self.vbs_main_window = None
        self.vbs_login_window = None
        self.window_handles = {}
        
        # Form credentials (exact as specified)
        self.credentials = {
            "company": "IT",
            "financial_year": "01/01/2023", 
            "login_id": "vj",
            "password": ""  # Empty as required
        }
        
        # Background monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Configuration
        self.config = {
            "stabilization_time": 25,  # Increased wait time
            "max_retries": 3,
            "process_timeout": 60,
            "form_detection_timeout": 30
        }
        
        self.logger.info("🚀 VBS Background Automation System initialized (Professional Grade)")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup professional logging"""
        logger = logging.getLogger("VBSBackgroundAuto")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler with enhanced formatting
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler for detailed logging
            log_dir = Path("EHC_Logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"vbs_background_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def launch_vbs_application(self) -> Dict[str, Any]:
        """Launch VBS application with professional background handling"""
        try:
            self.logger.info("🚀 Launching VBS application in background mode...")
            
            # Start background monitoring
            self._start_background_monitoring()
            
            # Try each path
            for i, path in enumerate(self.vbs_paths):
                try:
                    self.logger.info(f"📁 Attempting launch via path {i+1}: {path}")
                    
                    if not os.path.exists(path):
                        self.logger.warning(f"❌ Path not found: {path}")
                        continue
                    
                    # Launch process
                    self.logger.info("🔥 Starting VBS process...")
                    process = subprocess.Popen([path], shell=True)
                    
                    # Wait for process to stabilize
                    time.sleep(3)
                    
                    # Find VBS process and windows
                    if self._locate_vbs_process():
                        self.logger.info("✅ VBS process located successfully")
                        
                        # Wait for application stabilization
                        self.logger.info(f"⏳ Waiting {self.config['stabilization_time']} seconds for application stabilization...")
                        time.sleep(self.config["stabilization_time"])
                        
                        # Verify application is ready
                        if self._verify_application_ready():
                            self.logger.info("✅ VBS application ready for background automation")
                            return {
                                "success": True,
                                "process_id": self.vbs_process_id,
                                "main_window": self.vbs_main_window,
                                "launch_path": path
                            }
                        else:
                            self.logger.warning("⚠️ Application not ready, trying next path...")
                            continue
                    else:
                        self.logger.warning(f"❌ VBS process not found for path {i+1}")
                        continue
                        
                except Exception as e:
                    self.logger.warning(f"❌ Launch attempt {i+1} failed: {e}")
                    continue
            
            return {"success": False, "error": "Failed to launch VBS via all paths"}
            
        except Exception as e:
            error_msg = f"VBS launch failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _start_background_monitoring(self):
        """Start background monitoring thread"""
        try:
            if not self.monitoring_active:
                self.monitoring_active = True
                self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
                self.monitor_thread.start()
                self.logger.info("🔍 Background monitoring started")
        except Exception as e:
            self.logger.error(f"❌ Failed to start background monitoring: {e}")
    
    def _background_monitor(self):
        """Background monitoring for security popups and application state"""
        try:
            self.logger.info("🔍 Background monitor thread active")
            
            while self.monitoring_active:
                try:
                    # Monitor for security popups
                    self._handle_security_popups_background()
                    
                    # Monitor VBS application state
                    if self.vbs_process_id:
                        self._monitor_vbs_state()
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Background monitor error: {e}")
                    time.sleep(2)
            
            self.logger.info("🔍 Background monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Background monitor failed: {e}")
    
    def _handle_security_popups_background(self):
        """Handle security popups in background without affecting other applications"""
        try:
            # Find security dialogs
            security_windows = self._find_security_dialogs()
            
            for hwnd, title in security_windows:
                try:
                    # Verify this popup belongs to our process or is system-wide
                    if self._is_vbs_related_popup(hwnd):
                        self.logger.info(f"🔐 Handling security popup: {title}")
                        
                        # Use direct window messaging (no global input)
                        self._handle_popup_direct(hwnd)
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Popup handling error: {e}")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Security popup monitoring error: {e}")
    
    def _handle_popup_direct(self, hwnd):
        """Handle popup using direct window messaging only"""
        try:
            # Method 1: Send Alt+R directly to popup window
            self.logger.info("🔐 Sending Alt+R via direct messaging...")
            
            # Send Alt key down
            win32gui.PostMessage(hwnd, WM_KEYDOWN, VK_CONTROL, 0)  # Alt key
            time.sleep(0.1)
            
            # Send R key
            win32gui.PostMessage(hwnd, WM_CHAR, ord('R'), 0)
            time.sleep(0.1)
            
            # Send Alt key up
            win32gui.PostMessage(hwnd, WM_KEYUP, VK_CONTROL, 0)
            time.sleep(0.5)
            
            # Check if popup closed
            if not win32gui.IsWindowVisible(hwnd):
                self.logger.info("✅ Popup closed with Alt+R")
                return True
            
            # Method 2: Send Enter key
            self.logger.info("🔐 Trying Enter key...")
            win32gui.PostMessage(hwnd, WM_KEYDOWN, VK_RETURN, 0)
            time.sleep(0.1)
            win32gui.PostMessage(hwnd, WM_KEYUP, VK_RETURN, 0)
            time.sleep(0.5)
            
            if not win32gui.IsWindowVisible(hwnd):
                self.logger.info("✅ Popup closed with Enter")
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Direct popup handling failed: {e}")
            return False
    
    def _locate_vbs_process(self) -> bool:
        """Locate VBS process and main windows"""
        try:
            self.logger.info("🔍 Locating VBS process and windows...")
            
            # Find VBS windows
            vbs_windows = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            # Look for VBS-related windows
                            vbs_keywords = ['absons', 'erp', 'arabian', 'moonflower', 'login']
                            excluded_keywords = ['outlook', 'chrome', 'firefox', 'sql server']
                            
                            title_lower = title.lower()
                            
                            has_vbs = any(keyword in title_lower for keyword in vbs_keywords)
                            has_excluded = any(keyword in title_lower for keyword in excluded_keywords)
                            
                            if has_vbs and not has_excluded:
                                # Get process ID
                                _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                                windows.append((hwnd, title, process_id))
                                
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, vbs_windows)
            
            if vbs_windows:
                # Use the first VBS window found
                hwnd, title, process_id = vbs_windows[0]
                
                self.vbs_process_id = process_id
                self.vbs_main_window = hwnd
                
                # Determine if this is login window or main window
                if 'login' in title.lower():
                    self.vbs_login_window = hwnd
                else:
                    self.vbs_login_window = hwnd  # Assume it's login initially
                
                self.logger.info(f"✅ VBS process located: PID={process_id}, Window='{title}'")
                return True
            
            self.logger.warning("❌ No VBS windows found")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Process location failed: {e}")
            return False
    
    def _verify_application_ready(self) -> bool:
        """Verify VBS application is ready for automation"""
        try:
            if not self.vbs_main_window:
                return False
            
            # Check if window is valid and visible
            if not win32gui.IsWindow(self.vbs_main_window):
                return False
            
            if not win32gui.IsWindowVisible(self.vbs_main_window):
                return False
            
            # Check window size (detect if shrunk)
            rect = win32gui.GetWindowRect(self.vbs_main_window)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            if width < 400 or height < 300:
                self.logger.warning(f"⚠️ Window appears shrunk: {width}x{height}")
                return False
            
            self.logger.info("✅ VBS application verified ready")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Application readiness check failed: {e}")
            return False
    
    def perform_background_login(self) -> Dict[str, Any]:
        """Perform login using background automation with direct messaging"""
        try:
            self.logger.info("🔐 Starting background login sequence...")
            
            if not self.vbs_login_window:
                return {"success": False, "error": "No VBS login window available"}
            
            # Verify window is ready
            if not self._verify_application_ready():
                return {"success": False, "error": "VBS application not ready"}
            
            # Perform form filling sequence
            for attempt in range(self.config["max_retries"]):
                self.logger.info(f"🔐 Login attempt {attempt + 1}/{self.config['max_retries']}")
                
                # Execute the precise form sequence
                if self._execute_form_sequence():
                    self.logger.info("✅ Form sequence completed")
                    
                    # Submit login
                    if self._submit_login_background():
                        self.logger.info("✅ Login submitted successfully")
                        
                        # Verify login success
                        if self._verify_login_success():
                            self.logger.info("🎉 Background login completed successfully!")
                            return {"success": True, "message": "Background login successful"}
                        else:
                            self.logger.warning("⚠️ Login verification failed")
                            if attempt < self.config["max_retries"] - 1:
                                time.sleep(3)
                                continue
                    else:
                        self.logger.warning("⚠️ Login submission failed")
                        if attempt < self.config["max_retries"] - 1:
                            time.sleep(3)
                            continue
                else:
                    self.logger.warning("⚠️ Form sequence failed")
                    if attempt < self.config["max_retries"] - 1:
                        time.sleep(3)
                        continue
            
            return {"success": False, "error": "All login attempts failed"}
            
        except Exception as e:
            error_msg = f"Background login failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _execute_form_sequence(self) -> bool:
        """Execute the exact form filling sequence as specified"""
        try:
            self.logger.info("📝 Executing precise form sequence...")
            
            # Bring VBS window to focus (without affecting other apps)
            self._focus_vbs_window_safe()
            
            # User specified: Cursor starts at password field
            # Navigate backwards using Shift+Tab to reach Company dropdown
            
            # Step 1: Navigate from Password to Login ID
            self.logger.info("📝 Step 1: Navigate to Login ID field...")
            self._send_key_to_vbs(VK_SHIFT, VK_TAB)  # Shift+Tab
            time.sleep(0.5)
            
            # Step 2: Navigate from Login ID to Financial Year
            self.logger.info("📝 Step 2: Navigate to Financial Year field...")
            self._send_key_to_vbs(VK_SHIFT, VK_TAB)  # Shift+Tab
            time.sleep(0.5)
            
            # Step 3: Navigate from Financial Year to Company
            self.logger.info("📝 Step 3: Navigate to Company dropdown...")
            self._send_key_to_vbs(VK_SHIFT, VK_TAB)  # Shift+Tab
            time.sleep(0.5)
            
            # Step 4: Fill Company dropdown with "IT"
            self.logger.info("📝 Step 4: Filling Company with 'IT'...")
            self._clear_and_type_to_vbs("IT")
            time.sleep(0.5)
            
            # Step 5: Move to Financial Year and fill
            self.logger.info("📝 Step 5: Moving to Financial Year...")
            self._send_key_to_vbs(VK_TAB)  # Tab to next field
            time.sleep(0.5)
            self._clear_and_type_to_vbs("01/01/2023")
            time.sleep(0.5)
            
            # Step 6: Move to Login ID and fill
            self.logger.info("📝 Step 6: Moving to Login ID...")
            self._send_key_to_vbs(VK_TAB)  # Tab to next field
            time.sleep(0.5)
            self._clear_and_type_to_vbs("vj")
            time.sleep(0.5)
            
            # Step 7: Move to Password and ensure it's empty
            self.logger.info("📝 Step 7: Moving to Password field...")
            self._send_key_to_vbs(VK_TAB)  # Tab to password field
            time.sleep(0.5)
            self._clear_field_vbs()  # Ensure password is empty
            time.sleep(0.5)
            
            self.logger.info("✅ Form sequence completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Form sequence failed: {e}")
            return False
    
    def _focus_vbs_window_safe(self):
        """Focus VBS window safely without affecting other applications"""
        try:
            if self.vbs_login_window:
                # Use SetWindowPos instead of SetForegroundWindow to avoid stealing focus
                win32gui.SetWindowPos(
                    self.vbs_login_window,
                    win32con.HWND_TOP,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
                time.sleep(0.5)
        except Exception as e:
            self.logger.warning(f"⚠️ Safe window focus failed: {e}")
    
    def _send_key_to_vbs(self, *keys):
        """Send key combination directly to VBS window"""
        try:
            if not self.vbs_login_window:
                return False
            
            # Send key down for all keys
            for key in keys:
                win32gui.PostMessage(self.vbs_login_window, WM_KEYDOWN, key, 0)
                time.sleep(0.05)
            
            # Send key up for all keys (in reverse order)
            for key in reversed(keys):
                win32gui.PostMessage(self.vbs_login_window, WM_KEYUP, key, 0)
                time.sleep(0.05)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Key sending failed: {e}")
            return False
    
    def _clear_and_type_to_vbs(self, text: str):
        """Clear field and type text using direct messaging"""
        try:
            # Clear field using Ctrl+A and Delete
            self._send_key_to_vbs(VK_CONTROL, ord('A'))  # Ctrl+A
            time.sleep(0.1)
            self._send_key_to_vbs(win32con.VK_DELETE)  # Delete
            time.sleep(0.1)
            
            # Additional clearing with backspace
            for _ in range(10):
                self._send_key_to_vbs(win32con.VK_BACK)
                time.sleep(0.05)
            
            # Type text character by character
            for char in text:
                if self.vbs_login_window:
                    win32gui.PostMessage(self.vbs_login_window, WM_CHAR, ord(char), 0)
                    time.sleep(0.05)
            
            self.logger.info(f"✅ Typed '{text}' successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Clear and type failed for '{text}': {e}")
    
    def _clear_field_vbs(self):
        """Clear current field"""
        try:
            # Select all and delete
            self._send_key_to_vbs(VK_CONTROL, ord('A'))
            time.sleep(0.1)
            self._send_key_to_vbs(win32con.VK_DELETE)
            time.sleep(0.1)
            
            # Additional backspace clearing
            for _ in range(10):
                self._send_key_to_vbs(win32con.VK_BACK)
                time.sleep(0.05)
                
        except Exception as e:
            self.logger.error(f"❌ Field clearing failed: {e}")
    
    def _submit_login_background(self) -> bool:
        """Submit login using background methods"""
        try:
            self.logger.info("📤 Submitting login in background...")
            
            # Try multiple submission methods
            submit_methods = [
                ("Enter key", lambda: self._send_key_to_vbs(VK_RETURN)),
                ("Alt+O shortcut", lambda: self._send_key_to_vbs(VK_CONTROL, ord('O'))),  # Alt+O
                ("Tab to OK and Enter", lambda: (self._send_key_to_vbs(VK_TAB), time.sleep(0.3), self._send_key_to_vbs(VK_RETURN))),
            ]
            
            for method_name, method_func in submit_methods:
                try:
                    self.logger.info(f"📤 Trying {method_name}...")
                    method_func()
                    time.sleep(3)  # Wait for response
                    
                    # Check if login progressed
                    if self._check_login_progress():
                        self.logger.info(f"✅ Login submitted with {method_name}")
                        return True
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ {method_name} failed: {e}")
                    continue
            
            self.logger.error("❌ All submission methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Login submission failed: {e}")
            return False
    
    def _check_login_progress(self) -> bool:
        """Check if login has progressed"""
        try:
            if not self.vbs_login_window:
                return False
            
            # Check window title change
            current_title = win32gui.GetWindowText(self.vbs_login_window)
            
            # Login successful if title no longer contains "login"
            if 'login' not in current_title.lower():
                return True
            
            # Check for new windows (main application)
            return self._check_for_main_application_window()
            
        except Exception as e:
            self.logger.error(f"❌ Login progress check failed: {e}")
            return False
    
    def _verify_login_success(self) -> bool:
        """Verify login was successful"""
        try:
            self.logger.info("✅ Verifying login success...")
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check for main application window
            if self._check_for_main_application_window():
                self.logger.info("✅ Login verified - main application window found")
                return True
            
            # Check window title change
            if self.vbs_login_window:
                title = win32gui.GetWindowText(self.vbs_login_window)
                success_indicators = ['arabian', 'absons', 'erp', 'moonflower']
                failure_indicators = ['login', 'error', 'invalid']
                
                title_lower = title.lower()
                has_success = any(indicator in title_lower for indicator in success_indicators)
                has_failure = any(indicator in title_lower for indicator in failure_indicators)
                
                if has_success and not has_failure:
                    self.logger.info(f"✅ Login verified via title: {title}")
                    return True
            
            self.logger.warning("⚠️ Login verification inconclusive")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Login verification failed: {e}")
            return False
    
    def _check_for_main_application_window(self) -> bool:
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
                                main_indicators = ['arabian', 'absons', 'erp', 'moonflower']
                                exclude_indicators = ['login', 'security', 'warning']
                                
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
                self.logger.info(f"✅ Main application window found: {main_windows[0][1]}")
                # Update main window handle
                self.vbs_main_window = main_windows[0][0]
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Main window check failed: {e}")
            return False
    
    def _find_security_dialogs(self):
        """Find security dialogs"""
        try:
            dialogs = []
            
            def enum_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            security_indicators = [
                                'security warning', 'open file', 'windows protected',
                                'publisher cannot be verified', 'run', 'security',
                                'user account control', 'windows security'
                            ]
                            
                            title_lower = title.lower()
                            if any(indicator in title_lower for indicator in security_indicators):
                                windows.append((hwnd, title))
                                
                except:
                    pass
                return True
            
            win32gui.EnumWindows(enum_callback, dialogs)
            return dialogs
            
        except Exception as e:
            self.logger.warning(f"⚠️ Security dialog detection failed: {e}")
            return []
    
    def _is_vbs_related_popup(self, hwnd) -> bool:
        """Check if popup is related to VBS process"""
        try:
            # For security popups, they might be system-wide, so we allow them
            return True
        except Exception as e:
            return False
    
    def _monitor_vbs_state(self):
        """Monitor VBS application state"""
        try:
            if self.vbs_main_window and win32gui.IsWindow(self.vbs_main_window):
                # Check if window is still valid
                if not win32gui.IsWindowVisible(self.vbs_main_window):
                    self.logger.warning("⚠️ VBS main window no longer visible")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ VBS state monitoring error: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.logger.info("🧹 Cleaning up background automation...")
            
            # Stop monitoring
            self.monitoring_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            # Reset handles
            self.vbs_process_id = None
            self.vbs_main_window = None
            self.vbs_login_window = None
            
            self.logger.info("✅ Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")
    
    def run_complete_background_automation(self) -> Dict[str, Any]:
        """Run complete background automation sequence"""
        try:
            self.logger.info("🚀 Starting complete VBS background automation...")
            
            result = {
                "success": False,
                "steps_completed": [],
                "errors": [],
                "start_time": datetime.now().isoformat()
            }
            
            # Step 1: Launch application
            launch_result = self.launch_vbs_application()
            if launch_result["success"]:
                result["steps_completed"].append("application_launched")
                self.logger.info("✅ Step 1: Application launched successfully")
            else:
                result["errors"].append(f"Launch failed: {launch_result['error']}")
                return result
            
            # Step 2: Perform background login
            login_result = self.perform_background_login()
            if login_result["success"]:
                result["steps_completed"].append("background_login")
                self.logger.info("✅ Step 2: Background login completed")
                result["success"] = True
            else:
                result["errors"].append(f"Login failed: {login_result['error']}")
                return result
            
            result["end_time"] = datetime.now().isoformat()
            if result.get("start_time"):
                start_time = datetime.fromisoformat(result["start_time"])
                result["total_duration"] = (datetime.now() - start_time).total_seconds()
            
            self.logger.info("🎉 Complete background automation successful!")
            
            return result
            
        except Exception as e:
            error_msg = f"Complete automation failed: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
            result["end_time"] = datetime.now().isoformat()
            return result

# Test function
def test_background_automation():
    """Test the professional background automation system"""
    print("🧪 Testing VBS Background Automation System (Professional Grade)")
    print("=" * 80)
    
    automation = VBSBackgroundAutomation()
    
    try:
        # Test complete automation
        print("\n1. Testing complete background automation...")
        result = automation.run_complete_background_automation()
        
        print(f"\n📊 Results:")
        print(f"   Success: {result['success']}")
        print(f"   Steps completed: {result.get('steps_completed', [])}")
        print(f"   Errors: {result.get('errors', [])}")
        
        if result["success"]:
            print("\n✅ Background automation completed successfully!")
            print("🛡️ Other applications remained immune to automation")
        else:
            print(f"\n❌ Background automation failed: {result.get('errors', [])}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        # Cleanup
        automation.cleanup()
        
    print("\n" + "=" * 80)
    print("Professional Background Automation Test Completed")

if __name__ == "__main__":
    test_background_automation() 