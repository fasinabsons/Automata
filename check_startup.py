#!/usr/bin/env python3
"""
Check Windows startup registration
"""

import winreg

def check_startup():
    """Check if the automation is registered in Windows startup"""
    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, key_path) as reg_key:
            try:
                value = winreg.QueryValueEx(reg_key, "SimpleWiFiRunner")[0]
                print(f"✅ Startup entry found: {value}")
                return True
            except FileNotFoundError:
                print("❌ No startup entry found for SimpleWiFiRunner")
                return False
                
    except Exception as e:
        print(f"❌ Error checking startup: {e}")
        return False

if __name__ == "__main__":
    check_startup() 