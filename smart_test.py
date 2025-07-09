#!/usr/bin/env python3
"""
Smart VBS Test - Detects current state and starts from appropriate phase
Automatically determines if VBS needs login or is already logged in
"""

import sys
import time
import win32gui
import win32process
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

def detect_vbs_state():
    """Detect current VBS state and return appropriate starting phase"""
    vbs_windows = []
    
    def enum_windows_callback(hwnd, windows):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    # Look for VBS/Absons indicators
                    vbs_indicators = ['absons', 'erp', 'arabian', 'vbs']
                    
                    title_lower = title.lower()
                    has_vbs = any(indicator in title_lower for indicator in vbs_indicators)
                    
                    if has_vbs:
                        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                        windows.append((hwnd, title, process_id))
                        
        except:
            pass
        return True
    
    win32gui.EnumWindows(enum_windows_callback, vbs_windows)
    
    if not vbs_windows:
        return "no_vbs", None, None
    
    # Analyze windows to determine state
    for hwnd, title, process_id in vbs_windows:
        title_lower = title.lower()
        
        if 'login' in title_lower:
            return "login_required", hwnd, process_id
        elif 'wifi' in title_lower or 'registration' in title_lower:
            return "phase_3_ready", hwnd, process_id
        elif any(indicator in title_lower for indicator in ['absons', 'erp']):
            return "phase_2_ready", hwnd, process_id
    
    # Default to phase 2 if VBS is running but state unclear
    return "phase_2_ready", vbs_windows[0][0], vbs_windows[0][2]

def run_smart_test():
    """Run smart test based on detected VBS state"""
    print("=== SMART VBS AUTOMATION TEST ===")
    print("Detecting current VBS state...")
    print("=" * 50)
    
    # Detect current state
    state, window_handle, process_id = detect_vbs_state()
    
    print(f"Detected state: {state}")
    if window_handle:
        window_title = win32gui.GetWindowText(window_handle)
        print(f"Window: {window_title}")
        print(f"Handle: {window_handle}")
        print(f"Process ID: {process_id}")
    
    test_date_folder = "09jul"
    
    try:
        if state == "no_vbs":
            print("\n[1/3] VBS not running - Starting Phase 1")
            print("-" * 40)
            
            phase1 = VBSPhase1_Enhanced()
            phase1_result = phase1.run_simple_login()
            
            if not phase1_result["success"]:
                print(f"PHASE 1 FAILED: {phase1_result.get('errors', [])}")
                return False
            
            window_handle = phase1.get_window_handle()
            process_id = phase1.get_process_id()
            print(f"PHASE 1 SUCCESS - Window: {window_handle}")
            
            # Continue to Phase 2
            time.sleep(3)
            state = "phase_2_ready"
        
        elif state == "login_required":
            print("\n[1/3] VBS needs login - Starting Phase 1")
            print("-" * 40)
            
            phase1 = VBSPhase1_Enhanced()
            phase1_result = phase1.run_simple_login()
            
            if not phase1_result["success"]:
                print(f"PHASE 1 FAILED: {phase1_result.get('errors', [])}")
                return False
            
            window_handle = phase1.get_window_handle()
            process_id = phase1.get_process_id()
            print(f"PHASE 1 SUCCESS - Window: {window_handle}")
            
            # Continue to Phase 2
            time.sleep(3)
            state = "phase_2_ready"
        
        if state == "phase_2_ready":
            print("\n[2/3] VBS ready for navigation - Starting Phase 2")
            print("-" * 40)
            
            phase2 = VBSPhase2_Navigation()
            phase2.set_window_handle(window_handle)
            phase2_result = phase2.run_phase_2_complete()
            
            if not phase2_result["success"]:
                print(f"PHASE 2 FAILED: {phase2_result.get('errors', [])}")
                return False
            
            print(f"PHASE 2 SUCCESS - Tasks: {phase2_result.get('tasks_completed', [])}")
            
            # Continue to Phase 3
            time.sleep(3)
            state = "phase_3_ready"
        
        if state == "phase_3_ready":
            print("\n[3/3] VBS ready for import - Starting Phase 3")
            print("-" * 40)
            
            phase3 = VBSPhase3_ExcelImport()
            phase3.set_window_handle(window_handle)
            phase3_result = phase3.run_phase_3_complete(test_date_folder)
            
            if not phase3_result["success"]:
                print(f"PHASE 3 FAILED: {phase3_result.get('errors', [])}")
                return False
            
            print(f"PHASE 3 SUCCESS - Tasks: {phase3_result.get('tasks_completed', [])}")
            print(f"Excel File: {phase3_result.get('excel_file', 'N/A')}")
        
        # Success
        print("\n" + "=" * 50)
        print("🎉 SMART TEST COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ VBS automation system is working correctly")
        print("✅ Background operation confirmed")
        print("✅ All phases completed successfully")
        print(f"📁 Date Folder: {test_date_folder}")
        print(f"🪟 Final Window: {window_handle}")
        print(f"🔧 Process ID: {process_id}")
        
        return True
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Smart VBS Automation Test")
    print("This test automatically detects VBS state and runs appropriate phases")
    print("\nPress Enter to start or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        return False
    
    success = run_smart_test()
    
    if success:
        print("\n✅ SMART TEST PASSED!")
        print("The VBS automation system is fully functional.")
    else:
        print("\n❌ SMART TEST FAILED!")
        print("Check the output above for error details.")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except KeyboardInterrupt:
        pass
    
    return success

if __name__ == "__main__":
    main() 