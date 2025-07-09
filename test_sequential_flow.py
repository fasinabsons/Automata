#!/usr/bin/env python3
"""
VBS Sequential Flow Test - Simplified
Tests Phase 1 → Phase 2 → Phase 3 with proper background operation
"""

import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'sequential_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    return logging.getLogger("SequentialTest")

def test_sequential_phases():
    """Test Phase 1 → Phase 2 → Phase 3 sequentially"""
    logger = setup_logging()
    
    print("🚀 VBS Sequential Flow Test")
    print("=" * 60)
    
    # Test configuration
    test_date_folder = "09jul"
    
    try:
        # PHASE 1: Application Launch & Login
        print("\n🔥 PHASE 1: Application Launch & Login")
        print("-" * 40)
        
        phase1 = VBSPhase1_Enhanced()
        phase1_result = phase1.run_simple_login()
        
        if not phase1_result["success"]:
            print(f"❌ Phase 1 failed: {phase1_result.get('errors', [])}")
            return False
        
        window_handle = phase1.get_window_handle()
        process_id = phase1.get_process_id()
        
        print(f"✅ Phase 1 completed successfully")
        print(f"   Window Handle: {window_handle}")
        print(f"   Process ID: {process_id}")
        
        if not window_handle:
            print("❌ No window handle available for Phase 2")
            return False
        
        # Wait between phases
        time.sleep(3)
        
        # PHASE 2: Navigation
        print("\n🧭 PHASE 2: Navigation")
        print("-" * 40)
        
        phase2 = VBSPhase2_Navigation()
        phase2.set_window_handle(window_handle)
        phase2_result = phase2.run_phase_2_complete()
        
        if not phase2_result["success"]:
            print(f"❌ Phase 2 failed: {phase2_result.get('errors', [])}")
            return False
        
        print(f"✅ Phase 2 completed successfully")
        print(f"   Tasks completed: {phase2_result.get('tasks_completed', [])}")
        
        # Wait between phases
        time.sleep(3)
        
        # PHASE 3: Excel Import
        print("\n📊 PHASE 3: Excel Import")
        print("-" * 40)
        
        phase3 = VBSPhase3_ExcelImport()
        phase3.set_window_handle(window_handle)
        phase3_result = phase3.run_phase_3_complete(test_date_folder)
        
        if not phase3_result["success"]:
            print(f"❌ Phase 3 failed: {phase3_result.get('errors', [])}")
            return False
        
        print(f"✅ Phase 3 completed successfully")
        print(f"   Tasks completed: {phase3_result.get('tasks_completed', [])}")
        print(f"   Excel file: {phase3_result.get('excel_file', 'N/A')}")
        
        # Test completed successfully
        print("\n🎉 ALL PHASES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"✅ Phase 1: Application Launch & Login")
        print(f"✅ Phase 2: Navigation")
        print(f"✅ Phase 3: Excel Import")
        print(f"📁 Test Date Folder: {test_date_folder}")
        print(f"🪟 Window Handle: {window_handle}")
        print(f"🔧 Process ID: {process_id}")
        
        # Keep VBS open for inspection
        print("\n🔍 Keeping VBS open for inspection...")
        print("Press Enter to continue or Ctrl+C to exit...")
        try:
            input()
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        
        return True
        
    except Exception as e:
        logger.error(f"Sequential test failed: {e}")
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Main function"""
    success = test_sequential_phases()
    
    if success:
        print("\n✅ Sequential flow test completed successfully!")
    else:
        print("\n❌ Sequential flow test failed!")
    
    return success

if __name__ == "__main__":
    main() 