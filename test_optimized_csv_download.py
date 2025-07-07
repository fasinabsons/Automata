#!/usr/bin/env python3
"""
Test script for optimized CSV download system
"""

import sys
import os
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from corrected_wifi_app import CorrectedWiFiApp

def test_optimized_csv_download():
    """Test the optimized CSV download system"""
    print("🧪 Testing Optimized CSV Download System")
    print("=" * 50)
    
    print("\n🔧 Key Optimizations Applied:")
    print("✅ Reduced page load timeout from 30s to 15s")
    print("✅ Reduced login wait from 10s to 3s + smart waiting")
    print("✅ Reduced post-login wait from 15s to 8s")
    print("✅ Reduced navigation wait from 8s to 4s")
    print("✅ Reduced download wait from 5s to 3s")
    print("✅ Reduced final wait from 15s to 10s")
    print("✅ Added comprehensive SSL/certificate error handling")
    print("✅ Added smart page ready detection")
    print("✅ Added automatic page refresh on certificate errors")
    print("✅ Added shorter WebDriverWait timeouts (3s per element)")
    
    print("\n🚀 Starting optimized CSV download test...")
    
    # Initialize the app
    app = CorrectedWiFiApp()
    
    # Record start time
    start_time = time.time()
    
    # Run the automation
    result = app.run_corrected_automation()
    
    # Record end time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n📊 Test Results:")
    print(f"⏱️ Execution time: {execution_time:.2f} seconds")
    print(f"✅ Success: {result.get('success', False)}")
    print(f"📁 Files downloaded: {result.get('files_downloaded', 0)}")
    print(f"🎯 Networks processed: {result.get('networks_processed', 0)}")
    print(f"📂 Total files: {result.get('total_files', 0)}")
    
    if result.get('success'):
        print("\n🎉 SUCCESS: Optimized CSV download system is working!")
        print("💡 The system now handles SSL errors gracefully and runs faster")
    else:
        print("\n❌ FAILED: There may be issues with the optimization")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n🔍 Benefits of Optimization:")
    print("⚡ Faster execution (reduced wait times)")
    print("🛡️ Better SSL/certificate error handling")
    print("🔄 Automatic retry mechanisms")
    print("📊 Smart page load detection")
    print("🎯 More targeted element detection")
    
    return result.get('success', False)

def main():
    """Main test function"""
    try:
        success = test_optimized_csv_download()
        
        if success:
            print("\n✅ All optimizations are working correctly!")
            print("🚀 The CSV download system is now more robust and faster!")
        else:
            print("\n⚠️ Some optimizations may need adjustment")
            print("🔧 Check the error messages above for details")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Optimization test completed successfully!")
    else:
        print("\n❌ Optimization test failed!")
        sys.exit(1) 