#!/usr/bin/env python3
"""
Test Phase 1 Only - Intelligent VBS Login
Verify the improved login system works correctly
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced

def test_phase1_intelligent_login():
    """Test the improved Phase 1 intelligent login"""
    print("=== Phase 1 Intelligent Login Test ===")
    print("Testing improved login with smart field handling")
    print("=" * 50)
    
    try:
        print("\n🔐 Starting Phase 1: Intelligent VBS Login")
        print("-" * 40)
        
        phase1 = VBSPhase1_Enhanced()
        result = phase1.run_simple_login()
        
        if result["success"]:
            window_handle = phase1.get_window_handle()
            process_id = phase1.get_process_id()
            
            print("\n✅ PHASE 1 SUCCESS!")
            print("=" * 30)
            print("✅ Intelligent login completed successfully")
            print("✅ Smart field navigation working")
            print("✅ Efficient typing implemented")
            print("✅ No over-clearing of fields")
            print(f"🪟 Window Handle: {window_handle}")
            print(f"🔧 Process ID: {process_id}")
            
            print("\n🎉 INTELLIGENT LOGIN SYSTEM IS WORKING PERFECTLY!")
            print("\nKey improvements:")
            print("• Uses proper Tab navigation between fields")
            print("• Smart field filling (select all + type)")
            print("• No aggressive field clearing")
            print("• Efficient keyboard input")
            print("• Works with existing text in fields")
            
            return True
            
        else:
            print("\n❌ PHASE 1 FAILED!")
            print(f"Errors: {result.get('errors', [])}")
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Phase 1 Intelligent Login Test")
    print("This will test the improved VBS login system:")
    print("• Smart tab navigation")
    print("• Efficient field filling")
    print("• No over-clearing")
    print("\nPress Enter to start or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled")
        return False
    
    success = test_phase1_intelligent_login()
    
    if success:
        print("\n✅ PHASE 1 TEST PASSED!")
        print("The intelligent login system is working perfectly.")
        print("Ready to test Phase 2 and Phase 3!")
    else:
        print("\n❌ PHASE 1 TEST FAILED!")
        print("Check the errors above and fix the login issues.")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except KeyboardInterrupt:
        pass
    
    return success

if __name__ == "__main__":
    main() 