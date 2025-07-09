#!/usr/bin/env python3
"""
Combined Test: VBS Phase 1 + Phase 2
Tests the complete workflow from login to WiFi User Registration navigation
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Import Phase 1 and Phase 2
from modules.vbs_automation_phase1 import VBSPhase1_Simple
from vbs_phase2_navigation import VBSPhase2Navigation

def test_phase1_and_phase2():
    """Test complete Phase 1 + Phase 2 workflow"""
    print("🚀 TESTING COMPLETE VBS PHASE 1 + PHASE 2 WORKFLOW")
    print("=" * 80)
    print("This will test:")
    print("📋 PHASE 1: VBS Application Launch + Login")
    print("   • Launch VBS application")
    print("   • Handle security popup")
    print("   • Fill login form (IT, 01/01/2023, vj)")
    print("   • Submit login")
    print("")
    print("📋 PHASE 2: Navigation to WiFi User Registration")
    print("   • Navigate to Sales & Distribution")
    print("   • Navigate to POS")
    print("   • Navigate to WiFi User Registration")
    print("=" * 80)
    
    overall_success = True
    phase1_result = None
    phase2_result = None
    
    try:
        # ===================
        # PHASE 1: LOGIN
        # ===================
        print("\n🔥 STARTING PHASE 1: VBS LOGIN")
        print("-" * 50)
        
        # Initialize Phase 1
        phase1 = VBSPhase1_Simple()
        
        # Run Phase 1
        phase1_result = phase1.run_simple_login()
        
        # Display Phase 1 results
        print(f"\n📊 PHASE 1 RESULTS:")
        print(f"Success: {phase1_result['success']}")
        print(f"Start Time: {phase1_result['start_time']}")
        print(f"End Time: {phase1_result.get('end_time', 'N/A')}")
        
        if phase1_result.get('errors'):
            print(f"❌ PHASE 1 ERRORS:")
            for error in phase1_result['errors']:
                print(f"   • {error}")
        
        if not phase1_result['success']:
            print("❌ PHASE 1 FAILED - Cannot proceed to Phase 2")
            overall_success = False
            return
        
        print("✅ PHASE 1 COMPLETED SUCCESSFULLY!")
        print(f"VBS Window Handle: {hex(phase1.get_window_handle()) if phase1.get_window_handle() else 'N/A'}")
        print(f"VBS Process ID: {phase1.get_process_id()}")
        
        # Wait a moment for application to stabilize
        print("\n⏳ Waiting for application to stabilize before Phase 2...")
        time.sleep(5)
        
        # ===================
        # PHASE 2: NAVIGATION
        # ===================
        print("\n🧭 STARTING PHASE 2: NAVIGATION")
        print("-" * 50)
        
        # Initialize Phase 2 with window handle from Phase 1
        phase2 = VBSPhase2Navigation()
        phase2.set_window_handle(phase1.get_window_handle())
        
        # Run Phase 2
        phase2_result = phase2.run_phase2_navigation()
        
        # Display Phase 2 results
        print(f"\n📊 PHASE 2 RESULTS:")
        print(f"Success: {phase2_result['success']}")
        print(f"Start Time: {phase2_result['start_time']}")
        print(f"End Time: {phase2_result.get('end_time', 'N/A')}")
        
        if phase2_result.get('navigation_completed'):
            print(f"\n🧭 NAVIGATION COMPLETED:")
            for step in phase2_result['navigation_completed']:
                print(f"   ✅ {step}")
        
        if phase2_result.get('errors'):
            print(f"\n❌ PHASE 2 ERRORS:")
            for error in phase2_result['errors']:
                print(f"   • {error}")
        
        if not phase2_result['success']:
            print("❌ PHASE 2 FAILED")
            overall_success = False
        else:
            print("✅ PHASE 2 COMPLETED SUCCESSFULLY!")
            print(f"Final VBS Window Handle: {hex(phase2.get_window_handle()) if phase2.get_window_handle() else 'N/A'}")
            print(f"Final VBS Process ID: {phase2.get_process_id()}")
        
    except Exception as e:
        print(f"❌ WORKFLOW FAILED WITH EXCEPTION: {e}")
        overall_success = False
    
    # ===================
    # FINAL SUMMARY
    # ===================
    print("\n" + "=" * 80)
    print("📊 COMPLETE WORKFLOW SUMMARY")
    print("=" * 80)
    
    if phase1_result:
        print(f"📋 PHASE 1 (Login): {'✅ SUCCESS' if phase1_result['success'] else '❌ FAILED'}")
        if phase1_result.get('errors'):
            print(f"   Errors: {len(phase1_result['errors'])}")
    
    if phase2_result:
        print(f"📋 PHASE 2 (Navigation): {'✅ SUCCESS' if phase2_result['success'] else '❌ FAILED'}")
        if phase2_result.get('navigation_completed'):
            print(f"   Navigation Steps: {len(phase2_result['navigation_completed'])}/3")
        if phase2_result.get('errors'):
            print(f"   Errors: {len(phase2_result['errors'])}")
    
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        print("\n🎉 PHASE 1 + PHASE 2 WORKFLOW COMPLETED SUCCESSFULLY!")
        print("✅ VBS is now logged in and navigated to WiFi User Registration")
        print("🚀 Ready for Phase 3 (Excel Import)!")
    else:
        print("\n❌ WORKFLOW FAILED - Please check errors above")
    
    print("\n" + "=" * 80)
    print("Combined Phase 1 + Phase 2 Test Completed")
    
    return overall_success

def quick_test():
    """Quick test without detailed output"""
    print("🚀 Quick Test: Phase 1 + Phase 2")
    
    # Phase 1
    phase1 = VBSPhase1_Simple()
    result1 = phase1.run_simple_login()
    
    if result1['success']:
        print("✅ Phase 1 successful")
        
        # Phase 2
        time.sleep(3)
        phase2 = VBSPhase2Navigation()
        phase2.set_window_handle(phase1.get_window_handle())
        result2 = phase2.run_phase2_navigation()
        
        if result2['success']:
            print("✅ Phase 2 successful")
            print("🎉 Complete workflow successful!")
            return True
        else:
            print("❌ Phase 2 failed")
            return False
    else:
        print("❌ Phase 1 failed")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        test_phase1_and_phase2() 