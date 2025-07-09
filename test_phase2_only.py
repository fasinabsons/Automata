#!/usr/bin/env python3
"""
Test Phase 2 Only - Debug Arrow Button Issue
"""

import sys
import time
import win32gui
from modules.vbs_automation_phase2 import VBSPhase2_Navigation

def find_vbs_window():
    """Find the current VBS window"""
    vbs_windows = []
    
    def enum_windows_callback(hwnd, windows):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    # Look for VBS indicators
                    vbs_indicators = ['absons', 'arabian', 'moonflower', 'erp']
                    exclude_indicators = ['login', 'security', 'warning', 'brave', 'chrome', 'firefox']
                    
                    title_lower = title.lower()
                    has_vbs = any(indicator in title_lower for indicator in vbs_indicators)
                    has_exclude = any(indicator in title_lower for indicator in exclude_indicators)
                    
                    if has_vbs and not has_exclude:
                        windows.append((hwnd, title))
                        
        except:
            pass
        return True
    
    win32gui.EnumWindows(enum_windows_callback, vbs_windows)
    return vbs_windows

def test_phase2_arrow_button():
    """Test Phase 2 arrow button clicking specifically"""
    print("🧪 Testing VBS Phase 2 - Arrow Button Debug")
    print("=" * 50)
    
    # Find VBS window
    vbs_windows = find_vbs_window()
    
    if not vbs_windows:
        print("❌ No VBS windows found. Please ensure VBS is running.")
        return False
    
    # Use the first VBS window found
    window_handle, window_title = vbs_windows[0]
    print(f"✅ Found VBS window: '{window_title}' (Handle: {window_handle})")
    
    # Initialize Phase 2
    phase2 = VBSPhase2_Navigation(window_handle)
    
    # Test just the arrow button click
    print("\n🎯 Testing Arrow Button Click...")
    print("Current arrow button coordinates: (25, 65)")
    
    # Get the coordinates
    coords = phase2.get_current_coordinates()
    arrow_x, arrow_y = coords["arrow_button"]
    
    print(f"Clicking at coordinates: ({arrow_x}, {arrow_y})")
    
    # Try clicking the arrow button
    success = phase2._click_coordinate_background(arrow_x, arrow_y, False)
    
    if success:
        print("✅ Arrow button click successful!")
        
        # Wait and see if menu opened
        time.sleep(2)
        print("⏳ Waiting 2 seconds to see if menu opened...")
        
        # Try the next step - Sales & Distribution
        print("\n🎯 Testing Sales & Distribution Click...")
        sales_x, sales_y = coords["sales_distribution"]
        print(f"Clicking Sales & Distribution at: ({sales_x}, {sales_y})")
        
        success2 = phase2._click_coordinate_background(sales_x, sales_y, False)
        
        if success2:
            print("✅ Sales & Distribution click successful!")
            return True
        else:
            print("❌ Sales & Distribution click failed!")
            return False
    else:
        print("❌ Arrow button click failed!")
        return False

if __name__ == "__main__":
    success = test_phase2_arrow_button()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Phase 2 Arrow Button Test: SUCCESS")
    else:
        print("❌ Phase 2 Arrow Button Test: FAILED")
    print("=" * 50) 