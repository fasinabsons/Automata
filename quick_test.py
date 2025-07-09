#!/usr/bin/env python3
"""
Quick VBS Test - Check system status and run available phases
"""

import sys
import time
import win32gui
import win32process
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

def find_vbs_windows():
    """Find all VBS windows"""
    vbs_windows = []
    
    def enum_windows_callback(hwnd, windows):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    # Look for VBS/Absons indicators
                    vbs_indicators = ['absons', 'erp', 'arabian', 'vbs', 'wifi']
                    exclude_indicators = ['outlook', 'chrome', 'firefox', 'sql server']
                    
                    title_lower = title.lower()
                    has_vbs = any(indicator in title_lower for indicator in vbs_indicators)
                    has_exclude = any(indicator in title_lower for indicator in exclude_indicators)
                    
                    if has_vbs and not has_exclude:
                        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                        windows.append((hwnd, title, process_id))
                        
        except:
            pass
        return True
    
    win32gui.EnumWindows(enum_windows_callback, vbs_windows)
    return vbs_windows

def test_current_system():
    """Test the current VBS system"""
    print("VBS System Status Check")
    print("=" * 40)
    
    # Find VBS windows
    vbs_windows = find_vbs_windows()
    
    if not vbs_windows:
        print("No VBS windows found")
        print("Please start VBS application first")
        return False
    
    print("Found VBS windows:")
    for i, (hwnd, title, pid) in enumerate(vbs_windows):
        print(f"  {i+1}. {title} (Handle: {hwnd}, PID: {pid})")
    
    # Use first window
    window_handle = vbs_windows[0][0]
    window_title = vbs_windows[0][1]
    
    print(f"\nUsing window: {window_title}")
    print(f"Handle: {window_handle}")
    
    # Test Phase 2
    print("\n--- Testing Phase 2 (Navigation) ---")
    phase2 = VBSPhase2_Navigation()
    phase2.set_window_handle(window_handle)
    
    phase2_result = phase2.run_phase_2_complete()
    
    if phase2_result["success"]:
        print("PHASE 2 SUCCESS!")
        print(f"Tasks: {phase2_result.get('tasks_completed', [])}")
        
        # Test Phase 3
        print("\n--- Testing Phase 3 (Excel Import) ---")
        phase3 = VBSPhase3_ExcelImport()
        phase3.set_window_handle(window_handle)
        
        test_date_folder = "09jul"
        phase3_result = phase3.run_phase_3_complete(test_date_folder)
        
        if phase3_result["success"]:
            print("PHASE 3 SUCCESS!")
            print(f"Tasks: {phase3_result.get('tasks_completed', [])}")
            print(f"Excel file: {phase3_result.get('excel_file', 'N/A')}")
            
            print("\n=== COMPLETE SUCCESS ===")
            print("Both Phase 2 and Phase 3 completed successfully!")
            print("The VBS automation system is working correctly.")
            return True
        else:
            print("PHASE 3 FAILED!")
            print(f"Errors: {phase3_result.get('errors', [])}")
            return False
    else:
        print("PHASE 2 FAILED!")
        print(f"Errors: {phase2_result.get('errors', [])}")
        return False

if __name__ == "__main__":
    print("Quick VBS System Test")
    print("This will test Phase 2 -> Phase 3 with current VBS state")
    print("\nPress Enter to start...")
    try:
        input()
    except KeyboardInterrupt:
        print("Test cancelled")
        exit()
    
    success = test_current_system()
    
    if success:
        print("\n✅ SYSTEM TEST PASSED!")
        print("VBS automation is working correctly.")
    else:
        print("\n❌ SYSTEM TEST FAILED!")
        print("Check the errors above for details.")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except KeyboardInterrupt:
        pass 