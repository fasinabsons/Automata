#!/usr/bin/env python3
"""
VBS Master Orchestrator - Complete Automation Workflow
Combines all phases: Launch → Login → Navigation → Import → PDF Generation → Email
"""

import os
import sys
import time
import logging
from datetime import datetime, date
from typing import Dict, Optional, Any
import traceback
from pathlib import Path

# Import all phase modules
from modules.vbs_automation_phase1 import VBSPhase1_Enhanced
from modules.vbs_automation_phase2 import VBSPhase2_Navigation
from modules.vbs_automation_phase3 import VBSPhase3_ExcelImport
from modules.vbs_automation_phase4 import VBSPhase4_PDFGeneration
from modules.email_service import EmailService

class VBSMasterOrchestrator:
    """Master orchestrator for complete VBS automation workflow"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Phase instances
        self.phase1 = VBSPhase1_Enhanced()
        self.phase2 = VBSPhase2_Navigation()
        self.phase3 = VBSPhase3_ExcelImport()
        self.phase4 = VBSPhase4_PDFGeneration()
        self.email_service = EmailService()
        
        # Workflow state
        self.window_handle: Optional[int] = None
        self.current_phase = None
        self.workflow_start_time = None
        
        # Configuration
        self.config = {
            "max_retries": 3,
            "retry_delay": 30,  # seconds
            "phase_timeout": 3600,  # 1 hour per phase
            "email_on_success": True,
            "email_on_failure": True,
            "cleanup_on_completion": True
        }
        
        self.logger.info("VBS Master Orchestrator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("VBSMasterOrchestrator")
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
            
            log_file = log_dir / f"vbs_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
        
        return logger
    
    def run_complete_workflow(self, date_folder: str) -> Dict[str, Any]:
        """Run the complete VBS automation workflow"""
        try:
            self.workflow_start_time = datetime.now()
            self.logger.info(f"🚀 Starting complete VBS automation workflow for {date_folder}")
            self.logger.info("=" * 80)
            
            workflow_result = {
                "success": False,
                "phases_completed": [],
                "errors": [],
                "start_time": self.workflow_start_time.isoformat(),
                "date_folder": date_folder,
                "excel_file": None,
                "pdf_file": None,
                "email_sent": False
            }
            
            # PHASE 1: Application Launch & Login
            self.logger.info("🔥 PHASE 1: Application Launch & Login")
            self.current_phase = "phase1"
            phase1_result = self._run_phase_with_retry(
                self.phase1.run_simple_login, 
                "Phase 1 (Launch & Login)"
            )
            
            if not phase1_result["success"]:
                workflow_result["errors"].extend(phase1_result["errors"])
                self._send_failure_email(workflow_result, "Phase 1 failed")
                return workflow_result
            
            workflow_result["phases_completed"].append("phase1")
            self.window_handle = self.phase1.get_window_handle()
            self.logger.info("✅ Phase 1 completed successfully")
            
            # Check if window handle is valid before proceeding
            if self.window_handle is None:
                error_msg = "Phase 1 completed but no valid window handle available"
                workflow_result["errors"].append(error_msg)
                self._send_failure_email(workflow_result, error_msg)
                return workflow_result
            
            # PHASE 2: Navigation
            self.logger.info("🧭 PHASE 2: Navigation to WiFi User Registration")
            self.current_phase = "phase2"
            self.phase2.set_window_handle(self.window_handle)
            phase2_result = self._run_phase_with_retry(
                self.phase2.run_phase_2_complete,
                "Phase 2 (Navigation)"
            )
            
            if not phase2_result["success"]:
                workflow_result["errors"].extend(phase2_result["errors"])
                self._send_failure_email(workflow_result, "Phase 2 failed")
                return workflow_result
            
            workflow_result["phases_completed"].append("phase2")
            self.logger.info("✅ Phase 2 completed successfully")
            
            # PHASE 3: Excel Import
            self.logger.info("📊 PHASE 3: Excel Import Process")
            self.current_phase = "phase3"
            self.phase3.set_window_handle(self.window_handle)
            phase3_result = self._run_phase_with_retry(
                lambda: self.phase3.run_phase_3_complete(date_folder),
                "Phase 3 (Excel Import)"
            )
            
            if not phase3_result["success"]:
                workflow_result["errors"].extend(phase3_result["errors"])
                self._send_failure_email(workflow_result, "Phase 3 failed")
                return workflow_result
            
            workflow_result["phases_completed"].append("phase3")
            workflow_result["excel_file"] = phase3_result.get("excel_file")
            self.logger.info("✅ Phase 3 completed successfully")
            
            # PHASE 4: PDF Generation
            self.logger.info("📄 PHASE 4: PDF Generation")
            self.current_phase = "phase4"
            self.phase4.set_window_handle(self.window_handle)
            phase4_result = self._run_phase_with_retry(
                lambda: self.phase4.run_phase_4_complete(date_folder),
                "Phase 4 (PDF Generation)"
            )
            
            if not phase4_result["success"]:
                workflow_result["errors"].extend(phase4_result["errors"])
                self._send_failure_email(workflow_result, "Phase 4 failed")
                return workflow_result
            
            workflow_result["phases_completed"].append("phase4")
            workflow_result["pdf_file"] = phase4_result.get("pdf_path")
            self.logger.info("✅ Phase 4 completed successfully")
            
            # PHASE 5: Email Notification
            self.logger.info("📧 PHASE 5: Email Notification")
            self.current_phase = "phase5"
            email_result = self._send_success_email(workflow_result)
            
            if email_result["success"]:
                workflow_result["email_sent"] = True
                workflow_result["phases_completed"].append("phase5")
                self.logger.info("✅ Phase 5 completed successfully")
            else:
                workflow_result["errors"].append(f"Email notification failed: {email_result['error']}")
                # Don't fail entire workflow for email issues
                self.logger.warning("⚠️ Email notification failed, but workflow continues")
            
            # Mark workflow as successful
            workflow_result["success"] = True
            workflow_result["end_time"] = datetime.now().isoformat()
            workflow_result["total_duration"] = (datetime.now() - self.workflow_start_time).total_seconds()
            
            self.logger.info("🎉 COMPLETE VBS AUTOMATION WORKFLOW SUCCESSFUL!")
            self.logger.info("=" * 80)
            self.logger.info(f"Total duration: {workflow_result['total_duration']:.1f} seconds")
            self.logger.info(f"Excel file: {workflow_result['excel_file']}")
            self.logger.info(f"PDF file: {workflow_result['pdf_file']}")
            self.logger.info(f"Email sent: {workflow_result['email_sent']}")
            
            # Cleanup if configured
            if self.config["cleanup_on_completion"]:
                self._cleanup_workflow()
            
            return workflow_result
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            workflow_result["errors"].append(error_msg)
            workflow_result["end_time"] = datetime.now().isoformat()
            
            # Send failure email
            self._send_failure_email(workflow_result, "Workflow execution failed")
            
            return workflow_result
    
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
                        self.logger.info(f"Retrying {phase_name} in {self.config['retry_delay']} seconds...")
                        time.sleep(self.config["retry_delay"])
                    else:
                        self.logger.error(f"{phase_name} failed after {self.config['max_retries']} attempts")
                        return result
                        
            except Exception as e:
                error_msg = f"{phase_name} attempt {attempt + 1} failed with exception: {e}"
                self.logger.error(error_msg)
                
                if attempt < self.config["max_retries"] - 1:
                    self.logger.info(f"Retrying {phase_name} in {self.config['retry_delay']} seconds...")
                    time.sleep(self.config["retry_delay"])
                else:
                    return {"success": False, "errors": [error_msg]}
        
        return {"success": False, "errors": [f"{phase_name} failed after all retry attempts"]}
    
    def _send_success_email(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Send success email notification"""
        try:
            if not self.config["email_on_success"]:
                return {"success": True, "message": "Email notifications disabled"}
            
            # Prepare email content
            subject = f"✅ VBS Automation Successful - {workflow_result['date_folder']}"
            
            body = f"""
            🎉 VBS Automation Workflow Completed Successfully!
            
            📊 Workflow Details:
            • Date Folder: {workflow_result['date_folder']}
            • Start Time: {workflow_result['start_time']}
            • End Time: {workflow_result['end_time']}
            • Duration: {workflow_result.get('total_duration', 0):.1f} seconds
            
            ✅ Phases Completed:
            {chr(10).join([f"• {phase}" for phase in workflow_result['phases_completed']])}
            
            📁 Files Generated:
            • Excel File: {workflow_result.get('excel_file', 'N/A')}
            • PDF File: {workflow_result.get('pdf_file', 'N/A')}
            
            🏢 MoonFlower Hotel WiFi Management System
            Automated by VBS Integration
            """
            
            # Send email with proper attachment handling
            attachments = []
            if workflow_result.get('pdf_file'):
                attachments.append(Path(workflow_result['pdf_file']))
            
            # Send email
            try:
                email_sent = self.email_service.send_email(
                    subject=subject,
                    body=body,
                    attachments=attachments if attachments else None
                )
                
                if email_sent:
                    return {"success": True, "message": "Success email sent"}
                else:
                    return {"success": False, "error": "Email service returned False"}
                    
            except Exception as e:
                return {"success": False, "error": f"Email sending failed: {e}"}
            
        except Exception as e:
            error_msg = f"Success email failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _send_failure_email(self, workflow_result: Dict[str, Any], failure_reason: str) -> Dict[str, Any]:
        """Send failure email notification"""
        try:
            if not self.config["email_on_failure"]:
                return {"success": True, "message": "Email notifications disabled"}
            
            # Prepare email content
            subject = f"❌ VBS Automation Failed - {workflow_result['date_folder']}"
            
            body = f"""
            ❌ VBS Automation Workflow Failed
            
            🚨 Failure Reason: {failure_reason}
            
            📊 Workflow Details:
            • Date Folder: {workflow_result['date_folder']}
            • Start Time: {workflow_result['start_time']}
            • Current Phase: {self.current_phase}
            
            ✅ Phases Completed:
            {chr(10).join([f"• {phase}" for phase in workflow_result['phases_completed']]) if workflow_result['phases_completed'] else '• None'}
            
            ❌ Errors:
            {chr(10).join([f"• {error}" for error in workflow_result['errors']]) if workflow_result['errors'] else '• No specific errors recorded'}
            
            🔧 Please check the system and retry the automation process.
            
            🏢 MoonFlower Hotel WiFi Management System
            Automated by VBS Integration
            """
            
            # Send email
            try:
                email_sent = self.email_service.send_email(
                    subject=subject,
                    body=body
                )
                
                if email_sent:
                    return {"success": True, "message": "Failure email sent"}
                else:
                    return {"success": False, "error": "Email service returned False"}
                    
            except Exception as e:
                return {"success": False, "error": f"Email sending failed: {e}"}
            
        except Exception as e:
            error_msg = f"Failure email failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _cleanup_workflow(self):
        """Clean up workflow resources"""
        try:
            self.logger.info("🧹 Cleaning up workflow resources...")
            
            # Close any open applications or dialogs
            # This would involve specific cleanup logic
            
            # Reset state
            self.window_handle = None
            self.current_phase = None
            
            self.logger.info("✅ Workflow cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "current_phase": self.current_phase,
            "window_handle": self.window_handle,
            "workflow_start_time": self.workflow_start_time.isoformat() if self.workflow_start_time else None,
            "config": self.config
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration"""
        self.config.update(new_config)
        self.logger.info(f"Configuration updated: {new_config}")

# Integration with existing system
def run_vbs_automation_for_date(date_folder: str) -> Dict[str, Any]:
    """
    Main entry point for VBS automation
    Called by the enhanced service runner when Excel files are ready
    """
    try:
        print(f"🚀 Starting VBS automation for {date_folder}")
        
        orchestrator = VBSMasterOrchestrator()
        result = orchestrator.run_complete_workflow(date_folder)
        
        if result["success"]:
            print(f"✅ VBS automation completed successfully for {date_folder}")
            print(f"📄 PDF generated: {result.get('pdf_file', 'N/A')}")
            print(f"📧 Email sent: {result.get('email_sent', False)}")
        else:
            print(f"❌ VBS automation failed for {date_folder}")
            print(f"🚨 Errors: {result.get('errors', [])}")
        
        return result
        
    except Exception as e:
        error_msg = f"VBS automation entry point failed: {e}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

# Test function
def test_complete_workflow():
    """Test the complete VBS automation workflow"""
    print("🧪 Testing Complete VBS Automation Workflow")
    print("=" * 80)
    
    # Use current date folder for testing
    today = date.today()
    test_date_folder = f"{today.day:02d}{today.strftime('%B').lower()}"
    
    print(f"Testing with date folder: {test_date_folder}")
    
    # Run workflow
    result = run_vbs_automation_for_date(test_date_folder)
    
    print("\n📊 Test Results:")
    print(f"Success: {result['success']}")
    print(f"Phases completed: {result.get('phases_completed', [])}")
    print(f"Errors: {result.get('errors', [])}")
    print(f"Duration: {result.get('total_duration', 0):.1f} seconds")
    
    print("\n✅ Complete workflow testing completed")

if __name__ == "__main__":
    test_complete_workflow() 