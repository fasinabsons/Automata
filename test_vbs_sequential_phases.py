#!/usr/bin/env python3
"""
VBS Sequential Phases Test - Complete Background Operation
Tests Phase 1 → Phase 2 → Phase 3 with proper window handle management
Ensures background operation without interfering with other applications
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback
import win32gui
import win32con
import win32process
import ctypes
from ctypes import wintypes

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport

class VBSSequentialTester:
    """Test VBS phases sequentially with proper background operation"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.window_handle: Optional[int] = None
        self.process_id: Optional[int] = None
        
        # Phase instances
        self.phase1 = VBSPhase1_Enhanced()
        self.phase2 = VBSPhase2_Navigation()
        self.phase3 = VBSPhase3_ExcelImport()
        
        # Test configuration
        self.config = {
            "test_date_folder": "09jul",
            "inter_phase_delay": 3,  # seconds between phases
            "max_retries": 2,
            "enable_lock_screen_test": False,  # Set to True to test lock screen compatibility
            "keep_vbs_open": True,  # Keep VBS open for inspection
        }
        
        self.logger.info("VBS Sequential Tester initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging for testing"""
        logger = logging.getLogger("VBSSequentialTest")
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
            
            logger.info(f"Test logging to: {log_file}")
        
        return logger
    
    def run_sequential_test(self) -> Dict[str, Any]:
        """Run complete sequential test: Phase 1 → Phase 2 → Phase 3"""
        try:
            self.logger.info("🚀 Starting VBS Sequential Phases Test")
            self.logger.info("=" * 80)
            
            test_result = {
                "success": False,
                "phases_completed": [],
                "errors": [],
                "start_time": datetime.now().isoformat(),
                "test_date_folder": self.config["test_date_folder"],
                "window_handle": None,
                "process_id": None,
                "excel_file": None,
                "lock_screen_tested": False
            }
            
            # Optional: Test lock screen compatibility
            if self.config["enable_lock_screen_test"]:
                self.logger.info("🔒 Testing lock screen compatibility...")
                self._test_lock_screen_compatibility()
                test_result["lock_screen_tested"] = True
            
            # PHASE 1: Application Launch & Login
            self.logger.info("🔥 PHASE 1: Application Launch & Login")
            self.logger.info("-" * 50)
            
            phase1_result = self._run_phase_with_retry(
                self._execute_phase1,
                "Phase 1 (Launch & Login)"
            )
            
            if not phase1_result["success"]:
                test_result["errors"].extend(phase1_result["errors"])
                return test_result
            
            test_result["phases_completed"].append("phase1")
            self.window_handle = phase1_result["window_handle"]
            self.process_id = phase1_result["process_id"]
            test_result["window_handle"] = self.window_handle
            test_result["process_id"] = self.process_id
            
            self.logger.info("✅ Phase 1 completed successfully")
            self.logger.info(f"Window Handle: {self.window_handle}")
            self.logger.info(f"Process ID: {self.process_id}")
            
            # Inter-phase delay
            time.sleep(self.config["inter_phase_delay"])
            
            # PHASE 2: Navigation
            self.logger.info("🧭 PHASE 2: Navigation to WiFi User Registration")
            self.logger.info("-" * 50)
            
            phase2_result = self._run_phase_with_retry(
                self._execute_phase2,
                "Phase 2 (Navigation)"
            )
            
            if not phase2_result["success"]:
                test_result["errors"].extend(phase2_result["errors"])
                return test_result
            
            test_result["phases_completed"].append("phase2")
            self.logger.info("✅ Phase 2 completed successfully")
            
            # Inter-phase delay
            time.sleep(self.config["inter_phase_delay"])
            
            # PHASE 3: Excel Import
            self.logger.info("📊 PHASE 3: Excel Import Process")
            self.logger.info("-" * 50)
            
            phase3_result = self._run_phase_with_retry(
                self._execute_phase3,
                "Phase 3 (Excel Import)"
            )
            
            if not phase3_result["success"]:
                test_result["errors"].extend(phase3_result["errors"])
                return test_result
            
            test_result["phases_completed"].append("phase3")
            test_result["excel_file"] = phase3_result.get("excel_file")
            self.logger.info("✅ Phase 3 completed successfully")
            
            # Mark test as successful
            test_result["success"] = True
            test_result["end_time"] = datetime.now().isoformat()
            
            self.logger.info("🎉 SEQUENTIAL TEST COMPLETED SUCCESSFULLY!")
            self.logger.info("=" * 80)
            self.logger.info(f"Phases completed: {test_result['phases_completed']}")
            self.logger.info(f"Excel file: {test_result['excel_file']}")
            self.logger.info(f"Window handle maintained: {self.window_handle}")
            
            # Keep VBS open for inspection if configured
            if self.config["keep_vbs_open"]:
                self.logger.info("🔍 Keeping VBS open for inspection...")
                self.logger.info("Press Ctrl+C to close VBS and exit test")
                try:
                    while True:
                        time.sleep(1)
                        # Check if VBS is still running
                        if not self._is_vbs_still_running():
                            self.logger.info("VBS application was closed externally")
                            break
                except KeyboardInterrupt:
                    self.logger.info("Test interrupted by user")
                    self._cleanup_vbs()
            
            return test_result
            
        except Exception as e:
            error_msg = f"Sequential test failed: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            test_result["errors"].append(error_msg)
            test_result["end_time"] = datetime.now().isoformat()
            
            return test_result
    
    def _execute_phase1(self) -> Dict[str, Any]:
        """Execute Phase 1: Application Launch & Login"""
        try:
            self.logger.info("Executing Phase 1: Application Launch & Login")
            
            # Run Phase 1
            result = self.phase1.run_simple_login()
            
            if result["success"]:
                # Get window handle and process ID
                window_handle = self.phase1.get_window_handle()
                process_id = self.phase1.get_process_id()
                
                if window_handle:
                    self.logger.info(f"Phase 1 successful - Window: {window_handle}, Process: {process_id}")
                    return {
                        "success": True,
                        "window_handle": window_handle,
                        "process_id": process_id,
                        "message": "Phase 1 completed successfully"
                    }
                else:
                    return {
                        "success": False,
                        "errors": ["Phase 1 succeeded but no window handle available"]
                    }
            else:
                return {
                    "success": False,
                    "errors": result.get("errors", ["Phase 1 failed"])
                }
                
        except Exception as e:
            error_msg = f"Phase 1 execution failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "errors": [error_msg]}
    
    def _execute_phase2(self) -> Dict[str, Any]:
        """Execute Phase 2: Navigation"""
        try:
            self.logger.info("Executing Phase 2: Navigation")
            
            if not self.window_handle:
                return {"success": False, "errors": ["No window handle available for Phase 2"]}
            
            # Set window handle for Phase 2
            self.phase2.set_window_handle(self.window_handle)
            
            # Run Phase 2
            result = self.phase2.run_phase_2_complete()
            
            if result["success"]:
                self.logger.info("Phase 2 completed successfully")
                return {
                    "success": True,
                    "message": "Phase 2 completed successfully",
                    "tasks_completed": result.get("tasks_completed", [])
                }
            else:
                return {
                    "success": False,
                    "errors": result.get("errors", ["Phase 2 failed"])
                }
                
        except Exception as e:
            error_msg = f"Phase 2 execution failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "errors": [error_msg]}
    
    def _execute_phase3(self) -> Dict[str, Any]:
        """Execute Phase 3: Excel Import"""
        try:
            self.logger.info("Executing Phase 3: Excel Import")
            
            if not self.window_handle:
                return {"success": False, "errors": ["No window handle available for Phase 3"]}
            
            # Set window handle for Phase 3
            self.phase3.set_window_handle(self.window_handle)
            
            # Run Phase 3
            result = self.phase3.run_phase_3_complete(self.config["test_date_folder"])
            
            if result["success"]:
                self.logger.info("Phase 3 completed successfully")
                return {
                    "success": True,
                    "message": "Phase 3 completed successfully",
                    "tasks_completed": result.get("tasks_completed", []),
                    "excel_file": result.get("excel_file")
                }
            else:
                return {
                    "success": False,
                    "errors": result.get("errors", ["Phase 3 failed"])
                }
                
        except Exception as e:
            error_msg = f"Phase 3 execution failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "errors": [error_msg]}
    
    def _run_phase_with_retry(self, phase_func, phase_name: str) -> Dict[str, Any]:
        """Run a phase with retry logic"""
        for attempt in range(self.config["max_retries"]):
            try:
                self.logger.info(f"Attempting {phase_name} (attempt {attempt + 1}/{self.config['max_retries']})")
                
                result = phase_func()
                
                if result["success"]:
                    return result
                else:
                    self.logger.warning(f"{phase_name} failed on attempt {attempt + 1}: {result.get('errors', [])}")
                    
                    if attempt < self.config["max_retries"] - 1:
                        self.logger.info(f"Retrying {phase_name} in 5 seconds...")
                        time.sleep(5)
                    else:
                        self.logger.error(f"{phase_name} failed after {self.config['max_retries']} attempts")
                        return result
                        
            except Exception as e:
                error_msg = f"{phase_name} attempt {attempt + 1} failed with exception: {e}"
                self.logger.error(error_msg)
                
                if attempt < self.config["max_retries"] - 1:
                    self.logger.info(f"Retrying {phase_name} in 5 seconds...")
                    time.sleep(5)
                else:
                    return {"success": False, "errors": [error_msg]}
        
        return {"success": False, "errors": [f"{phase_name} failed after all retry attempts"]}
    
    def _test_lock_screen_compatibility(self):
        """Test lock screen compatibility"""
        try:
            self.logger.info("🔒 Testing lock screen compatibility...")
            
            # Simulate lock screen (Windows+L)
            self.logger.info("Simulating Windows+L lock screen...")
            ctypes.windll.user32.LockWorkStation()
            
            time.sleep(3)
            
            # Unlock screen (this would normally require user interaction)
            self.logger.info("⚠️ Lock screen test activated - manual unlock required")
            
        except Exception as e:
            self.logger.error(f"Lock screen test failed: {e}")
    
    def _is_vbs_still_running(self) -> bool:
        """Check if VBS is still running"""
        try:
            if self.window_handle and win32gui.IsWindow(self.window_handle):
                return win32gui.IsWindowVisible(self.window_handle)
            return False
        except:
            return False
    
    def _cleanup_vbs(self):
        """Clean up VBS application"""
        try:
            if self.window_handle:
                self.logger.info("Closing VBS application...")
                win32gui.PostMessage(self.window_handle, win32con.WM_CLOSE, 0, 0)
                time.sleep(2)
        except Exception as e:
            self.logger.error(f"VBS cleanup failed: {e}")
    
    def run_individual_phase_tests(self):
        """Run individual phase tests for debugging"""
        self.logger.info("🔧 Running individual phase tests...")
        
        # Test Phase 1 only
        print("\n" + "="*50)
        print("TESTING PHASE 1 ONLY")
        print("="*50)
        
        phase1_result = self._execute_phase1()
        print(f"Phase 1 Result: {phase1_result}")
        
        if phase1_result["success"]:
            self.window_handle = phase1_result["window_handle"]
            
            # Test Phase 2 only
            print("\n" + "="*50)
            print("TESTING PHASE 2 ONLY")
            print("="*50)
            
            time.sleep(3)
            phase2_result = self._execute_phase2()
            print(f"Phase 2 Result: {phase2_result}")
            
            if phase2_result["success"]:
                # Test Phase 3 only
                print("\n" + "="*50)
                print("TESTING PHASE 3 ONLY")
                print("="*50)
                
                time.sleep(3)
                phase3_result = self._execute_phase3()
                print(f"Phase 3 Result: {phase3_result}")
        
        # Keep VBS open for inspection
        if self.config["keep_vbs_open"]:
            input("\nPress Enter to close VBS and exit...")
            self._cleanup_vbs()

def main():
    """Main test function"""
    print("🧪 VBS Sequential Phases Test")
    print("=" * 80)
    print("This test will run Phase 1 → Phase 2 → Phase 3 sequentially")
    print("Ensuring proper background operation without affecting other apps")
    print("=" * 80)
    
    # Create tester instance
    tester = VBSSequentialTester()
    
    # Ask user for test type
    print("\nSelect test type:")
    print("1. Full sequential test (Phase 1 → 2 → 3)")
    print("2. Individual phase tests (for debugging)")
    print("3. Lock screen compatibility test")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            # Run full sequential test
            result = tester.run_sequential_test()
            
            print("\n" + "="*80)
            print("SEQUENTIAL TEST RESULTS")
            print("="*80)
            print(f"Success: {result['success']}")
            print(f"Phases completed: {result['phases_completed']}")
            print(f"Errors: {result.get('errors', [])}")
            print(f"Window handle: {result.get('window_handle')}")
            print(f"Excel file: {result.get('excel_file')}")
            
        elif choice == "2":
            # Run individual phase tests
            tester.run_individual_phase_tests()
            
        elif choice == "3":
            # Run lock screen test
            tester.config["enable_lock_screen_test"] = True
            result = tester.run_sequential_test()
            print(f"Lock screen test result: {result}")
            
        else:
            print("Invalid choice. Running full sequential test...")
            result = tester.run_sequential_test()
            print(f"Test result: {result}")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        tester._cleanup_vbs()
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()
        tester._cleanup_vbs()

if __name__ == "__main__":
    main() 