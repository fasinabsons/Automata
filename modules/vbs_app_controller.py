#!/usr/bin/env python3
"""
VBS Application Controller
Foundation module for VBS (Absons IT ERP) automation
Handles application launch, window management, and basic operations
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import win32gui
import win32con
import win32api
import win32process
import psutil
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logger import logger

class VBSAppController:
    """
    VBS Application Controller for Absons IT ERP automation
    Handles application lifecycle and basic window operations
    """
    
    def __init__(self):
        """Initialize VBS Application Controller"""
        self.config = {
            "primary_path": r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk",
            "backup_path": r"\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe",
            "app_title_patterns": [
                "Absons IT",
                "AbsonsItERP",
                "ERP",
                "Absons"
            ],
            "startup_timeout": 30,  # seconds
            "operation_timeout": 10,  # seconds
            "retry_attempts": 3
        }
        
        self.process = None
        self.main_window = None
        self.window_handle = None
        self.is_running = False
        
        logger.info("VBS Application Controller initialized", "VBSController")
    
    def launch_application(self) -> Dict[str, Any]:
        """
        Launch VBS application using primary or backup path
        
        Returns:
            Dictionary with launch results
        """
        try:
            logger.info("🚀 Launching VBS application...", "VBSController")
            
            # Try primary path first
            launch_result = self._try_launch_path(self.config["primary_path"])
            
            if not launch_result["success"]:
                logger.warning("Primary path failed, trying backup path", "VBSController")
                launch_result = self._try_launch_path(self.config["backup_path"])
            
            if launch_result["success"]:
                # Wait for application to fully load
                if self._wait_for_application_ready():
                    self.is_running = True
                    logger.info("✅ VBS application launched successfully", "VBSController")
                    return {
                        "success": True,
                        "message": "VBS application launched and ready",
                        "window_handle": self.window_handle,
                        "process_id": self.process.pid if self.process else None
                    }
                else:
                    return {
                        "success": False,
                        "error": "Application launched but not ready for automation"
                    }
            else:
                return launch_result
                
        except Exception as e:
            error_msg = f"Failed to launch VBS application: {e}"
            logger.error(error_msg, "VBSController")
            return {"success": False, "error": error_msg}
    
    def _try_launch_path(self, app_path: str) -> Dict[str, Any]:
        """
        Try to launch VBS from specific path
        
        Args:
            app_path: Path to VBS executable or shortcut
            
        Returns:
            Dictionary with launch attempt results
        """
        try:
            logger.info(f"Attempting to launch: {app_path}", "VBSController")
            
            # Check if path exists
            if not os.path.exists(app_path):
                return {
                    "success": False,
                    "error": f"Path does not exist: {app_path}"
                }
            
            # Launch application
            if app_path.endswith('.lnk'):
                # Handle shortcut
                self.process = subprocess.Popen(['cmd', '/c', 'start', '', app_path], shell=True)
            else:
                # Handle direct executable
                self.process = subprocess.Popen([app_path])
            
            logger.info(f"Process started with PID: {self.process.pid}", "VBSController")
            
            # Give application time to start
            time.sleep(3)
            
            return {"success": True, "process": self.process}
            
        except Exception as e:
            error_msg = f"Launch attempt failed for {app_path}: {e}"
            logger.error(error_msg, "VBSController")
            return {"success": False, "error": error_msg}
    
    def _wait_for_application_ready(self) -> bool:
        """
        Wait for VBS application to be ready for automation
        
        Returns:
            True if application is ready, False otherwise
        """
        try:
            logger.info("⏳ Waiting for VBS application to be ready...", "VBSController")
            
            start_time = time.time()
            timeout = self.config["startup_timeout"]
            
            while time.time() - start_time < timeout:
                # Look for VBS window
                window_handle = self._find_vbs_window()
                
                if window_handle:
                    self.window_handle = window_handle
                    self.main_window = window_handle
                    
                    # Check if window is responsive
                    if self._is_window_responsive(window_handle):
                        logger.info(f"✅ VBS window found and responsive: {hex(window_handle)}", "VBSController")
                        return True
                
                time.sleep(1)
            
            logger.warning(f"⏰ Timeout waiting for VBS application ({timeout}s)", "VBSController")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for application: {e}", "VBSController")
            return False
    
    def _find_vbs_window(self) -> Optional[int]:
        """
        Find VBS application window handle
        
        Returns:
            Window handle if found, None otherwise
        """
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:
                        # Check if title matches VBS patterns
                        for pattern in self.config["app_title_patterns"]:
                            if pattern.lower() in window_title.lower():
                                windows.append((hwnd, window_title))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                # Return the first matching window
                hwnd, title = windows[0]
                logger.info(f"Found VBS window: '{title}' (Handle: {hex(hwnd)})", "VBSController")
                return hwnd
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding VBS window: {e}", "VBSController")
            return None
    
    def _is_window_responsive(self, window_handle: int) -> bool:
        """
        Check if window is responsive to automation
        
        Args:
            window_handle: Window handle to check
            
        Returns:
            True if responsive, False otherwise
        """
        try:
            # Check if window exists and is visible
            if not win32gui.IsWindow(window_handle):
                return False
            
            if not win32gui.IsWindowVisible(window_handle):
                return False
            
            # Try to get window rect (basic responsiveness test)
            rect = win32gui.GetWindowRect(window_handle)
            if rect[2] - rect[0] > 0 and rect[3] - rect[1] > 0:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking window responsiveness: {e}", "VBSController")
            return False
    
    def bring_to_foreground(self) -> bool:
        """
        Bring VBS window to foreground for automation
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.window_handle:
                logger.error("No VBS window handle available", "VBSController")
                return False
            
            # Bring window to foreground
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.window_handle)
            win32gui.BringWindowToTop(self.window_handle)
            
            time.sleep(1)  # Allow window to come to front
            
            logger.info("VBS window brought to foreground", "VBSController")
            return True
            
        except Exception as e:
            logger.error(f"Error bringing window to foreground: {e}", "VBSController")
            return False
    
    def get_window_info(self) -> Dict[str, Any]:
        """
        Get information about the VBS window
        
        Returns:
            Dictionary with window information
        """
        try:
            if not self.window_handle:
                return {"error": "No window handle available"}
            
            rect = win32gui.GetWindowRect(self.window_handle)
            title = win32gui.GetWindowText(self.window_handle)
            
            return {
                "handle": self.window_handle,
                "title": title,
                "position": {
                    "left": rect[0],
                    "top": rect[1],
                    "right": rect[2],
                    "bottom": rect[3],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1]
                },
                "visible": win32gui.IsWindowVisible(self.window_handle),
                "enabled": win32gui.IsWindowEnabled(self.window_handle)
            }
            
        except Exception as e:
            logger.error(f"Error getting window info: {e}", "VBSController")
            return {"error": str(e)}
    
    def close_application(self) -> bool:
        """
        Close VBS application gracefully
        
        Returns:
            True if closed successfully, False otherwise
        """
        try:
            logger.info("🔄 Closing VBS application...", "VBSController")
            
            if self.window_handle:
                # Try to close window gracefully
                win32gui.PostMessage(self.window_handle, win32con.WM_CLOSE, 0, 0)
                time.sleep(2)
                
                # Check if window is still open
                if win32gui.IsWindow(self.window_handle):
                    logger.warning("Window still open, forcing close", "VBSController")
                    win32api.TerminateProcess(win32api.GetCurrentProcess(), 0)
            
            if self.process:
                # Terminate process if still running
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                except:
                    self.process.kill()
            
            self.is_running = False
            self.window_handle = None
            self.main_window = None
            self.process = None
            
            logger.info("✅ VBS application closed", "VBSController")
            return True
            
        except Exception as e:
            logger.error(f"Error closing application: {e}", "VBSController")
            return False
    
    def is_application_running(self) -> bool:
        """
        Check if VBS application is currently running
        
        Returns:
            True if running, False otherwise
        """
        try:
            if not self.is_running:
                return False
            
            if self.window_handle and win32gui.IsWindow(self.window_handle):
                return True
            
            # Try to find window again
            window_handle = self._find_vbs_window()
            if window_handle:
                self.window_handle = window_handle
                return True
            
            self.is_running = False
            return False
            
        except Exception as e:
            logger.error(f"Error checking if application is running: {e}", "VBSController")
            return False
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """
        Take screenshot of VBS window for debugging
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to screenshot file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vbs_screenshot_{timestamp}.png"
            
            screenshot_path = Path("logs") / filename
            screenshot_path.parent.mkdir(exist_ok=True)
            
            # Take screenshot using win32gui
            import win32ui
            import win32con
            from PIL import Image
            
            if self.window_handle:
                # Get window dimensions
                rect = win32gui.GetWindowRect(self.window_handle)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                
                # Create device context
                hwndDC = win32gui.GetWindowDC(self.window_handle)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                # Create bitmap
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                # Copy window content
                saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                
                # Save screenshot
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                img.save(screenshot_path)
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(self.window_handle, hwndDC)
                
                logger.info(f"Screenshot saved: {screenshot_path}", "VBSController")
                return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}", "VBSController")
            return ""

def test_vbs_controller():
    """Test VBS Application Controller functionality"""
    print("🧪 TESTING VBS APPLICATION CONTROLLER")
    print("=" * 50)
    
    controller = VBSAppController()
    
    try:
        # Test 1: Launch Application
        print("\n1. Testing Application Launch...")
        launch_result = controller.launch_application()
        
        if launch_result["success"]:
            print("✅ Application launched successfully")
            print(f"   Window Handle: {launch_result.get('window_handle')}")
            print(f"   Process ID: {launch_result.get('process_id')}")
            
            # Test 2: Window Information
            print("\n2. Testing Window Information...")
            window_info = controller.get_window_info()
            print(f"   Title: {window_info.get('title')}")
            print(f"   Position: {window_info.get('position')}")
            
            # Test 3: Screenshot
            print("\n3. Testing Screenshot...")
            screenshot_path = controller.take_screenshot("test_vbs_controller.png")
            if screenshot_path:
                print(f"✅ Screenshot saved: {screenshot_path}")
            
            # Test 4: Bring to Foreground
            print("\n4. Testing Bring to Foreground...")
            if controller.bring_to_foreground():
                print("✅ Window brought to foreground")
            
            # Wait for user to see the application
            input("\nPress Enter to close the application...")
            
            # Test 5: Close Application
            print("\n5. Testing Application Close...")
            if controller.close_application():
                print("✅ Application closed successfully")
            
        else:
            print(f"❌ Application launch failed: {launch_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    print("\n" + "=" * 50)
    print("VBS Controller Test Completed")

if __name__ == "__main__":
    test_vbs_controller() 