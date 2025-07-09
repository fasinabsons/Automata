#!/usr/bin/env python3
"""
Debug Tab Navigation - Test where cursor goes when pressing Tab
This will help us understand the correct field order
"""

import sys
import time
import win32gui
import win32con
import win32api
import win32process
import psutil
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced

def debug_tab_navigation():
    """Debug tab navigation to see field order"""
    print("=== VBS Tab Navigation Debug ===")
    print("This will help us understand the correct field order")
    print("=" * 50)
    
    # Start VBS and get to login screen
    phase1 = VBSPhase1_Enhanced()
    
    # Check if VBS is already running
    if not phase1._check_vbs_window_exists():
        print("🚀 Starting VBS...")
        launch_result = phase1._launch_vbs_enhanced()
        if not launch_result["success"]:
            print(f"❌ Failed to launch VBS: {launch_result['error']}")
            return
        
        time.sleep(15)  # Wait for VBS to load
        
        if not phase1._find_and_focus_vbs_window():
            print("❌ Could not find VBS window")
            return
    else:
        print("✅ VBS already running")
        phase1._find_and_focus_vbs_window()
    
    print(f"🪟 VBS Window Handle: {phase1.window_handle}")
    
    # Make sure window is focused
    if phase1.window_handle:
        try:
            win32gui.SetForegroundWindow(phase1.window_handle)
            time.sleep(1)
        except:
            pass
    
    print("\n🔍 DEBUG: Testing Tab Navigation")
    print("We'll press Tab and see where cursor goes...")
    
    # Test 1: Press Tab once
    print("\n1️⃣ Pressing Tab ONCE...")
    input("Press Enter to continue...")
    phase1._press_tab()
    time.sleep(1)
    
    print("Type 'TEST1' to see which field this is:")
    input("Press Enter after you see where TEST1 appears...")
    phase1._type_text_efficiently("TEST1")
    time.sleep(2)
    
    # Test 2: Press Tab twice from beginning
    print("\n2️⃣ Going back to beginning and pressing Tab TWICE...")
    input("Press Enter to continue...")
    
    # Reset to beginning
    for i in range(5):
        phase1._press_shift_tab()
        time.sleep(0.2)
    
    # Press Tab twice
    phase1._press_tab()
    time.sleep(0.5)
    phase1._press_tab()
    time.sleep(1)
    
    print("Type 'TEST2' to see which field this is:")
    input("Press Enter after you see where TEST2 appears...")
    phase1._type_text_efficiently("TEST2")
    time.sleep(2)
    
    # Test 3: Press Tab three times from beginning
    print("\n3️⃣ Going back to beginning and pressing Tab THREE times...")
    input("Press Enter to continue...")
    
    # Reset to beginning
    for i in range(5):
        phase1._press_shift_tab()
        time.sleep(0.2)
    
    # Press Tab three times
    phase1._press_tab()
    time.sleep(0.5)
    phase1._press_tab()
    time.sleep(0.5)
    phase1._press_tab()
    time.sleep(1)
    
    print("Type 'TEST3' to see which field this is:")
    input("Press Enter after you see where TEST3 appears...")
    phase1._type_text_efficiently("TEST3")
    time.sleep(2)
    
    # Test 4: No tabs - start from current position
    print("\n4️⃣ Testing current position (no tabs)...")
    input("Press Enter to continue...")
    
    # Reset to beginning
    for i in range(5):
        phase1._press_shift_tab()
        time.sleep(0.2)
    
    print("Type 'TEST0' to see which field this is (no tabs):")
    input("Press Enter after you see where TEST0 appears...")
    phase1._type_text_efficiently("TEST0")
    time.sleep(2)
    
    print("\n🎯 DEBUG COMPLETE!")
    print("Now we know the field order:")
    print("- TEST0 = Field with 0 tabs")
    print("- TEST1 = Field with 1 tab")
    print("- TEST2 = Field with 2 tabs")
    print("- TEST3 = Field with 3 tabs")
    print("\nBased on this, we can fix the Phase 1 navigation!")

if __name__ == "__main__":
    debug_tab_navigation() 