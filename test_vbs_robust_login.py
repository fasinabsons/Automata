#!/usr/bin/env python3
"""
Test script for VBS Phase 1 Robust Implementation
Tests early interaction detection, retry logic, and form state handling
"""

import sys
import os
import time
from datetime import datetime

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from vbs_automation_phase1 import VBSPhase1_LaunchLogin_Robust

def test_robust_vbs_phase1():
    """Test the robust VBS Phase 1 implementation"""
    print("=" * 80)
    print("VBS PHASE 1 ROBUST IMPLEMENTATION TEST")
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the robust Phase 1 implementation
    print("1. Initializing VBS Phase 1 Robust Implementation...")
    phase1 = VBSPhase1_LaunchLogin_Robust()
    print("   ✅ VBS Phase 1 Robust initialized successfully")
    print()
    
    # Display configuration
    print("2. Configuration Details:")
    print(f"   • Max login attempts: {phase1.max_login_attempts}")
    print(f"   • Max app restart attempts: {phase1.max_app_restart_attempts}")
    print(f"   • Form ready wait time: {phase1.form_ready_wait_time} seconds")
    print(f"   • Application paths: {len(phase1.vbs_paths)} configured")
    print()
    
    # Test the complete robust Phase 1 flow
    print("3. Testing Complete Robust Phase 1 Flow...")
    print("   This will test:")
    print("   • Early interaction detection and handling")
    print("   • Form state detection (LoginEmpty.png vs Form.png)")
    print("   • Retry logic for failed login attempts")
    print("   • Application restart capability")
    print("   • Robust form filling with 'rdsr' handling")
    print()
    
    print("   Starting Phase 1 execution...")
    start_time = time.time()
    
    try:
        # Run the complete robust Phase 1
        result = phase1.run_phase_1_complete_robust()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print()
        print("4. Test Results:")
        print(f"   • Execution time: {execution_time:.2f} seconds")
        print(f"   • Success: {result['success']}")
        print(f"   • Attempts made: {result['attempts_made']}")
        print(f"   • Tasks completed: {len(result['tasks_completed'])}")
        
        if result['tasks_completed']:
            print("   • Completed tasks:")
            for task in result['tasks_completed']:
                print(f"     - {task}")
        
        if result['errors']:
            print("   • Errors encountered:")
            for error in result['errors']:
                print(f"     - {error}")
        
        print()
        
        if result['success']:
            print("✅ ROBUST PHASE 1 TEST PASSED!")
            print("   The implementation successfully handled:")
            print("   • Application launch with popup handling")
            print("   • Early interaction detection and waiting")
            print("   • Form state detection and appropriate handling")
            print("   • Login sequence with retry logic")
            print("   • Post-login navigation")
            
            # Get window handle for further testing
            window_handle = phase1.get_window_handle()
            if window_handle:
                print(f"   • VBS application window handle: {window_handle}")
                print("   • Application is ready for Phase 2 operations")
            
        else:
            print("❌ ROBUST PHASE 1 TEST FAILED!")
            print("   The implementation encountered issues that need attention.")
            print("   Review the errors above and check the following:")
            print("   • Network connectivity to VBS application path")
            print("   • Application availability and permissions")
            print("   • Form state detection accuracy")
            print("   • Coordinate accuracy for UI elements")
        
    except Exception as e:
        print(f"❌ TEST EXECUTION FAILED: {e}")
        print("   This indicates a code-level issue that needs fixing.")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def test_individual_components():
    """Test individual components of the robust implementation"""
    print()
    print("INDIVIDUAL COMPONENT TESTS")
    print("-" * 40)
    
    phase1 = VBSPhase1_LaunchLogin_Robust()
    
    # Test 1: Application Launch
    print("1. Testing Application Launch...")
    try:
        launch_result = phase1.task_1_1_launch_application_robust()
        if launch_result['success']:
            print("   ✅ Application launch successful")
            print(f"   • Window handle: {launch_result['window_handle']}")
            print(f"   • Launch path: {launch_result['launch_path']}")
            print(f"   • Window title: {launch_result['window_title']}")
        else:
            print("   ❌ Application launch failed")
            print(f"   • Error: {launch_result['error']}")
    except Exception as e:
        print(f"   ❌ Application launch test failed: {e}")
    
    print()
    
    # Test 2: Form State Detection (if app is running)
    if phase1.window_handle:
        print("2. Testing Form State Detection...")
        try:
            # Test form readiness
            form_ready = phase1._wait_for_form_ready()
            print(f"   • Form ready: {form_ready}")
            
            # Test form state detection
            form_state = phase1._detect_form_state()
            print(f"   • Detected form state: {form_state}")
            
            # Test early interaction detection
            early_interaction = phase1._is_early_interaction_state()
            print(f"   • Early interaction state: {early_interaction}")
            
            # Test form element accessibility
            elements_accessible = phase1._are_form_elements_accessible()
            print(f"   • Form elements accessible: {elements_accessible}")
            
        except Exception as e:
            print(f"   ❌ Form state detection test failed: {e}")
    
    print()

if __name__ == "__main__":
    # Run the main robust test
    test_robust_vbs_phase1()
    
    # Ask user if they want to run individual component tests
    print()
    response = input("Do you want to run individual component tests? (y/n): ").lower().strip()
    if response == 'y' or response == 'yes':
        test_individual_components()
    
    print()
    print("Test script completed. The VBS application should now be ready for Phase 2 operations.") 