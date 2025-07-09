#!/usr/bin/env python3
"""
Test VBS Simple Login - 3 fields + 1 click
Tests the simplified VBS automation approach
"""

import sys
import time
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from vbs_automation_phase1 import VBSPhase1_Simple

def test_vbs_simple_login():
    """Test the simple VBS login approach"""
    print("🧪 TESTING VBS SIMPLE LOGIN")
    print("=" * 50)
    print("This will test the simplified approach:")
    print("1. Launch VBS application")
    print("2. Type 'IT' in company dropdown")
    print("3. Type '01/01/2023' in financial year")
    print("4. Type 'vj' in username")
    print("5. Click OK")
    print("=" * 50)
    
    # Initialize simple login
    vbs_login = VBSPhase1_Simple()
    
    try:
        # Run the simple login
        print("\n🚀 Starting simple VBS login...")
        result = vbs_login.run_simple_login()
        
        print(f"\n📊 RESULTS:")
        print(f"Success: {result['success']}")
        print(f"Start Time: {result['start_time']}")
        print(f"End Time: {result.get('end_time', 'N/A')}")
        print(f"Errors: {result.get('errors', [])}")
        
        if result["success"]:
            print("\n✅ SIMPLE LOGIN SUCCESSFUL!")
            print(f"Window Handle: {hex(vbs_login.get_window_handle()) if vbs_login.get_window_handle() else 'N/A'}")
            print(f"Process ID: {vbs_login.get_process_id()}")
            
            # Wait for user to see the result
            input("\nPress Enter to continue...")
            
        else:
            print("\n❌ SIMPLE LOGIN FAILED!")
            for error in result.get('errors', []):
                print(f"   • {error}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("VBS Simple Login Test Completed")

if __name__ == "__main__":
    test_vbs_simple_login() 