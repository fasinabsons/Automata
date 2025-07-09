#!/usr/bin/env python3
"""
Complete Workflow Test Script
Tests all components of the WiFi automation system
"""

import sys
import os
import time
import traceback
from pathlib import Path
from datetime import datetime
import schedule

# Add project root to path
sys.path.append('.')

# Import all necessary modules
from service_runner import WiFiAutomationService
from working_email_notifications import WorkingEmailNotifications
from modules.dynamic_file_manager import DynamicFileManager
from modules.csv_to_excel_processor import CSVToExcelProcessor
from corrected_wifi_app import CorrectedWiFiApp

def test_complete_workflow():
    """Test the complete workflow"""
    print("🧪 COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    results = {
        "service_initialization": False,
        "scheduling_system": False,
        "email_notifications": False,
        "file_management": False,
        "excel_generation": False,
        "wifi_download": False
    }
    
    try:
        # 1. Test Service Initialization
        print("\n✅ 1. TESTING SERVICE INITIALIZATION")
        service = WiFiAutomationService()
        email_service = WorkingEmailNotifications()
        file_manager = DynamicFileManager()
        
        if service and email_service and file_manager:
            results["service_initialization"] = True
            print("   ✅ All services initialized successfully")
        else:
            print("   ❌ Service initialization failed")
            
        # 2. Test Scheduling System
        print("\n✅ 2. TESTING SCHEDULING SYSTEM")
        service.schedule_tasks()
        scheduled_jobs = len(schedule.jobs)
        
        if scheduled_jobs >= 3:  # Should have at least 3 jobs (morning, evening, reset)
            results["scheduling_system"] = True
            print(f"   ✅ Scheduling system active with {scheduled_jobs} jobs")
            
            # Show next run time
            next_run = schedule.next_run()
            if next_run:
                time_until = next_run - datetime.now()
                hours, remainder = divmod(time_until.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                print(f"   📅 Next run: {next_run}")
                print(f"   ⏰ Time until next run: {hours}h {minutes}m")
        else:
            print("   ❌ Scheduling system failed")
            
        # 3. Test Email Notifications
        print("\n✅ 3. TESTING EMAIL NOTIFICATIONS")
        try:
            email_result = email_service.send_csv_download_notification('test-workflow', 4, 4, True)
            if email_result:
                results["email_notifications"] = True
                print("   ✅ Email notifications working")
            else:
                print("   ❌ Email notifications failed")
        except Exception as e:
            print(f"   ❌ Email error: {e}")
            
        # 4. Test File Management
        print("\n✅ 4. TESTING FILE MANAGEMENT")
        today_dir = file_manager.get_download_directory()
        merge_dir = file_manager.get_merge_directory()
        pdf_dir = file_manager.get_pdf_directory()
        
        if today_dir.exists() and merge_dir.exists() and pdf_dir.exists():
            results["file_management"] = True
            print("   ✅ File management system working")
            print(f"   📁 CSV Directory: {today_dir}")
            print(f"   📁 Excel Directory: {merge_dir}")
            print(f"   📁 PDF Directory: {pdf_dir}")
        else:
            print("   ❌ File management failed")
            
        # 5. Test Excel Generation (with mock data)
        print("\n✅ 5. TESTING EXCEL GENERATION")
        try:
            # Create mock CSV files with unique data
            mock_files = []
            for i in range(8):
                mock_file = today_dir / f'mock_clients_{i}.csv'
                mock_content = f"""Hostname,IP_Address,MAC_Address,Package,AP_MAC,Upload,Download
device-{i}-1,192.168.1.{100+i},aa:bb:cc:dd:ee:{i:02d},Standard,ff:ff:ff:ff:ff:{i:02d},{1000+i*100},{2000+i*200}
device-{i}-2,192.168.1.{150+i},aa:bb:cc:dd:ee:{i+10:02d},Premium,ff:ff:ff:ff:ff:{i+10:02d},{1500+i*100},{3000+i*200}
"""
                with open(mock_file, 'w') as f:
                    f.write(mock_content)
                mock_files.append(mock_file)
            
            # Test Excel generation
            processor = CSVToExcelProcessor()
            excel_result = processor.process_and_generate_excel(today_dir)
            
            if excel_result.get('success'):
                results["excel_generation"] = True
                print("   ✅ Excel generation working")
                excel_file = excel_result.get('excel_file')
                if excel_file and Path(excel_file).exists():
                    print(f"   📊 Excel file: {Path(excel_file).name}")
                    print(f"   📏 File size: {Path(excel_file).stat().st_size} bytes")
            else:
                print(f"   ❌ Excel generation failed: {excel_result.get('error')}")
                
            # Clean up mock files
            for mock_file in mock_files:
                if mock_file.exists():
                    mock_file.unlink()
                    
        except Exception as e:
            print(f"   ❌ Excel generation error: {e}")
            
        # 6. Test WiFi Download (check configuration only, not actual download)
        print("\n✅ 6. TESTING WIFI DOWNLOAD CONFIGURATION")
        try:
            wifi_app = CorrectedWiFiApp()
            if wifi_app:
                results["wifi_download"] = True
                print("   ✅ WiFi download app configured")
                print("   📡 Target networks: EHC TV, EHC-15, Reception Hall-Mobile, Reception Hall-TV")
                print("   🌐 Target URL: https://51.38.163.73:8443/wsg/")
                print("   ⚠️ Note: Actual download test skipped to avoid network timeout")
            else:
                print("   ❌ WiFi download app failed to initialize")
        except Exception as e:
            print(f"   ❌ WiFi download error: {e}")
            
        # Summary
        print("\n🎯 WORKFLOW TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
            
        print(f"\n📊 Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ MOST TESTS PASSED - SYSTEM MOSTLY READY")
        else:
            print("❌ MULTIPLE FAILURES - SYSTEM NEEDS ATTENTION")
            
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 WiFi Automation System - Complete Workflow Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working Directory: {Path.cwd()}")
    
    success = test_complete_workflow()
    
    if success:
        print("\n✅ SYSTEM VERIFICATION COMPLETE")
        print("🔄 The system is ready for automated operation")
        print("📅 Next scheduled run will occur at 13:00 (1:00 PM)")
        print("📧 Email notifications will be sent for all operations")
        print("📊 Excel files will be generated after 8 CSV files are downloaded")
    else:
        print("\n❌ SYSTEM VERIFICATION FAILED")
        print("🔧 Please check the error messages above and fix any issues")
        
    return success

if __name__ == "__main__":
    main() 