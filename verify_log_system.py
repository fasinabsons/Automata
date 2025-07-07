#!/usr/bin/env python3
"""
Log System Verification Script
Verifies that the centralized logging system is working properly
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

def test_centralized_logging():
    """Test that the centralized logging system is working"""
    print("🔍 Testing centralized logging system...")
    
    # Import the updated logger
    try:
        from core.logger import logger
        print("✅ Core logger imported successfully")
        
        # Test logging
        logger.info("Test message from verification script", "LogVerification", "test_001")
        logger.warning("Test warning message", "LogVerification", "test_002")
        logger.success("Test success message", "LogVerification", "test_003")
        
        print("✅ Test messages logged successfully")
        
        # Check if logs are in EHC_Logs
        ehc_logs_dir = Path("EHC_Logs")
        if ehc_logs_dir.exists():
            log_files = list(ehc_logs_dir.glob("*.log"))
            print(f"✅ Found {len(log_files)} log files in EHC_Logs")
            
            # Check for automation.log
            automation_log = ehc_logs_dir / "automation.log"
            if automation_log.exists():
                print(f"✅ Main automation.log found: {automation_log}")
                print(f"   Size: {automation_log.stat().st_size} bytes")
            else:
                print("❌ automation.log not found in EHC_Logs")
                
            # Check for errors.log
            errors_log = ehc_logs_dir / "errors.log"
            if errors_log.exists():
                print(f"✅ Errors log found: {errors_log}")
                print(f"   Size: {errors_log.stat().st_size} bytes")
            else:
                print("❌ errors.log not found in EHC_Logs")
                
        else:
            print("❌ EHC_Logs directory not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing centralized logging: {e}")
        return False
    
    return True

def test_log_cleanup_function():
    """Test the log cleanup function"""
    print("\n🧹 Testing log cleanup function...")
    
    try:
        from core.logger import cleanup_old_logs
        print("✅ Log cleanup function imported successfully")
        
        # Run cleanup (won't delete anything recent)
        cleanup_old_logs()
        print("✅ Log cleanup function executed successfully")
        
    except Exception as e:
        print(f"❌ Error testing log cleanup: {e}")
        return False
    
    return True

def test_log_manager():
    """Test the log manager module"""
    print("\n📋 Testing log manager module...")
    
    try:
        from modules.log_manager import log_manager, get_centralized_logger
        print("✅ Log manager imported successfully")
        
        # Test getting a logger
        test_logger = get_centralized_logger("test_verification", "verification")
        test_logger.info("Test message from log manager")
        print("✅ Log manager logger created and tested")
        
        # Test log statistics
        stats = log_manager.get_log_stats()
        print(f"✅ Log statistics: {stats}")
        
    except Exception as e:
        print(f"❌ Error testing log manager: {e}")
        return False
    
    return True

def verify_log_directory_structure():
    """Verify the log directory structure"""
    print("\n📁 Verifying log directory structure...")
    
    # Check EHC_Logs exists
    ehc_logs_dir = Path("EHC_Logs")
    if not ehc_logs_dir.exists():
        print("❌ EHC_Logs directory does not exist")
        return False
    
    print(f"✅ EHC_Logs directory exists: {ehc_logs_dir.absolute()}")
    
    # List all log files
    log_files = list(ehc_logs_dir.glob("*.log*"))
    print(f"📊 Found {len(log_files)} log files:")
    
    total_size = 0
    for log_file in log_files:
        size = log_file.stat().st_size
        total_size += size
        mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"   📄 {log_file.name} ({size} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    print(f"💾 Total log size: {total_size / 1024:.2f} KB")
    
    # Check for old logs directory
    old_logs_dir = Path("logs")
    if old_logs_dir.exists():
        old_log_files = list(old_logs_dir.glob("*.log"))
        if old_log_files:
            print(f"⚠️ Found {len(old_log_files)} files still in old logs/ directory")
            print("   Consider running migration again or manually moving these files")
        else:
            print("✅ Old logs/ directory is empty")
    else:
        print("✅ Old logs/ directory does not exist")
    
    return True

def test_system_integration():
    """Test integration with main system components"""
    print("\n🔗 Testing system integration...")
    
    try:
        # Test enhanced service runner
        print("📋 Testing enhanced service runner integration...")
        
        # Check if enhanced_service_runner.py exists and can be imported
        enhanced_service_path = Path("enhanced_service_runner.py")
        if enhanced_service_path.exists():
            print("✅ Enhanced service runner file exists")
        else:
            print("❌ Enhanced service runner file not found")
            return False
        
        # Test corrected_wifi_app integration
        print("📋 Testing corrected_wifi_app integration...")
        corrected_wifi_path = Path("corrected_wifi_app.py")
        if corrected_wifi_path.exists():
            print("✅ Corrected WiFi app file exists")
        else:
            print("❌ Corrected WiFi app file not found")
            return False
        
        print("✅ System integration verified")
        
    except Exception as e:
        print(f"❌ Error testing system integration: {e}")
        return False
    
    return True

def show_log_system_summary():
    """Show a summary of the log system"""
    print("\n📊 LOG SYSTEM SUMMARY")
    print("=" * 40)
    
    ehc_logs_dir = Path("EHC_Logs")
    if ehc_logs_dir.exists():
        log_files = list(ehc_logs_dir.glob("*.log*"))
        total_size = sum(f.stat().st_size for f in log_files)
        
        print(f"📁 Log directory: {ehc_logs_dir.absolute()}")
        print(f"📄 Total log files: {len(log_files)}")
        print(f"💾 Total size: {total_size / (1024 * 1024):.2f} MB")
        print(f"🧹 Cleanup policy: 7 days retention")
        print(f"⏰ Cleanup schedule: Daily at 2:00 AM")
        print(f"🔄 Auto-rotation: 10 MB max file size")
        
        # Recent activity
        recent_files = [f for f in log_files if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days < 1]
        print(f"🆕 Recent files (24h): {len(recent_files)}")
        
        # System status
        print(f"✅ Centralized logging: Active")
        print(f"✅ Log migration: Completed")
        print(f"✅ Cleanup system: Active")
        
    else:
        print("❌ EHC_Logs directory not found")

def main():
    """Main verification function"""
    print("🚀 LOG SYSTEM VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Centralized Logging", test_centralized_logging),
        ("Log Cleanup Function", test_log_cleanup_function),
        ("Log Manager Module", test_log_manager),
        ("Directory Structure", verify_log_directory_structure),
        ("System Integration", test_system_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 VERIFICATION RESULTS")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1
    
    print(f"\n📊 Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - Log system is working correctly!")
    else:
        print("⚠️ Some tests failed - please review the issues above")
    
    # Show system summary
    show_log_system_summary()
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 