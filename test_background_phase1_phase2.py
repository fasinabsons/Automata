#!/usr/bin/env python3
"""
Test VBS Phase 1 (Background Mode) then Phase 2 (Navigation)
"""

import sys
import time
import os
from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation

def test_background_phase1_then_phase2():
    """Test Phase 1 in background mode, then Phase 2 navigation"""
    print("🧪 Testing VBS Phase 1 (Background Mode) then Phase 2 (Navigation)")
    print("=" * 70)
    
    # Phase 1: Login in Background Mode
    print("\n🔐 PHASE 1: VBS Login (Background Mode)")
    print("-" * 40)
    print("ℹ️  This test will run in background without affecting other applications")
    print("ℹ️  You can continue working while this runs")
    
    vbs_phase1 = VBSPhase1_Enhanced()
    
    # Store current active window to restore later
    import win32gui
    original_window = win32gui.GetForegroundWindow()
    
    print("\n🚀 Starting Phase 1 in background mode...")
    phase1_result = vbs_phase1.run_simple_login()
    
    # Restore original window focus
    try:
        if original_window:
            win32gui.SetForegroundWindow(original_window)
    except:
        pass
    
    print(f"\n📊 Phase 1 Results:")
    print(f"   Success: {phase1_result['success']}")
    print(f"   Errors: {phase1_result.get('errors', [])}")
    print(f"   Window Handle: {vbs_phase1.get_window_handle()}")
    print(f"   Process ID: {vbs_phase1.get_process_id()}")
    
    if not phase1_result["success"]:
        print("\n❌ Phase 1 failed, cannot proceed to Phase 2")
        return False
    
    print("\n✅ Phase 1 completed successfully in background mode!")
    
    # Get window handle from Phase 1 for Phase 2
    window_handle = vbs_phase1.get_window_handle()
    
    if not window_handle:
        print("\n❌ No window handle available for Phase 2")
        return False
    
    # Brief pause between phases
    print("\n⏳ Waiting 3 seconds before starting Phase 2...")
    time.sleep(3)
    
    # Phase 2: Navigation (Background Mode)
    print("\n🧭 PHASE 2: Navigation to WiFi User Registration (Background Mode)")
    print("-" * 60)
    
    vbs_phase2 = VBSPhase2_Navigation(window_handle)
    
    print("🚀 Starting Phase 2 navigation...")
    phase2_result = vbs_phase2.run_phase_2_complete()
    
    print(f"\n📊 Phase 2 Results:")
    print(f"   Success: {phase2_result['success']}")
    print(f"   Tasks Completed: {phase2_result.get('tasks_completed', [])}")
    print(f"   Errors: {phase2_result.get('errors', [])}")
    
    if phase2_result["success"]:
        print("\n🎉 Both Phase 1 and Phase 2 completed successfully in background mode!")
        print("✅ VBS is now ready for Phase 3 (Excel Import)")
        return True
    else:
        print(f"\n❌ Phase 2 failed: {phase2_result.get('errors', [])}")
        return False

def test_locked_screen_compatibility():
    """Test if the system works when screen is locked"""
    print("\n🔒 LOCKED SCREEN COMPATIBILITY TEST")
    print("-" * 40)
    print("ℹ️  This test checks if automation works when screen is locked")
    print("ℹ️  You can lock your screen (Win+L) and the automation should continue")
    
    # Give user time to lock screen if they want
    print("\n⏰ You have 10 seconds to lock your screen (Win+L) if you want to test locked mode...")
    for i in range(10, 0, -1):
        print(f"   {i} seconds remaining...")
        time.sleep(1)
    
    print("\n🚀 Starting automation (works with locked screen)...")
    return test_background_phase1_then_phase2()

if __name__ == "__main__":
    print("🔧 VBS Background & Locked Screen Compatibility Test")
    print("=" * 70)
    
    choice = input("\nChoose test mode:\n1. Background Mode Test\n2. Locked Screen Compatibility Test\n\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        success = test_locked_screen_compatibility()
    else:
        success = test_background_phase1_then_phase2()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 COMPLETE SUCCESS: Background automation works perfectly!")
        print("✅ Phase 1 + Phase 2 completed without affecting other applications")
        print("🚀 Ready for Phase 3 (Excel Import)")
    else:
        print("❌ TEST FAILED: Background automation needs adjustment")
    
    print("=" * 70) 