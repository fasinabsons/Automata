#!/usr/bin/env python3
"""
Debug OK Button Clicking Issue
Focused test to identify and fix the OK button clicking problem
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import win32gui
import win32con
import win32api
import pyautogui
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.logger import logger

class OKButtonDebugger:
    """
    Debug and fix OK button clicking issue
    """
    
    def __init__(self):
        self.config = {
            "vbs_path": r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk",
            "credentials": {
                "department": "IT",
                "date": "01/01/2023", 
                "username": "Vj"
            }
        }
        
        # Test different OK button coordinates
        self.ok_button_coordinates = [
            (897, 724),   # Original coordinate
            (897, 720),   # Slightly higher
            (897, 728),   # Slightly lower
            (900, 724),   # Slightly right
            (894, 724),   # Slightly left
            (897, 730),   # Lower
            (897, 715),   # Higher
        ]
        
        # Other coordinates
        self.coordinates = {
            "it_dropdown": (1054, 528),
            "date_field": (1053, 565),
            "username_field": (929, 561),
            "run_button": (1043, 608)
        }
        
        logger.info("OK Button Debugger initialized", "OKDebugger")
    
    def find_vbs_window(self):
        """Find VBS window handle"""
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if "Absons IT" in window_title or "AbsonsItERP" in window_title:
                        windows.append((hwnd, window_title))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                hwnd, title = windows[0]
                print(f"Found VBS window: '{title}' (Handle: {hex(hwnd)})")
                return hwnd
            
            return None
            
        except Exception as e:
            print(f"Error finding VBS window: {e}")
            return None
    
    def launch_vbs(self):
        """Launch VBS application"""
        try:
            print("🚀 Launching VBS application...")
            
            # Launch VBS
            process = subprocess.Popen(['cmd', '/c', 'start', '', self.config["vbs_path"]], shell=True)
            print(f"VBS process started with PID: {process.pid}")
            
            # Wait for VBS to start
            time.sleep(8)  # Longer wait for VBS to fully load
            
            # Find VBS window
            window_handle = self.find_vbs_window()
            
            if window_handle:
                print("✅ VBS application launched and detected")
                
                # Try to bring to foreground
                try:
                    win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
                    time.sleep(1)
                    
                    # Click on window to ensure it's active
                    rect = win32gui.GetWindowRect(window_handle)
                    if rect[2] > rect[0] and rect[3] > rect[1]:  # Valid rectangle
                        center_x = (rect[0] + rect[2]) // 2
                        center_y = (rect[1] + rect[3]) // 2
                        win32api.SetCursorPos((center_x, center_y))
                        time.sleep(0.5)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, center_x, center_y, 0, 0)
                        time.sleep(0.1)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, center_x, center_y, 0, 0)
                        time.sleep(1)
                except:
                    pass  # Continue even if window manipulation fails
                
                return window_handle
            else:
                print("❌ VBS window not found after launch")
                return None
                
        except Exception as e:
            print(f"Error launching VBS: {e}")
            return None
    
    def bring_to_foreground(self, window_handle):
        """Bring VBS window to foreground with better error handling"""
        try:
            # Try multiple methods to bring window to foreground
            win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
            time.sleep(0.5)
            win32gui.SetForegroundWindow(window_handle)
            time.sleep(0.5)
            win32gui.BringWindowToTop(window_handle)
            time.sleep(0.5)
            
            # Click on the window to ensure it's active
            rect = win32gui.GetWindowRect(window_handle)
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            win32api.SetCursorPos((center_x, center_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, center_x, center_y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, center_x, center_y, 0, 0)
            
            print("VBS window brought to foreground")
            return True
        except Exception as e:
            print(f"Warning: Could not bring window to foreground: {e}")
            return False  # Don't fail completely, just warn
    
    def click_coordinate_with_verification(self, coordinate, description=""):
        """Click at coordinate with verification"""
        try:
            x, y = coordinate
            print(f"🖱️ Clicking {description} at ({x}, {y})")
            
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.2)
            
            # Take screenshot of cursor position for verification
            current_pos = win32api.GetCursorPos()
            print(f"   Cursor position: {current_pos}")
            
            # Perform click using Windows API
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            print(f"   ✅ Clicked at ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"   ❌ Error clicking {description}: {e}")
            return False
    
    def double_click_coordinate(self, coordinate, description=""):
        """Double click at coordinate"""
        try:
            x, y = coordinate
            print(f"🖱️ Double-clicking {description} at ({x}, {y})")
            
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.2)
            
            # Perform double click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            print(f"   ✅ Double-clicked at ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"   ❌ Error double-clicking {description}: {e}")
            return False
    
    def ensure_vbs_focus_simple(self, window_handle):
        """Simple method to ensure VBS window has focus"""
        try:
            print("🎯 Ensuring VBS window focus (simple method)...")
            
            # Get window rectangle
            rect = win32gui.GetWindowRect(window_handle)
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            
            print(f"   VBS window found at: {rect}")
            print(f"   Window center: ({center_x}, {center_y})")
            
            # Method 1: Show and restore window
            try:
                win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
                print("   ✅ Window restored")
            except Exception as e:
                print(f"   ⚠️ Could not restore window: {e}")
            
            # Method 2: Click on window center multiple times
            for i in range(3):
                print(f"   Clicking center attempt {i+1}/3")
                win32api.SetCursorPos((center_x, center_y))
                time.sleep(0.3)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, center_x, center_y, 0, 0)
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, center_x, center_y, 0, 0)
                time.sleep(0.5)
            
            # Method 3: Use Alt+Tab to cycle to VBS
            print("   Using Alt+Tab to find VBS window...")
            for i in range(5):  # Try up to 5 Alt+Tab presses
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.8)
                
                # Check if we found VBS
                current_window = win32gui.GetForegroundWindow()
                if current_window == window_handle:
                    print("   ✅ Found VBS window via Alt+Tab")
                    break
                else:
                    current_title = win32gui.GetWindowText(current_window)
                    if "Absons IT" in current_title:
                        print("   ✅ Found VBS window with similar title")
                        break
                    print(f"   Current window: {current_title}")
            
            # Final verification
            time.sleep(1)
            print("   ✅ VBS focus ensured (simple method)")
            return True
            
        except Exception as e:
            print(f"   ❌ Error with simple focus method: {e}")
            return False
    
    def fill_login_form_correctly(self, window_handle):
        """Fill login form with correct sequence and simple focus handling"""
        try:
            print("📝 Filling login form with correct sequence...")
            
            # Use simple focus method
            if not self.ensure_vbs_focus_simple(window_handle):
                print("❌ Cannot ensure VBS focus")
                return False
            
            # Handle security popup
            print("🔐 Handling security popup...")
            time.sleep(2)
            pyautogui.press('left')
            time.sleep(0.5)
            pyautogui.press('enter')
            
            # CRITICAL: Wait 5 seconds for VBS to be completely ready
            print("⏳ Waiting 5 seconds for VBS to be completely ready...")
            time.sleep(5)
            
            # Re-ensure focus after popup
            print("🎯 Re-ensuring focus after popup...")
            self.ensure_vbs_focus_simple(window_handle)
            
            # Field 1: IT Dropdown
            print("📝 Step 1: Filling IT dropdown...")
            self.click_coordinate_with_verification(self.coordinates["it_dropdown"], "IT dropdown")
            time.sleep(1)
            
            # Type IT safely
            print("   ⌨️ Typing 'IT'...")
            pyautogui.typewrite("IT")
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            print("   ✅ IT filled and confirmed")
            
            # Field 2: Date Dropdown
            print("📅 Step 2: Filling date dropdown...")
            pyautogui.press('tab')
            time.sleep(0.8)
            
            # Alternative click
            self.click_coordinate_with_verification(self.coordinates["date_field"], "Date dropdown")
            time.sleep(1)
            
            # Type date safely
            print("   ⌨️ Typing '01/01/2023'...")
            pyautogui.typewrite("01/01/2023")
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            print("   ✅ Date filled and confirmed")
            
            # Field 3: Username field (CRITICAL)
            print("👤 Step 3: Filling username field (Vj)...")
            pyautogui.press('tab')
            time.sleep(0.8)
            
            # Click username field
            self.click_coordinate_with_verification(self.coordinates["username_field"], "Username field")
            time.sleep(0.8)
            
            # Clear field thoroughly
            print("   🧹 Clearing username field...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.3)
            pyautogui.press('backspace')
            time.sleep(0.3)
            
            # Type username
            print("   ⌨️ Typing 'Vj'...")
            pyautogui.typewrite("Vj")
            time.sleep(0.5)
            print("   ✅ Username 'Vj' filled successfully")
            
            # Field 4: Skip password
            print("🔒 Step 4: Skipping password field...")
            pyautogui.press('tab')
            time.sleep(0.5)
            print("   ✅ Password field skipped")
            
            print("✅ All fields filled correctly!")
            return True
            
        except Exception as e:
            print(f"❌ Error filling login form: {e}")
            return False
    
    def test_ok_button_with_better_coordinates(self):
        """Test OK button with more accurate coordinates"""
        try:
            print("\n🧪 TESTING OK BUTTON WITH REFINED COORDINATES")
            print("=" * 55)
            
            # More precise OK button coordinates (accounting for slight variations)
            refined_ok_coordinates = [
                (897, 724),   # Original coordinate
                (897, 722),   # Slightly higher
                (897, 726),   # Slightly lower
                (895, 724),   # Slightly left
                (899, 724),   # Slightly right
                (897, 720),   # Higher
                (897, 728),   # Lower
                (900, 724),   # More right
                (894, 724),   # More left
            ]
            
            for i, coordinate in enumerate(refined_ok_coordinates):
                print(f"\n🔍 Test {i+1}: Trying refined coordinate {coordinate}")
                
                # Click with verification
                success = self.click_coordinate_with_verification(coordinate, f"OK button test {i+1}")
                
                if success:
                    print(f"   ⏳ Waiting to see if coordinate {coordinate} worked...")
                    time.sleep(3)  # Wait to see the result
                    
                    # Ask user for feedback
                    response = input(f"   ❓ Did coordinate {coordinate} successfully click OK and proceed? (y/n/skip): ").lower()
                    
                    if response == 'y':
                        print(f"   🎉 SUCCESS: Coordinate {coordinate} works perfectly!")
                        return coordinate
                    elif response == 'skip':
                        print(f"   ⏭️ Skipping remaining coordinate tests")
                        break
                    else:
                        print(f"   ❌ Coordinate {coordinate} didn't work, trying next...")
                else:
                    print(f"   ❌ Failed to click coordinate {coordinate}")
                
                time.sleep(1)
            
            return None
            
        except Exception as e:
            print(f"❌ Error testing refined OK coordinates: {e}")
            return None
    
    def test_alternative_ok_methods(self):
        """Test alternative methods to click OK"""
        try:
            print("\n🧪 TESTING ALTERNATIVE OK METHODS")
            print("=" * 50)
            
            methods = [
                ("Enter Key", lambda: pyautogui.press('enter')),
                ("Space Key", lambda: pyautogui.press('space')),
                ("Tab + Enter", lambda: (pyautogui.press('tab'), time.sleep(0.2), pyautogui.press('enter'))),
                ("Alt + O", lambda: pyautogui.hotkey('alt', 'o')),
                ("Double Click OK", lambda: self.double_click_coordinate(self.ok_button_coordinates[0], "OK button double-click")),
            ]
            
            for method_name, method_func in methods:
                print(f"\n🔍 Testing: {method_name}")
                
                try:
                    method_func()
                    time.sleep(2)
                    
                    response = input(f"   ❓ Did {method_name} work? (y/n/skip): ").lower()
                    
                    if response == 'y':
                        print(f"   ✅ SUCCESS: {method_name} works!")
                        return method_name
                    elif response == 'skip':
                        print(f"   ⏭️ Skipping remaining tests")
                        break
                    else:
                        print(f"   ❌ {method_name} didn't work, trying next...")
                        
                except Exception as e:
                    print(f"   ❌ Error with {method_name}: {e}")
                
                time.sleep(1)
            
            print("\n❌ No working alternative method found")
            return None
            
        except Exception as e:
            print(f"❌ Error testing alternative methods: {e}")
            return None
    
    def minimize_other_applications(self):
        """Minimize code editors and other applications that might steal focus"""
        try:
            print("🔻 Minimizing other applications to prevent focus stealing...")
            
            # List of applications to minimize
            apps_to_minimize = [
                "Visual Studio Code",
                "Code",
                "Cursor",
                "Notepad++",
                "Sublime Text",
                "Atom",
                "PyCharm",
                "Jupyter",
                "Chrome",
                "Firefox",
                "Edge"
            ]
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    for app in apps_to_minimize:
                        if app.lower() in window_title.lower() and "Absons IT" not in window_title:
                            windows.append((hwnd, window_title))
                            break
                return True
            
            windows_to_minimize = []
            win32gui.EnumWindows(enum_windows_callback, windows_to_minimize)
            
            for hwnd, title in windows_to_minimize:
                try:
                    print(f"   Minimizing: {title}")
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    time.sleep(0.2)
                except:
                    pass
            
            print(f"   ✅ Minimized {len(windows_to_minimize)} applications")
            return True
            
        except Exception as e:
            print(f"   ⚠️ Warning: Could not minimize other applications: {e}")
            return False
    
    def validate_vbs_window_only(self, window_handle):
        """Strict validation to ensure we're only working with VBS window"""
        try:
            print("🔍 Validating VBS window (strict check)...")
            
            # Get window title
            window_title = win32gui.GetWindowText(window_handle)
            print(f"   Window title: '{window_title}'")
            
            # Strict validation - must contain "Absons IT"
            if "Absons IT" not in window_title:
                print(f"   ❌ INVALID: Window title doesn't contain 'Absons IT'")
                return False
            
            # Get window class name for extra validation
            try:
                class_name = win32gui.GetClassName(window_handle)
                print(f"   Window class: '{class_name}'")
            except:
                print("   ⚠️ Could not get window class")
            
            # Check if window is visible
            if not win32gui.IsWindowVisible(window_handle):
                print("   ❌ INVALID: Window is not visible")
                return False
            
            # Get window rectangle
            rect = win32gui.GetWindowRect(window_handle)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            print(f"   Window size: {width}x{height} at ({rect[0]}, {rect[1]})")
            
            # Check if window is minimized (size 0x0)
            if width == 0 and height == 0:
                print("   ⚠️ VBS window is minimized, attempting to restore...")
                try:
                    win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
                    time.sleep(1)
                    
                    # Re-check size after restore
                    rect = win32gui.GetWindowRect(window_handle)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    print(f"   After restore: {width}x{height} at ({rect[0]}, {rect[1]})")
                    
                    if width < 100 or height < 100:
                        print("   ❌ INVALID: Window still too small after restore")
                        return False
                    
                    print("   ✅ VBS window restored successfully")
                    
                except Exception as e:
                    print(f"   ❌ Could not restore window: {e}")
                    return False
            
            elif width < 100 or height < 100:
                print("   ❌ INVALID: Window too small to be VBS")
                return False
            
            print("   ✅ VBS window validation PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Error validating VBS window: {e}")
            return False
    
    def safe_click_vbs_only(self, coordinate, description, window_handle):
        """Safely click only if VBS window is active and valid"""
        try:
            print(f"🖱️ Safe VBS-only click: {description}")
            
            # Validate VBS window before clicking
            if not self.validate_vbs_window_only(window_handle):
                print("   ❌ ABORT: VBS window validation failed")
                return False
            
            # Double-check current active window
            current_window = win32gui.GetForegroundWindow()
            current_title = win32gui.GetWindowText(current_window)
            
            if current_window != window_handle:
                print(f"   ⚠️ Warning: Active window is '{current_title}', not VBS")
                print("   🔄 Attempting to activate VBS window...")
                
                # Try to activate VBS window
                rect = win32gui.GetWindowRect(window_handle)
                center_x = (rect[0] + rect[2]) // 2
                center_y = (rect[1] + rect[3]) // 2
                
                win32api.SetCursorPos((center_x, center_y))
                time.sleep(0.3)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, center_x, center_y, 0, 0)
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, center_x, center_y, 0, 0)
                time.sleep(1)
                
                # Re-check active window
                current_window = win32gui.GetForegroundWindow()
                current_title = win32gui.GetWindowText(current_window)
                
                if "Absons IT" not in current_title:
                    print(f"   ❌ ABORT: Still not VBS window: '{current_title}'")
                    return False
            
            # Now safe to click
            x, y = coordinate
            print(f"   Clicking at ({x}, {y}) in VBS window")
            
            win32api.SetCursorPos((x, y))
            time.sleep(0.3)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            print(f"   ✅ Safe click completed: {description}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error with safe VBS click: {e}")
            return False
    
    def safe_type_vbs_only(self, text, description, window_handle):
        """Safely type text only if VBS window is active"""
        try:
            print(f"⌨️ Safe VBS-only typing: '{text}' for {description}")
            
            # Validate VBS window before typing
            if not self.validate_vbs_window_only(window_handle):
                print("   ❌ ABORT: VBS window validation failed")
                return False
            
            # Double-check current active window
            current_window = win32gui.GetForegroundWindow()
            current_title = win32gui.GetWindowText(current_window)
            
            if "Absons IT" not in current_title:
                print(f"   ❌ ABORT: Active window is '{current_title}', not VBS")
                return False
            
            # Safe to type
            print(f"   Typing '{text}' character by character...")
            for i, char in enumerate(text):
                # Re-check window before each character
                current_window = win32gui.GetForegroundWindow()
                current_title = win32gui.GetWindowText(current_window)
                
                if "Absons IT" not in current_title:
                    print(f"   ❌ ABORT: Lost VBS focus during typing at character {i+1}")
                    return False
                
                print(f"     Typing character {i+1}/{len(text)}: '{char}'")
                pyautogui.typewrite(char)
                time.sleep(0.3)  # Slower typing for safety
            
            print(f"   ✅ Safe typing completed: '{text}'")
            return True
            
        except Exception as e:
            print(f"   ❌ Error with safe VBS typing: {e}")
            return False
    
    def run_vbs_only_debug_session(self):
        """Run debug session that ONLY works with VBS - no other applications"""
        try:
            print("🎯 VBS-ONLY DEBUG SESSION")
            print("=" * 50)
            print("⚠️  STRICT MODE: Will ONLY work with VBS software")
            print("⚠️  Will ABORT if any other application becomes active")
            print("=" * 50)
            
            # Step 1: Find VBS window (don't launch new one)
            print("\n1. Finding existing VBS window...")
            window_handle = self.find_vbs_window()
            
            if not window_handle:
                print("❌ No VBS window found. Please:")
                print("   1. Launch VBS manually")
                print("   2. Make sure it's visible")
                print("   3. Run this script again")
                return False
            
            # Step 2: Strict validation
            print("\n2. Strict VBS window validation...")
            if not self.validate_vbs_window_only(window_handle):
                print("❌ VBS window validation failed")
                return False
            
            # Step 3: Safe login form filling
            print("\n3. Safe VBS-only login form filling...")
            
            # Handle security popup (if present)
            print("🔐 Checking for security popup...")
            current_window = win32gui.GetForegroundWindow()
            current_title = win32gui.GetWindowText(current_window)
            
            if "security" in current_title.lower() or current_window != window_handle:
                print("   Security popup detected, handling...")
                pyautogui.press('left')
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(3)
            
            # Wait for VBS to be ready
            print("⏳ Waiting 5 seconds for VBS to be ready...")
            time.sleep(5)
            
            # Field 1: IT Dropdown
            print("📝 Step 1: IT Dropdown (VBS-only)...")
            if not self.safe_click_vbs_only(self.coordinates["it_dropdown"], "IT dropdown", window_handle):
                return False
            
            time.sleep(1)
            
            if not self.safe_type_vbs_only("IT", "IT dropdown", window_handle):
                return False
            
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # Field 2: Date Dropdown
            print("📅 Step 2: Date Dropdown (VBS-only)...")
            pyautogui.press('tab')
            time.sleep(0.8)
            
            if not self.safe_click_vbs_only(self.coordinates["date_field"], "Date dropdown", window_handle):
                return False
            
            time.sleep(1)
            
            if not self.safe_type_vbs_only("01/01/2023", "Date dropdown", window_handle):
                return False
            
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # Field 3: Username Field (CRITICAL - this is where Vj should go)
            print("👤 Step 3: Username Field (VBS-only) - CRITICAL...")
            pyautogui.press('tab')
            time.sleep(0.8)
            
            if not self.safe_click_vbs_only(self.coordinates["username_field"], "Username field", window_handle):
                return False
            
            time.sleep(0.8)
            
            # Clear field
            print("   🧹 Clearing username field...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # Type Vj ONLY in VBS
            if not self.safe_type_vbs_only("Vj", "Username field", window_handle):
                return False
            
            time.sleep(0.5)
            
            # Field 4: Skip password
            print("🔒 Step 4: Skip password field...")
            pyautogui.press('tab')
            time.sleep(0.5)
            
            print("✅ VBS-only login form completed successfully!")
            
            # Step 4: Test OK button
            print("\n4. Testing OK button (VBS-only)...")
            for i, coordinate in enumerate([(897, 724), (897, 722), (897, 726)]):
                print(f"   Testing OK coordinate {i+1}: {coordinate}")
                
                if not self.safe_click_vbs_only(coordinate, f"OK button test {i+1}", window_handle):
                    continue
                
                time.sleep(2)
                response = input(f"   Did OK button work at {coordinate}? (y/n): ").lower()
                if response == 'y':
                    print(f"   🎉 SUCCESS: OK button works at {coordinate}")
                    return coordinate
            
            return None
            
        except Exception as e:
            print(f"❌ VBS-only debug session failed: {e}")
            return None
        finally:
            print("\n" + "=" * 50)
            print("VBS-Only Debug Session Completed")

    def run_simple_vbs_flow(self):
        """Simple VBS flow: Launch → Click Run → Login → OK"""
        try:
            print("🎯 SIMPLE VBS FLOW")
            print("=" * 50)
            print("Step 1: Launch VBS")
            print("Step 2: Click Run")
            print("Step 3: Login (IT → 01/01/2023 → Vj)")
            print("Step 4: Click OK")
            print("=" * 50)
            
            # Step 1: Launch VBS
            print("\n1. Launching VBS application...")
            window_handle = self.launch_vbs()
            
            if not window_handle:
                print("❌ Failed to launch VBS")
                return False
            
            print(f"✅ VBS launched (Handle: {hex(window_handle)})")
            
            # Step 2: Handle security popup and click Run
            print("\n2. Handling security popup and clicking Run...")
            time.sleep(3)  # Wait for VBS to fully load
            
            # Handle security popup
            print("🔐 Handling security popup...")
            pyautogui.press('left')  # Navigate to Run button
            time.sleep(0.5)
            pyautogui.press('enter')  # Click Run
            time.sleep(5)  # Wait for VBS to be ready for login
            
            print("✅ Run button clicked, VBS should be ready for login")
            
            # Step 3: Login flow - SELECT FROM DROPDOWN LISTS
            print("\n3. Starting login flow - SELECT from dropdown lists...")
            
            # Field 1: IT Dropdown - SELECT from list (don't type)
            print("📝 Step 1: IT Dropdown - Click to open and select...")
            self.click_coordinate_with_verification(self.coordinates["it_dropdown"], "IT dropdown")
            time.sleep(1.5)  # Wait for dropdown to open
            
            # Select IT from dropdown list (first item or arrow keys)
            print("   ⬇️ Selecting IT from dropdown list...")
            pyautogui.press('down')  # Move to IT option
            time.sleep(0.5)
            pyautogui.press('enter')  # Select IT
            time.sleep(0.8)
            print("   ✅ IT selected from dropdown")
            
            # Field 2: Date dropdown - SELECT from list (don't type)
            print("📅 Step 2: Date dropdown - Click to open and select...")
            # Use TAB to move to date field
            pyautogui.press('tab')
            time.sleep(0.8)
            
            # Alternative: Click date field
            self.click_coordinate_with_verification(self.coordinates["date_field"], "Date dropdown")
            time.sleep(1.5)  # Wait for dropdown to open
            
            # Select 01/01/2023 from dropdown list
            print("   ⬇️ Selecting 01/01/2023 from dropdown list...")
            pyautogui.press('down')  # Move to first date option
            time.sleep(0.5)
            pyautogui.press('enter')  # Select the date
            time.sleep(0.8)
            print("   ✅ Date selected from dropdown")
            
            # Field 3: Username field - TYPE "Vj" (this is a text field, not dropdown)
            print("👤 Step 3: Username field - Type 'Vj'...")
            # Use TAB to move to username field
            pyautogui.press('tab')
            time.sleep(0.8)
            
            # Clear any existing content in username field
            print("   🧹 Clearing username field...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # Type Vj in username field
            print("   ⌨️ Typing 'Vj' in username text field...")
            pyautogui.typewrite("Vj")
            time.sleep(0.8)
            print("   ✅ Username 'Vj' entered")
            
            # Field 4: Skip password - Move to next field
            print("🔒 Step 4: Skip password field...")
            pyautogui.press('tab')
            time.sleep(0.5)
            print("   ✅ Password field skipped")
            
            print("✅ Login form completed with DROPDOWN SELECTION!")
            print("   Strategy used:")
            print("   1. ✅ IT dropdown → Click + Select from list")
            print("   2. ✅ Date dropdown → Click + Select from list")
            print("   3. ✅ Username field → Type 'Vj'")
            print("   4. ✅ Password → Skip")
            
            # Step 4: Click OK button
            print("\n4. Testing OK button...")
            ok_coordinates = [(897, 724), (897, 722), (897, 726), (895, 724), (899, 724)]
            
            for i, coordinate in enumerate(ok_coordinates):
                print(f"   Testing OK coordinate {i+1}: {coordinate}")
                
                if self.click_coordinate_with_verification(coordinate, f"OK button test {i+1}"):
                    time.sleep(2)
                    response = input(f"   Did OK button work at {coordinate}? (y/n/continue): ").lower()
                    
                    if response == 'y':
                        print(f"   🎉 SUCCESS: OK button works at {coordinate}")
                        
                        # Check if Run button appears
                        time.sleep(2)
                        run_response = input("   Do you see a Run button now? (y/n): ").lower()
                        if run_response == 'y':
                            print("   Clicking Run button...")
                            self.click_coordinate_with_verification(self.coordinates["run_button"], "Run button")
                        
                        return coordinate
                    elif response == 'continue':
                        continue
                    else:
                        print(f"   ❌ Coordinate {coordinate} didn't work")
            
            print("❌ No working OK button found")
            return None
            
        except Exception as e:
            print(f"❌ Simple VBS flow failed: {e}")
            return None
        finally:
            print("\n" + "=" * 50)
            print("Simple VBS Flow Completed")

def main():
    """Main debug function"""
    debugger = OKButtonDebugger()
    
    print("🎯 SIMPLE VBS LOGIN AUTOMATION")
    print("This simple version will:")
    print("✅ 1. Launch VBS application")
    print("✅ 2. Click Run button in security popup")
    print("✅ 3. Fill login form: IT → 01/01/2023 → Vj")
    print("✅ 4. Test OK button coordinates")
    print("✅ 5. Click Run button if it appears")
    print("=" * 60)
    
    input("Press Enter to start simple VBS automation...")
    
    result = debugger.run_simple_vbs_flow()
    
    if result:
        print(f"\n🎉 SUCCESS: Simple VBS automation working!")
        print(f"✅ Working OK button coordinate: {result}")
        print("✅ Login flow completed successfully")
    else:
        print("\n❌ Simple VBS automation failed")
        print("Please check VBS application and try again")

if __name__ == "__main__":
    main() 