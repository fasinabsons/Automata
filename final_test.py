#!/usr/bin/env python3
"""
Final VBS Test - Complete Phase 1 → Phase 2 → Phase 3 Flow
Tests the complete automation workflow with background operation
"""

import sys
import time
import logging
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

# Configure logging to avoid Unicode issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('final_test.log', encoding='utf-8')
    ]
)

def test_complete_vbs_flow():
    """Test complete VBS automation flow"""
    print("=== VBS COMPLETE AUTOMATION TEST ===")
    print("Testing Phase 1 -> Phase 2 -> Phase 3")
    print("=" * 50)
    
    test_date_folder = "09jul"
    
    try:
        # PHASE 1: Login
        print("\n[1/3] PHASE 1: VBS Login")
        print("-" * 30)
        
        phase1 = VBSPhase1_Enhanced()
        phase1_result = phase1.run_simple_login()
        
        if not phase1_result["success"]:
            print(f"PHASE 1 FAILED: {phase1_result.get('errors', [])}")
            return False
        
        window_handle = phase1.get_window_handle()
        process_id = phase1.get_process_id()
        
        print(f"PHASE 1 SUCCESS")
        print(f"  Window Handle: {window_handle}")
        print(f"  Process ID: {process_id}")
        
        if not window_handle:
            print("ERROR: No window handle from Phase 1")
            return False
        
        # Wait between phases
        print("Waiting 3 seconds before Phase 2...")
        time.sleep(3)
        
        # PHASE 2: Navigation
        print("\n[2/3] PHASE 2: Navigation")
        print("-" * 30)
        
        phase2 = VBSPhase2_Navigation()
        phase2.set_window_handle(window_handle)
        phase2_result = phase2.run_phase_2_complete()
        
        if not phase2_result["success"]:
            print(f"PHASE 2 FAILED: {phase2_result.get('errors', [])}")
            return False
        
        print(f"PHASE 2 SUCCESS")
        print(f"  Tasks: {phase2_result.get('tasks_completed', [])}")
        
        # Wait between phases
        print("Waiting 3 seconds before Phase 3...")
        time.sleep(3)
        
        # PHASE 3: Excel Import
        print("\n[3/3] PHASE 3: Excel Import")
        print("-" * 30)
        
        phase3 = VBSPhase3_ExcelImport()
        phase3.set_window_handle(window_handle)
        phase3_result = phase3.run_phase_3_complete(test_date_folder)
        
        if not phase3_result["success"]:
            print(f"PHASE 3 FAILED: {phase3_result.get('errors', [])}")
            return False
        
        print(f"PHASE 3 SUCCESS")
        print(f"  Tasks: {phase3_result.get('tasks_completed', [])}")
        print(f"  Excel File: {phase3_result.get('excel_file', 'N/A')}")
        
        # Complete success
        print("\n" + "=" * 50)
        print("🎉 ALL PHASES COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ Phase 1: VBS Login - SUCCESS")
        print("✅ Phase 2: Navigation - SUCCESS")
        print("✅ Phase 3: Excel Import - SUCCESS")
        print(f"📁 Date Folder: {test_date_folder}")
        print(f"🪟 Window Handle: {window_handle}")
        print(f"🔧 Process ID: {process_id}")
        
        return True
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Starting VBS Complete Automation Test...")
    print("This will test the complete workflow:")
    print("1. Phase 1: VBS Login")
    print("2. Phase 2: Navigation to WiFi User Registration")
    print("3. Phase 3: Excel Import")
    print("\nPress Enter to start or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        return False
    
    success = test_complete_vbs_flow()
    
    if success:
        print("\n✅ COMPLETE AUTOMATION TEST PASSED!")
        print("The VBS automation system is working correctly.")
        print("All phases can run in background without affecting other applications.")
    else:
        print("\n❌ COMPLETE AUTOMATION TEST FAILED!")
        print("Check the logs for detailed error information.")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except KeyboardInterrupt:
        pass
    
    return success

if __name__ == "__main__":
    main() 