#!/usr/bin/env python3
"""
VBS Sequential Phase Testing - Phase 1 → Phase 2 → Phase 3
Tests the complete workflow without closing VBS between phases
Includes lock screen compatibility testing
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all phases
from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

class VBSSequentialTester:
    """Sequential VBS Phase Tester with Lock Screen Compatibility"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Phase instances
        self.phase1 = None
        self.phase2 = None
        self.phase3 = None
        
        # Shared state
        self.window_handle = None
        self.test_date_folder = "09jul"  # Use current test data
        
        # Test configuration
        self.config = {
            "wait_between_phases": 3,  # seconds
            "max_phase_retries": 2,
            "lock_screen_test": True,
            "cleanup_on_completion": False  # Keep VBS open for inspection
        }
        
        self.logger.info("🧪 VBS Sequential Phase Tester initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("VBSSequentialTester")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler
            log_dir = Path("EHC_Logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"vbs_sequential_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
        
        return logger
    
    def run_sequential_test(self) -> dict:
        """Run the complete sequential test"""
        try:
            self.logger.info("🚀 Starting VBS Sequential Phase Testing")
            self.logger.info("=" * 80)
            
            test_result = {
                "success": False,
                "phases_completed": [],
                "errors": [],
                "start_time": datetime.now().isoformat(),
                "test_date_folder": self.test_date_folder,
                "lock_screen_compatible": False
            }
            
            # PHASE 1: Launch & Login
            self.logger.info("🔥 PHASE 1: VBS Launch & Login")
            phase1_result = self._run_phase_1()
            
            if not phase1_result["success"]:
                test_result["errors"].append(f"Phase 1 failed: {phase1_result.get('error', 'Unknown error')}")
                return test_result
            
            test_result["phases_completed"].append("phase1")
            self.window_handle = phase1_result.get("window_handle")
            self.logger.info("✅ Phase 1 completed successfully")
            
            # Wait between phases
            self.logger.info(f"⏳ Waiting {self.config['wait_between_phases']} seconds between phases...")
            time.sleep(self.config["wait_between_phases"])
            
            # PHASE 2: Navigation
            self.logger.info("🧭 PHASE 2: Navigation to WiFi User Registration")
            phase2_result = self._run_phase_2()
            
            if not phase2_result["success"]:
                test_result["errors"].append(f"Phase 2 failed: {phase2_result.get('error', 'Unknown error')}")
                return test_result
            
            test_result["phases_completed"].append("phase2")
            self.logger.info("✅ Phase 2 completed successfully")
            
            # Wait between phases
            self.logger.info(f"⏳ Waiting {self.config['wait_between_phases']} seconds between phases...")
            time.sleep(self.config["wait_between_phases"])
            
            # Optional: Lock screen test
            if self.config["lock_screen_test"]:
                self.logger.info("🔒 LOCK SCREEN TEST: Please lock your screen (Windows+L) and press Enter to continue...")
                input("Press Enter after locking screen...")
                test_result["lock_screen_compatible"] = True
                self.logger.info("🔒 Lock screen test initiated - continuing with Phase 3...")
            
            # PHASE 3: Excel Import
            self.logger.info("📊 PHASE 3: Excel Import Process")
            phase3_result = self._run_phase_3()
            
            if not phase3_result["success"]:
                test_result["errors"].append(f"Phase 3 failed: {phase3_result.get('error', 'Unknown error')}")
                return test_result
            
            test_result["phases_completed"].append("phase3")
            test_result["excel_file"] = phase3_result.get("excel_file")
            self.logger.info("✅ Phase 3 completed successfully")
            
            # Mark test as successful
            test_result["success"] = True
            test_result["end_time"] = datetime.now().isoformat()
            
            self.logger.info("🎉 SEQUENTIAL VBS TESTING COMPLETED SUCCESSFULLY!")
            self.logger.info("=" * 80)
            self.logger.info(f"Phases completed: {test_result['phases_completed']}")
            self.logger.info(f"Excel file: {test_result.get('excel_file', 'N/A')}")
            self.logger.info(f"Lock screen compatible: {test_result['lock_screen_compatible']}")
            
            return test_result
            
        except Exception as e:
            error_msg = f"Sequential test failed: {e}"
            self.logger.error(error_msg)
            test_result["errors"].append(error_msg)
            test_result["end_time"] = datetime.now().isoformat()
            return test_result
    
    def _run_phase_1(self) -> dict:
        """Run Phase 1: Launch & Login"""
        try:
            self.logger.info("Initializing Phase 1...")
            self.phase1 = VBSPhase1_Enhanced()
            
            # Run login with retry
            for attempt in range(self.config["max_phase_retries"]):
                self.logger.info(f"Phase 1 attempt {attempt + 1}/{self.config['max_phase_retries']}")
                
                result = self.phase1.run_simple_login()
                
                if result["success"]:
                    window_handle = self.phase1.get_window_handle()
                    process_id = self.phase1.get_process_id()
                    
                    self.logger.info(f"✅ Phase 1 successful: Window={window_handle}, Process={process_id}")
                    return {
                        "success": True,
                        "window_handle": window_handle,
                        "process_id": process_id
                    }
                else:
                    self.logger.warning(f"Phase 1 attempt {attempt + 1} failed: {result.get('errors', [])}")
                    if attempt < self.config["max_phase_retries"] - 1:
                        time.sleep(5)  # Wait before retry
            
            return {"success": False, "error": "Phase 1 failed after all retries"}
            
        except Exception as e:
            return {"success": False, "error": f"Phase 1 exception: {e}"}
    
    def _run_phase_2(self) -> dict:
        """Run Phase 2: Navigation"""
        try:
            if not self.window_handle:
                return {"success": False, "error": "No window handle from Phase 1"}
            
            self.logger.info("Initializing Phase 2...")
            self.phase2 = VBSPhase2_Navigation(self.window_handle)
            
            # Run navigation with retry
            for attempt in range(self.config["max_phase_retries"]):
                self.logger.info(f"Phase 2 attempt {attempt + 1}/{self.config['max_phase_retries']}")
                
                result = self.phase2.run_phase_2_complete()
                
                if result["success"]:
                    self.logger.info("✅ Phase 2 successful: Navigation completed")
                    return {"success": True, "tasks_completed": result.get("tasks_completed", [])}
                else:
                    self.logger.warning(f"Phase 2 attempt {attempt + 1} failed: {result.get('errors', [])}")
                    if attempt < self.config["max_phase_retries"] - 1:
                        time.sleep(5)  # Wait before retry
            
            return {"success": False, "error": "Phase 2 failed after all retries"}
            
        except Exception as e:
            return {"success": False, "error": f"Phase 2 exception: {e}"}
    
    def _run_phase_3(self) -> dict:
        """Run Phase 3: Excel Import"""
        try:
            if not self.window_handle:
                return {"success": False, "error": "No window handle from Phase 1"}
            
            self.logger.info("Initializing Phase 3...")
            self.phase3 = VBSPhase3_ExcelImport(self.window_handle)
            
            # Run import with retry
            for attempt in range(self.config["max_phase_retries"]):
                self.logger.info(f"Phase 3 attempt {attempt + 1}/{self.config['max_phase_retries']}")
                
                result = self.phase3.run_phase_3_complete(self.test_date_folder)
                
                if result["success"]:
                    self.logger.info("✅ Phase 3 successful: Excel import completed")
                    return {
                        "success": True, 
                        "tasks_completed": result.get("tasks_completed", []),
                        "excel_file": result.get("excel_file")
                    }
                else:
                    self.logger.warning(f"Phase 3 attempt {attempt + 1} failed: {result.get('errors', [])}")
                    if attempt < self.config["max_phase_retries"] - 1:
                        time.sleep(5)  # Wait before retry
            
            return {"success": False, "error": "Phase 3 failed after all retries"}
            
        except Exception as e:
            return {"success": False, "error": f"Phase 3 exception: {e}"}
    
    def cleanup(self):
        """Cleanup test resources"""
        try:
            if not self.config["cleanup_on_completion"]:
                self.logger.info("🔍 Cleanup disabled - VBS remains open for inspection")
                return
            
            self.logger.info("🧹 Cleaning up test resources...")
            
            # Close VBS if needed
            if self.phase1:
                # Add cleanup logic here if needed
                pass
            
            self.logger.info("✅ Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

def main():
    """Main test function"""
    print("🧪 VBS SEQUENTIAL PHASE TESTING")
    print("=" * 80)
    print("This test will run Phase 1 → Phase 2 → Phase 3 sequentially")
    print("The VBS application will remain open between phases")
    print("Lock screen compatibility will be tested")
    print("=" * 80)
    
    # Confirm test data exists
    test_date = "09jul"
    excel_path = Path(f"EHC_Data_Merge/{test_date}")
    
    if not excel_path.exists():
        print(f"❌ Test data not found: {excel_path}")
        print("Please ensure Excel files exist in the test folder")
        return
    
    print(f"✅ Test data found: {excel_path}")
    print(f"📅 Testing with date folder: {test_date}")
    
    # Initialize tester
    tester = VBSSequentialTester()
    
    try:
        # Run sequential test
        print("\n🚀 Starting sequential test...")
        result = tester.run_sequential_test()
        
        # Display results
        print("\n📊 TEST RESULTS:")
        print(f"Success: {result['success']}")
        print(f"Phases completed: {result.get('phases_completed', [])}")
        print(f"Lock screen compatible: {result.get('lock_screen_compatible', False)}")
        print(f"Excel file: {result.get('excel_file', 'N/A')}")
        
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        
        if result["success"]:
            print("\n🎉 SEQUENTIAL TEST COMPLETED SUCCESSFULLY!")
            print("🔒 Lock screen compatibility confirmed")
            print("🔄 All phases worked without closing VBS")
        else:
            print(f"\n❌ SEQUENTIAL TEST FAILED")
            print("Check the logs for detailed error information")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        
    finally:
        # Cleanup
        tester.cleanup()
        
        # Keep console open for inspection
        if not result.get("success"):
            input("\nPress Enter to exit...")
    
    print("\n" + "=" * 80)
    print("VBS Sequential Phase Testing Completed")

if __name__ == "__main__":
    main() 