#!/usr/bin/env python3
"""
Efficient VBS Controller
Streamlined VBS automation controller for integration with enhanced service runner
Combines all VBS phases into a single efficient workflow
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logger import logger
from modules.vbs_app_controller import VBSAppController
from modules.vbs_login_handler import VBSLoginHandler

class EfficientVBSController:
    """
    Efficient VBS Controller for streamlined automation
    Integrates with enhanced service runner for complete workflow
    """
    
    def __init__(self):
        self.logger = logger
        self.app_controller = None
        self.login_handler = None
        self.is_initialized = False
        self.current_session = None
        
        # Configuration
        self.config = {
            "max_retries": 3,
            "retry_delay": 15,  # seconds
            "session_timeout": 1800,  # 30 minutes
            "auto_cleanup": True,
            "enable_screenshots": True
        }
        
        self.logger.info("Efficient VBS Controller initialized", "EfficientVBS")
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize VBS components"""
        try:
            self.logger.info("🔧 Initializing VBS components...", "EfficientVBS")
            
            # Initialize app controller
            self.app_controller = VBSAppController()
            
            # Initialize login handler
            self.login_handler = VBSLoginHandler(self.app_controller)
            
            self.is_initialized = True
            self.logger.info("✅ VBS components initialized successfully", "EfficientVBS")
            
            return {"success": True, "message": "VBS components initialized"}
            
        except Exception as e:
            error_msg = f"VBS initialization failed: {e}"
            self.logger.error(error_msg, "EfficientVBS")
            return {"success": False, "error": error_msg}
    
    def run_complete_vbs_automation(self, date_folder: str) -> Dict[str, Any]:
        """
        Run complete VBS automation workflow
        
        Args:
            date_folder: Date folder for Excel file processing (e.g., "03july")
            
        Returns:
            Dictionary with automation results
        """
        try:
            self.logger.info(f"🚀 Starting complete VBS automation for {date_folder}", "EfficientVBS")
            
            # Initialize if not already done
            if not self.is_initialized:
                init_result = self.initialize()
                if not init_result["success"]:
                    return init_result
            
            # Start session
            session_start = datetime.now()
            self.current_session = {
                "start_time": session_start,
                "date_folder": date_folder,
                "steps_completed": []
            }
            
            workflow_result = {
                "success": False,
                "date_folder": date_folder,
                "steps_completed": [],
                "errors": [],
                "start_time": session_start.isoformat(),
                "excel_file": None,
                "pdf_file": None
            }
            
            # STEP 1: Launch VBS Application
            self.logger.info("📱 STEP 1: Launching VBS Application", "EfficientVBS")
            launch_result = self._launch_application_with_retry()
            
            if not launch_result["success"]:
                workflow_result["errors"].append(f"Application launch failed: {launch_result['error']}")
                return workflow_result
            
            workflow_result["steps_completed"].append("application_launched")
            self.logger.info("✅ Step 1 completed: Application launched", "EfficientVBS")
            
            # STEP 2: Perform Login
            self.logger.info("🔐 STEP 2: Performing VBS Login", "EfficientVBS")
            login_result = self._perform_login_with_retry()
            
            if not login_result["success"]:
                workflow_result["errors"].append(f"Login failed: {login_result['error']}")
                return workflow_result
            
            workflow_result["steps_completed"].append("login_completed")
            self.logger.info("✅ Step 2 completed: Login successful", "EfficientVBS")
            
            # STEP 3: Navigate to WiFi Registration
            self.logger.info("🧭 STEP 3: Navigating to WiFi Registration", "EfficientVBS")
            navigation_result = self._navigate_to_wifi_registration()
            
            if not navigation_result["success"]:
                workflow_result["errors"].append(f"Navigation failed: {navigation_result['error']}")
                return workflow_result
            
            workflow_result["steps_completed"].append("navigation_completed")
            self.logger.info("✅ Step 3 completed: Navigation successful", "EfficientVBS")
            
            # STEP 4: Import Excel File
            self.logger.info("📊 STEP 4: Importing Excel File", "EfficientVBS")
            import_result = self._import_excel_file(date_folder)
            
            if not import_result["success"]:
                workflow_result["errors"].append(f"Excel import failed: {import_result['error']}")
                return workflow_result
            
            workflow_result["steps_completed"].append("excel_imported")
            workflow_result["excel_file"] = import_result.get("excel_file")
            self.logger.info("✅ Step 4 completed: Excel file imported", "EfficientVBS")
            
            # STEP 5: Generate PDF Report
            self.logger.info("📄 STEP 5: Generating PDF Report", "EfficientVBS")
            pdf_result = self._generate_pdf_report(date_folder)
            
            if not pdf_result["success"]:
                workflow_result["errors"].append(f"PDF generation failed: {pdf_result['error']}")
                return workflow_result
            
            workflow_result["steps_completed"].append("pdf_generated")
            workflow_result["pdf_file"] = pdf_result.get("pdf_file")
            self.logger.info("✅ Step 5 completed: PDF report generated", "EfficientVBS")
            
            # Mark workflow as successful
            workflow_result["success"] = True
            workflow_result["end_time"] = datetime.now().isoformat()
            workflow_result["total_duration"] = (datetime.now() - session_start).total_seconds()
            
            self.logger.info("🎉 Complete VBS automation workflow successful!", "EfficientVBS")
            self.logger.info(f"📊 Total duration: {workflow_result['total_duration']:.1f} seconds", "EfficientVBS")
            self.logger.info(f"📄 PDF file: {workflow_result['pdf_file']}", "EfficientVBS")
            
            # Cleanup if configured
            if self.config["auto_cleanup"]:
                self._cleanup_session()
            
            return workflow_result
            
        except Exception as e:
            error_msg = f"VBS automation workflow failed: {e}"
            self.logger.error(error_msg, "EfficientVBS")
            
            workflow_result["errors"].append(error_msg)
            workflow_result["end_time"] = datetime.now().isoformat()
            
            # Cleanup on error
            self._cleanup_session()
            
            return workflow_result
    
    def _launch_application_with_retry(self) -> Dict[str, Any]:
        """Launch VBS application with retry logic"""
        for attempt in range(self.config["max_retries"]):
            try:
                self.logger.info(f"🚀 Launch attempt {attempt + 1}/{self.config['max_retries']}", "EfficientVBS")
                
                launch_result = self.app_controller.launch_application()
                
                if launch_result["success"]:
                    self.logger.info("✅ Application launched successfully", "EfficientVBS")
                    return launch_result
                else:
                    self.logger.warning(f"Launch attempt {attempt + 1} failed: {launch_result['error']}", "EfficientVBS")
                    
                    if attempt < self.config["max_retries"] - 1:
                        self.logger.info(f"Retrying in {self.config['retry_delay']} seconds...", "EfficientVBS")
                        time.sleep(self.config["retry_delay"])
                    
            except Exception as e:
                self.logger.error(f"Launch attempt {attempt + 1} exception: {e}", "EfficientVBS")
                
                if attempt < self.config["max_retries"] - 1:
                    time.sleep(self.config["retry_delay"])
        
        return {"success": False, "error": "Application launch failed after all retry attempts"}
    
    def _perform_login_with_retry(self) -> Dict[str, Any]:
        """Perform VBS login with retry logic"""
        for attempt in range(self.config["max_retries"]):
            try:
                self.logger.info(f"🔐 Login attempt {attempt + 1}/{self.config['max_retries']}", "EfficientVBS")
                
                login_result = self.login_handler.perform_login()
                
                if login_result["success"]:
                    self.logger.info("✅ Login completed successfully", "EfficientVBS")
                    return login_result
                else:
                    self.logger.warning(f"Login attempt {attempt + 1} failed: {login_result['error']}", "EfficientVBS")
                    
                    if attempt < self.config["max_retries"] - 1:
                        self.logger.info(f"Retrying in {self.config['retry_delay']} seconds...", "EfficientVBS")
                        time.sleep(self.config["retry_delay"])
                    
            except Exception as e:
                self.logger.error(f"Login attempt {attempt + 1} exception: {e}", "EfficientVBS")
                
                if attempt < self.config["max_retries"] - 1:
                    time.sleep(self.config["retry_delay"])
        
        return {"success": False, "error": "Login failed after all retry attempts"}
    
    def _navigate_to_wifi_registration(self) -> Dict[str, Any]:
        """Navigate to WiFi User Registration"""
        try:
            self.logger.info("🧭 Navigating to WiFi User Registration...", "EfficientVBS")
            
            # Import navigation module
            from modules.vbs_automation_phase2 import VBSPhase2_Navigation
            
            # Create navigation instance
            navigation = VBSPhase2_Navigation(self.app_controller.window_handle)
            
            # Perform navigation
            nav_result = navigation.task_2_1_navigate_to_wifi_registration()
            
            if nav_result["success"]:
                self.logger.info("✅ Navigation completed successfully", "EfficientVBS")
                return nav_result
            else:
                self.logger.error(f"Navigation failed: {nav_result['error']}", "EfficientVBS")
                return nav_result
                
        except Exception as e:
            error_msg = f"Navigation exception: {e}"
            self.logger.error(error_msg, "EfficientVBS")
            return {"success": False, "error": error_msg}
    
    def _import_excel_file(self, date_folder: str) -> Dict[str, Any]:
        """Import Excel file into VBS"""
        try:
            self.logger.info(f"📊 Importing Excel file for {date_folder}...", "EfficientVBS")
            
            # Import Excel import module
            from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport
            
            # Create import instance
            excel_import = VBSPhase3_ExcelImport(self.app_controller.window_handle)
            
            # Perform Excel import
            import_result = excel_import.run_phase_3_complete(date_folder)
            
            if import_result["success"]:
                self.logger.info("✅ Excel import completed successfully", "EfficientVBS")
                return import_result
            else:
                self.logger.error(f"Excel import failed: {import_result['error']}", "EfficientVBS")
                return import_result
                
        except Exception as e:
            error_msg = f"Excel import exception: {e}"
            self.logger.error(error_msg, "EfficientVBS")
            return {"success": False, "error": error_msg}
    
    def _generate_pdf_report(self, date_folder: str) -> Dict[str, Any]:
        """Generate PDF report from VBS"""
        try:
            self.logger.info(f"📄 Generating PDF report for {date_folder}...", "EfficientVBS")
            
            # Import PDF generation module
            from modules.vbs_automation_phase4 import VBSPhase4_PDFGeneration
            
            # Create PDF generation instance
            pdf_gen = VBSPhase4_PDFGeneration(self.app_controller.window_handle)
            
            # Perform PDF generation
            pdf_result = pdf_gen.run_phase_4_complete(date_folder)
            
            if pdf_result["success"]:
                self.logger.info("✅ PDF generation completed successfully", "EfficientVBS")
                return pdf_result
            else:
                self.logger.error(f"PDF generation failed: {pdf_result['error']}", "EfficientVBS")
                return pdf_result
                
        except Exception as e:
            error_msg = f"PDF generation exception: {e}"
            self.logger.error(error_msg, "EfficientVBS")
            return {"success": False, "error": error_msg}
    
    def _cleanup_session(self):
        """Clean up VBS session"""
        try:
            self.logger.info("🧹 Cleaning up VBS session...", "EfficientVBS")
            
            # Close VBS application
            if self.app_controller:
                self.app_controller.close_application()
            
            # Reset session
            self.current_session = None
            
            self.logger.info("✅ VBS session cleanup completed", "EfficientVBS")
            
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {e}", "EfficientVBS")
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        if not self.current_session:
            return {"active": False, "message": "No active session"}
        
        return {
            "active": True,
            "start_time": self.current_session["start_time"].isoformat(),
            "date_folder": self.current_session["date_folder"],
            "steps_completed": self.current_session["steps_completed"],
            "duration": (datetime.now() - self.current_session["start_time"]).total_seconds()
        }
    
    def is_vbs_available(self) -> bool:
        """Check if VBS is available for automation"""
        try:
            if not self.is_initialized:
                return False
            
            if not self.app_controller:
                return False
            
            return self.app_controller.is_application_running()
            
        except Exception as e:
            self.logger.error(f"VBS availability check failed: {e}", "EfficientVBS")
            return False

def test_efficient_vbs_controller():
    """Test the efficient VBS controller"""
    print("🧪 Testing Efficient VBS Controller")
    print("=" * 50)
    
    controller = EfficientVBSController()
    
    # Test initialization
    print("\n1. Testing initialization...")
    init_result = controller.initialize()
    print(f"   Initialization result: {init_result}")
    
    # Test availability check
    print("\n2. Testing VBS availability...")
    available = controller.is_vbs_available()
    print(f"   VBS available: {available}")
    
    # Test complete workflow (with current date)
    from datetime import date
    today = date.today()
    test_date_folder = f"{today.day:02d}{today.strftime('%B').lower()}"
    
    print(f"\n3. Testing complete workflow for {test_date_folder}...")
    workflow_result = controller.run_complete_vbs_automation(test_date_folder)
    
    print(f"   Workflow success: {workflow_result['success']}")
    print(f"   Steps completed: {workflow_result['steps_completed']}")
    print(f"   Errors: {workflow_result['errors']}")
    
    print("\n✅ Efficient VBS Controller testing completed")

if __name__ == "__main__":
    test_efficient_vbs_controller() 