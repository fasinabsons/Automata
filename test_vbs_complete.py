#!/usr/bin/env python3
"""
Complete VBS Test - Single file to test Phase 1 → Phase 2 → Phase 3
Efficient and intelligent workflow testing
"""

import sys
import time
import win32gui
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

def test_complete_vbs_workflow():
    """Test complete VBS workflow efficiently"""
    print("=== VBS Complete Workflow Test ===")
    print("Testing Phase 1 → Phase 2 → Phase 3")
    print("=" * 50)
    
    test_date_folder = "09jul"
    
    try:
        # PHASE 1: Intelligent Login
        print("\n[1/3] PHASE 1: Intelligent VBS Login")
        print("-" * 30)
        
        phase1 = VBSPhase1_Enhanced()
        phase1_result = phase1.run_simple_login()
        
        if not phase1_result["success"]:
            print(f"❌ Phase 1 FAILED: {phase1_result.get('errors', [])}")
            return False
        
        window_handle = phase1.get_window_handle()
        process_id = phase1.get_process_id()
        
        print(f"✅ Phase 1 SUCCESS")
        print(f"   Window Handle: {window_handle}")
        print(f"   Process ID: {process_id}")
        
        if not window_handle:
            print("❌ No window handle from Phase 1")
            return False
        
        # Wait between phases
        time.sleep(2)
        
        # PHASE 2: Smart Navigation
        print("\n[2/3] PHASE 2: Smart Navigation")
        print("-" * 30)
        
        phase2 = VBSPhase2_Navigation()
        phase2.set_window_handle(window_handle)
        phase2_result = phase2.run_phase_2_complete()
        
        if not phase2_result["success"]:
            print(f"❌ Phase 2 FAILED: {phase2_result.get('errors', [])}")
            return False
        
        print(f"✅ Phase 2 SUCCESS")
        print(f"   Tasks: {phase2_result.get('tasks_completed', [])}")
        
        # Wait between phases
        time.sleep(2)
        
        # PHASE 3: Efficient Excel Import
        print("\n[3/3] PHASE 3: Efficient Excel Import")
        print("-" * 30)
        
        phase3 = VBSPhase3_ExcelImport()
        phase3.set_window_handle(window_handle)
        phase3_result = phase3.run_phase_3_complete(test_date_folder)
        
        if not phase3_result["success"]:
            print(f"❌ Phase 3 FAILED: {phase3_result.get('errors', [])}")
            return False
        
        print(f"✅ Phase 3 SUCCESS")
        print(f"   Tasks: {phase3_result.get('tasks_completed', [])}")
        print(f"   Excel File: {phase3_result.get('excel_file', 'N/A')}")
        
        # SUCCESS!
        print("\n" + "=" * 50)
        print("🎉 COMPLETE WORKFLOW SUCCESS!")
        print("=" * 50)
        print("✅ Phase 1: Intelligent Login - SUCCESS")
        print("✅ Phase 2: Smart Navigation - SUCCESS") 
        print("✅ Phase 3: Efficient Excel Import - SUCCESS")
        print(f"📁 Date Folder: {test_date_folder}")
        print(f"🪟 Window Handle: {window_handle}")
        print(f"🔧 Process ID: {process_id}")
        print("\n🚀 VBS Automation System is WORKING PERFECTLY!")
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("VBS Complete Workflow Test")
    print("This will test the complete automation system:")
    print("1. Phase 1: Intelligent VBS Login")
    print("2. Phase 2: Smart Navigation")
    print("3. Phase 3: Efficient Excel Import")
    print("\nPress Enter to start or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled")
        return False
    
    success = test_complete_vbs_workflow()
    
    if success:
        print("\n✅ COMPLETE TEST PASSED!")
        print("The VBS automation system is working perfectly.")
        print("Ready for production use!")
    else:
        print("\n❌ TEST FAILED!")
        print("Check the errors above and fix the issues.")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except KeyboardInterrupt:
        pass
    
    return success

if __name__ == "__main__":
    main() 