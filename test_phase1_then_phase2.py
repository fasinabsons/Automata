#!/usr/bin/env python3
"""
Test Phase 1 (Login) then Phase 2 (Navigation) in sequence
"""

import sys
import time
from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation

def test_phase1_then_phase2():
    """Test Phase 1 login, then Phase 2 navigation if successful"""
    print("🧪 Testing VBS Phase 1 (Login) then Phase 2 (Navigation)")
    print("=" * 70)
    
    # Phase 1: Login
    print("\n🔐 PHASE 1: VBS Login")
    print("-" * 30)
    
    vbs_phase1 = VBSPhase1_Enhanced()
    phase1_result = vbs_phase1.run_simple_login()
    
    print(f"\n📊 Phase 1 Results:")
    print(f"   Success: {phase1_result['success']}")
    print(f"   Errors: {phase1_result.get('errors', [])}")
    print(f"   Window Handle: {vbs_phase1.get_window_handle()}")
    print(f"   Process ID: {vbs_phase1.get_process_id()}")
    
    if not phase1_result["success"]:
        print("\n❌ Phase 1 failed, cannot proceed to Phase 2")
        return False
    
    print("\n✅ Phase 1 completed successfully!")
    
    # Get window handle from Phase 1 for Phase 2
    window_handle = vbs_phase1.get_window_handle()
    
    if not window_handle:
        print("\n❌ No window handle available for Phase 2")
        return False
    
    # Brief pause between phases
    print("\n⏳ Waiting 2 seconds before starting Phase 2...")
    time.sleep(2)
    
    # Phase 2: Navigation
    print("\n🧭 PHASE 2: Navigation to WiFi User Registration")
    print("-" * 50)
    
    vbs_phase2 = VBSPhase2_Navigation(window_handle)
    phase2_result = vbs_phase2.run_phase_2_complete()
    
    print(f"\n📊 Phase 2 Results:")
    print(f"   Success: {phase2_result['success']}")
    print(f"   Tasks Completed: {phase2_result.get('tasks_completed', [])}")
    print(f"   Errors: {phase2_result.get('errors', [])}")
    
    if phase2_result["success"]:
        print("\n🎉 Both Phase 1 and Phase 2 completed successfully!")
        print("✅ VBS is now ready for Phase 3 (Excel Import)")
        return True
    else:
        print(f"\n❌ Phase 2 failed: {phase2_result.get('errors', [])}")
        return False

if __name__ == "__main__":
    success = test_phase1_then_phase2()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 COMPLETE SUCCESS: Phase 1 + Phase 2 finished!")
        print("🚀 Ready for Phase 3 (Excel Import)")
    else:
        print("❌ TEST FAILED: One or both phases failed")
    
    print("=" * 70) 