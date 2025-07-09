#!/usr/bin/env python3
"""
Test Complete Phase 2 Navigation Sequence
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

def test_complete_phase2():
    """Test complete Phase 2 navigation sequence"""
    print("🧪 Testing Complete VBS Phase 2 Navigation")
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
    
    print("\n🚀 Starting Complete Phase 2 Navigation...")
    print("This will navigate: Arrow → Sales & Distribution → POS → WiFi User Registration")
    
    # Run the complete Phase 2 sequence
    result = phase2.run_phase_2_complete()
    
    print(f"\n📊 Phase 2 Results:")
    print(f"   Success: {result['success']}")
    print(f"   Tasks Completed: {result.get('tasks_completed', [])}")
    print(f"   Errors: {result.get('errors', [])}")
    
    return result['success']

if __name__ == "__main__":
    success = test_complete_phase2()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Complete Phase 2 Navigation: SUCCESS")
        print("✅ Ready for Phase 3 (Excel Import)")
    else:
        print("❌ Complete Phase 2 Navigation: FAILED")
    print("=" * 50) 