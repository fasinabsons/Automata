#!/usr/bin/env python3
"""
Simple Login Test - Test the basic login without interference
"""

import sys
import time
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced

def test_simple_login():
    """Test simple login"""
    print("=== Simple Login Test ===")
    
    try:
        phase1 = VBSPhase1_Enhanced()
        result = phase1.run_simple_login()
        
        print(f"Result: {result}")
        print(f"Success: {result['success']}")
        print(f"Window Handle: {phase1.get_window_handle()}")
        
        if result["success"]:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_login() 