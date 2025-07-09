#!/usr/bin/env python3
"""
Test Phase 3 Excel Import Only
Assumes VBS is already running and WiFi User Registration window is open
"""

import sys
import time
import win32gui
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

def find_vbs_window():
    """Find existing VBS window"""
    vbs_windows = []
    
    def enum_windows_callback(hwnd, windows):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    # Look for VBS/Absons indicators
                    vbs_indicators = ['absons', 'erp', 'arabian', 'vbs', 'wifi']
                    exclude_indicators = ['login', 'security', 'warning']
                    
                    title_lower = title.lower()
                    has_vbs = any(indicator in title_lower for indicator in vbs_indicators)
                    has_exclude = any(indicator in title_lower for indicator in exclude_indicators)
                    
                    if has_vbs and not has_exclude:
                        windows.append((hwnd, title))
                        
        except:
            pass
        return True
    
    win32gui.EnumWindows(enum_windows_callback, vbs_windows)
    
    if vbs_windows:
        print(f"Found VBS windows:")
        for i, (hwnd, title) in enumerate(vbs_windows):
            print(f"  {i+1}. {title} (Handle: {hwnd})")
        return vbs_windows[0][0]  # Return first window
    
    return None

def test_phase3_import():
    """Test Phase 3 Excel import only"""
    print("Phase 3 Excel Import Test")
    print("=" * 30)
    
    # Find existing VBS window
    window_handle = find_vbs_window()
    
    if not window_handle:
        print("ERROR: No VBS window found")
        print("Please ensure VBS is running and WiFi User Registration window is open")
        return False
    
    print(f"Using VBS window handle: {window_handle}")
    
    # Test Phase 3
    print("\nTesting Phase 3 Excel Import...")
    
    phase3 = VBSPhase3_ExcelImport()
    phase3.set_window_handle(window_handle)
    
    # Run import with test date folder
    test_date_folder = "09jul"
    result = phase3.run_phase_3_complete(test_date_folder)
    
    if result["success"]:
        print("PHASE 3 SUCCESS!")
        print(f"Tasks completed: {result.get('tasks_completed', [])}")
        print(f"Excel file: {result.get('excel_file', 'N/A')}")
        return True
    else:
        print("PHASE 3 FAILED!")
        print(f"Errors: {result.get('errors', [])}")
        return False

if __name__ == "__main__":
    success = test_phase3_import()
    
    if success:
        print("\nPhase 3 test completed successfully!")
    else:
        print("\nPhase 3 test failed!")
        
    print("\nPress Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("Test interrupted") 