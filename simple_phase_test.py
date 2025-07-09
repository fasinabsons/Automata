#!/usr/bin/env python3
"""
Simple VBS Phase Test
Tests Phase 1 -> Phase 2 -> Phase 3 without Unicode issues
"""

import sys
import time
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

def test_phases():
    """Test Phase 1 -> Phase 2 -> Phase 3 sequentially"""
    print("VBS Sequential Phase Test")
    print("=" * 50)
    
    test_date_folder = "09jul"
    
    try:
        # PHASE 1: Login
        print("\nPHASE 1: Application Launch & Login")
        print("-" * 30)
        
        phase1 = VBSPhase1_Enhanced()
        phase1_result = phase1.run_simple_login()
        
        if not phase1_result["success"]:
            print(f"PHASE 1 FAILED: {phase1_result.get('errors', [])}")
            return False
        
        window_handle = phase1.get_window_handle()
        process_id = phase1.get_process_id()
        
        print(f"PHASE 1 SUCCESS")
        print(f"Window Handle: {window_handle}")
        print(f"Process ID: {process_id}")
        
        if not window_handle:
            print("ERROR: No window handle available")
            return False
        
        # Wait between phases
        time.sleep(3)
        
        # PHASE 2: Navigation
        print("\nPHASE 2: Navigation")
        print("-" * 30)
        
        phase2 = VBSPhase2_Navigation()
        phase2.set_window_handle(window_handle)
        phase2_result = phase2.run_phase_2_complete()
        
        if not phase2_result["success"]:
            print(f"PHASE 2 FAILED: {phase2_result.get('errors', [])}")
            return False
        
        print(f"PHASE 2 SUCCESS")
        print(f"Tasks: {phase2_result.get('tasks_completed', [])}")
        
        # Wait between phases
        time.sleep(3)
        
        # PHASE 3: Excel Import
        print("\nPHASE 3: Excel Import")
        print("-" * 30)
        
        phase3 = VBSPhase3_ExcelImport()
        phase3.set_window_handle(window_handle)
        phase3_result = phase3.run_phase_3_complete(test_date_folder)
        
        if not phase3_result["success"]:
            print(f"PHASE 3 FAILED: {phase3_result.get('errors', [])}")
            return False
        
        print(f"PHASE 3 SUCCESS")
        print(f"Tasks: {phase3_result.get('tasks_completed', [])}")
        print(f"Excel file: {phase3_result.get('excel_file', 'N/A')}")
        
        # All phases completed
        print("\nALL PHASES COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("Phase 1: Login - SUCCESS")
        print("Phase 2: Navigation - SUCCESS")
        print("Phase 3: Excel Import - SUCCESS")
        print(f"Date Folder: {test_date_folder}")
        print(f"Window Handle: {window_handle}")
        print(f"Process ID: {process_id}")
        
        # Keep VBS open
        print("\nKeeping VBS open for inspection...")
        print("Press Enter to continue...")
        try:
            input()
        except KeyboardInterrupt:
            print("Test interrupted")
        
        return True
        
    except Exception as e:
        print(f"TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_phases()
    
    if success:
        print("\nSEQUENTIAL TEST COMPLETED SUCCESSFULLY!")
    else:
        print("\nSEQUENTIAL TEST FAILED!") 