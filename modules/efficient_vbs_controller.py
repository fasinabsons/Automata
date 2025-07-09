#!/usr/bin/env python3
"""
Efficient VBS Controller - FIXED FOR VB6 APPLICATION
Streamlined VBS automation controller that properly targets VB6 application
Prevents interference with other applications like Excel
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import core modules
from core.logger import logger
from modules.vbs_app_controller import VBSAppController
from modules.vbs_automation_phase1 import VBSPhase1_LaunchLogin_Fixed  # FIXED: Use VB6 implementation
from modules.vbs_automation_phase2 import VBSPhase2_Navigation

class EfficientVBSController:
    """
    Efficient VBS Controller for VB6 Application - FIXED
    Ensures proper targeting of VB6 application without interfering with other apps
    """
    
    def __init__(self):
        self.logger = logger
        
        # Initialize VB6 automation phases
        self.phase1 = VBSPhase1_LaunchLogin_Fixed()  # FIXED: VB6 implementation
        self.phase2 = VBSPhase2_Navigation()
        
        # State tracking
        self.vb6_window_handle = None
        self.vb6_process_id = None
        self.current_phase = None
        
        # Configuration
        self.config = {
            "max_retries": 3,
            "retry_delay": 10,
            "phase_timeout": 300,  # 5 minutes per phase
            "vb6_stabilization_time": 5
        }
        
        self.logger.info("Efficient VBS Controller (VB6 FIXED) initialized", "EfficientVBSController")
    
    def run_vbs_automation(self, date_folder: str = None) -> Dict[str, Any]:
        """
        Run VBS automation for VB6 application
        
        Args:
            date_folder: Optional date folder for file operations
            
        Returns:
            Dictionary with automation results
        """
        try:
            self.logger.info("🚀 Starting VB6 automation workflow...", "EfficientVBSController")
            
            automation_result = {
                "success": False,
                "phases_completed": [],
                "errors": [],
                "start_time": datetime.now().isoformat(),
                "date_folder": date_folder,
                "vb6_window_handle": None,
                "vb6_process_id": None
            }
            
            # Phase 1: VB6 Application Launch & Login
            self.logger.info("🔥 Phase 1: VB6 Application Launch & Login", "EfficientVBSController")
            self.current_phase = "phase1"
            
            phase1_result = self._run_phase_with_retry(
                self.phase1.run_phase_1_complete_fixed,
                "VB6 Phase 1 (Launch & Login)"
            )
            
            if not phase1_result["success"]:
                automation_result["errors"].extend(phase1_result.get("errors", []))
                self.logger.error(f"❌ VB6 Phase 1 failed: {phase1_result.get('errors', [])}", "EfficientVBSController")
                return automation_result
            
            # Store VB6 window information
            self.vb6_window_handle = self.phase1.get_window_handle()
            self.vb6_process_id = self.phase1.get_process_id()
            
            automation_result["phases_completed"].append("phase1")
            automation_result["vb6_window_handle"] = self.vb6_window_handle
            automation_result["vb6_process_id"] = self.vb6_process_id
            
            self.logger.info(f"✅ VB6 Phase 1 completed successfully (Window: {self.vb6_window_handle}, PID: {self.vb6_process_id})", "EfficientVBSController")
            
            # Phase 2: VB6 Navigation
            self.logger.info("🧭 Phase 2: VB6 Navigation", "EfficientVBSController")
            self.current_phase = "phase2"
            
            # Set window handle for Phase 2
            self.phase2.set_window_handle(self.vb6_window_handle)
            
            phase2_result = self._run_phase_with_retry(
                self.phase2.run_phase_2_complete,
                "VB6 Phase 2 (Navigation)"
            )
            
            if not phase2_result["success"]:
                automation_result["errors"].extend(phase2_result.get("errors", []))
                self.logger.error(f"❌ VB6 Phase 2 failed: {phase2_result.get('errors', [])}", "EfficientVBSController")
                return automation_result
            
            automation_result["phases_completed"].append("phase2")
            self.logger.info("✅ VB6 Phase 2 completed successfully", "EfficientVBSController")
            
            # Mark automation as successful
            automation_result["success"] = True
            automation_result["end_time"] = datetime.now().isoformat()
            
            self.logger.info("🎉 VB6 automation workflow completed successfully!", "EfficientVBSController")
            
            return automation_result
            
        except Exception as e:
            error_msg = f"VB6 automation workflow failed: {e}"
            self.logger.error(error_msg, "EfficientVBSController")
            
            automation_result["errors"].append(error_msg)
            automation_result["end_time"] = datetime.now().isoformat()
            
            return automation_result
    
    def _run_phase_with_retry(self, phase_func, phase_name: str) -> Dict[str, Any]:
        """Run a VB6 phase with retry logic"""
        for attempt in range(self.config["max_retries"]):
            try:
                self.logger.info(f"Attempting {phase_name} (attempt {attempt + 1}/{self.config['max_retries']})", "EfficientVBSController")
                
                result = phase_func()
                
                if result["success"]:
                    self.logger.info(f"✅ {phase_name} completed successfully", "EfficientVBSController")
                    return result
                else:
                    self.logger.warning(f"⚠️ {phase_name} failed on attempt {attempt + 1}: {result.get('errors', [])}", "EfficientVBSController")
                    
                    if attempt < self.config["max_retries"] - 1:
                        self.logger.info(f"🔄 Retrying {phase_name} in {self.config['retry_delay']} seconds...", "EfficientVBSController")
                        time.sleep(self.config["retry_delay"])
                    else:
                        self.logger.error(f"❌ {phase_name} failed after {self.config['max_retries']} attempts", "EfficientVBSController")
                        return result
                        
            except Exception as e:
                error_msg = f"{phase_name} attempt {attempt + 1} failed with exception: {e}"
                self.logger.error(error_msg, "EfficientVBSController")
                
                if attempt < self.config["max_retries"] - 1:
                    self.logger.info(f"🔄 Retrying {phase_name} in {self.config['retry_delay']} seconds...", "EfficientVBSController")
                    time.sleep(self.config["retry_delay"])
                else:
                    return {"success": False, "errors": [error_msg]}
        
        return {"success": False, "errors": [f"{phase_name} failed after all retry attempts"]}
    
    def get_vb6_window_handle(self) -> Optional[int]:
        """Get current VB6 window handle"""
        return self.vb6_window_handle
    
    def get_vb6_process_id(self) -> Optional[int]:
        """Get current VB6 process ID"""
        return self.vb6_process_id
    
    def get_current_phase(self) -> Optional[str]:
        """Get current automation phase"""
        return self.current_phase
    
    def is_vb6_application_ready(self) -> bool:
        """Check if VB6 application is ready for automation"""
        try:
            if not self.vb6_window_handle:
                return False
            
            # Check if VB6 window is still valid
            import win32gui
            if not win32gui.IsWindow(self.vb6_window_handle):
                return False
            
            if not win32gui.IsWindowVisible(self.vb6_window_handle):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"VB6 application readiness check failed: {e}", "EfficientVBSController")
            return False
    
    def cleanup_vb6_automation(self):
        """Cleanup VB6 automation resources"""
        try:
            self.logger.info("🧹 Cleaning up VB6 automation resources...", "EfficientVBSController")
            
            # Close VB6 application if needed
            if self.vb6_window_handle:
                try:
                    import win32gui
                    import win32con
                    win32gui.PostMessage(self.vb6_window_handle, win32con.WM_CLOSE, 0, 0)
                    time.sleep(2)
                except:
                    pass
            
            # Reset state
            self.vb6_window_handle = None
            self.vb6_process_id = None
            self.current_phase = None
            
            self.logger.info("✅ VB6 automation cleanup completed", "EfficientVBSController")
            
        except Exception as e:
            self.logger.error(f"VB6 automation cleanup failed: {e}", "EfficientVBSController")

# Test function
def test_efficient_vb6_controller():
    """Test the efficient VB6 controller"""
    print("🧪 Testing Efficient VB6 Controller")
    print("=" * 60)
    
    controller = EfficientVBSController()
    
    try:
        # Test VB6 automation
        print("\n1. Testing VB6 automation workflow...")
        result = controller.run_vbs_automation()
        
        print(f"\n📊 Results:")
        print(f"   Success: {result['success']}")
        print(f"   Phases completed: {result.get('phases_completed', [])}")
        print(f"   VB6 Window Handle: {result.get('vb6_window_handle')}")
        print(f"   VB6 Process ID: {result.get('vb6_process_id')}")
        print(f"   Errors: {result.get('errors', [])}")
        
        if result["success"]:
            print("\n✅ VB6 automation completed successfully!")
            
            # Test readiness check
            print("\n2. Testing VB6 application readiness...")
            if controller.is_vb6_application_ready():
                print("✅ VB6 application is ready for further automation")
            else:
                print("❌ VB6 application is not ready")
        else:
            print(f"\n❌ VB6 automation failed: {result.get('errors', [])}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        # Cleanup
        controller.cleanup_vb6_automation()
        
    print("\n" + "=" * 60)
    print("Efficient VB6 Controller Test Completed")

if __name__ == "__main__":
    test_efficient_vb6_controller() 