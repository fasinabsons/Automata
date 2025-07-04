import smtplib
import win32com.client as win32
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from pathlib import Path
import os
from core.logger import logger
from config.settings import REPORTS_DIR

class EmailService:
    def __init__(self, execution_id=None):
        self.execution_id = execution_id
        self.outlook = None
        
    def setup_outlook(self):
        """Setup Outlook COM interface"""
        try:
            self.outlook = win32.Dispatch("Outlook.Application")
            logger.info("Outlook COM interface initialized", "EmailService", self.execution_id)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Outlook: {str(e)}", "EmailService", self.execution_id, e)
            return False
    
    def send_daily_report(self, pdf_file_path=None, recipients=None):
        """Send daily WiFi user data report"""
        try:
            logger.info("Starting daily report email", "EmailService", self.execution_id)
            
            # Default recipients if not provided
            if not recipients:
                recipients = [
                    "admin@company.com",
                    "manager@company.com"
                ]
            
            # Find latest PDF report if not specified
            if not pdf_file_path:
                pdf_file_path = self._find_latest_pdf_report()
            
            if not pdf_file_path or not Path(pdf_file_path).exists():
                logger.warning("No PDF report found for email", "EmailService", self.execution_id)
                return False
            
            # Setup Outlook
            if not self.setup_outlook():
                logger.error("Failed to setup Outlook for email", "EmailService", self.execution_id)
                return False
            
            # Create email
            mail = self.outlook.CreateItem(0)  # 0 = olMailItem
            
            # Email content
            yesterday = datetime.now() - timedelta(days=1)
            subject = f"WiFi User Data Report - {yesterday.strftime('%Y-%m-%d')}"
            
            body = f"""
Dear Team,

Please find attached the WiFi User Data Report for {yesterday.strftime('%B %d, %Y')}.

Report Summary:
- Report Date: {yesterday.strftime('%Y-%m-%d')}
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- File: {Path(pdf_file_path).name}

This report contains user activity data from all WiFi access points including:
- EHC TV access point
- EHC-15 access point  
- Reception Hall Mobile access point
- Reception Hall TV access point

If you have any questions about this report, please contact the IT team.

Best regards,
WiFi Automation System
            """.strip()
            
            # Set email properties
            mail.Subject = subject
            mail.Body = body
            mail.To = "; ".join(recipients)
            
            # Attach PDF report
            mail.Attachments.Add(str(pdf_file_path))
            
            # Send email
            mail.Send()
            
            logger.success(f"Daily report email sent to {len(recipients)} recipients", "EmailService", self.execution_id)
            logger.info(f"Email sent to: {', '.join(recipients)}", "EmailService", self.execution_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send daily report email: {str(e)}", "EmailService", self.execution_id, e)
            return False
    
    def _find_latest_pdf_report(self):
        """Find the most recent PDF report"""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            date_folder = yesterday.strftime("%d%B").lower()
            
            pdf_dir = REPORTS_DIR / date_folder
            
            if not pdf_dir.exists():
                logger.warning(f"PDF directory not found: {pdf_dir}", "EmailService", self.execution_id)
                return None
            
            # Find PDF files
            pdf_files = list(pdf_dir.glob("*.pdf"))
            
            if not pdf_files:
                logger.warning(f"No PDF files found in {pdf_dir}", "EmailService", self.execution_id)
                return None
            
            # Return the most recent PDF file
            latest_pdf = max(pdf_files, key=lambda f: f.stat().st_mtime)
            logger.info(f"Found latest PDF report: {latest_pdf}", "EmailService", self.execution_id)
            
            return str(latest_pdf)
            
        except Exception as e:
            logger.error(f"Failed to find latest PDF report: {str(e)}", "EmailService", self.execution_id, e)
            return None
    
    def send_error_alert(self, error_message, component="System"):
        """Send error alert email"""
        try:
            logger.info(f"Sending error alert for {component}", "EmailService", self.execution_id)
            
            # Setup Outlook
            if not self.setup_outlook():
                return False
            
            # Create email
            mail = self.outlook.CreateItem(0)
            
            subject = f"WiFi Automation System - {component} Error Alert"
            
            body = f"""
ALERT: WiFi Automation System Error

Component: {component}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Error: {error_message}

Please check the system logs for more details and take appropriate action.

This is an automated alert from the WiFi User Data Automation System.
            """.strip()
            
            # Set email properties
            mail.Subject = subject
            mail.Body = body
            mail.To = "admin@company.com"
            mail.Importance = 2  # High importance
            
            # Send email
            mail.Send()
            
            logger.success("Error alert email sent", "EmailService", self.execution_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send error alert: {str(e)}", "EmailService", self.execution_id, e)
            return False
    
    def send_status_report(self, status_data):
        """Send system status report"""
        try:
            logger.info("Sending system status report", "EmailService", self.execution_id)
            
            # Setup Outlook
            if not self.setup_outlook():
                return False
            
            # Create email
            mail = self.outlook.CreateItem(0)
            
            subject = f"WiFi Automation System - Status Report {datetime.now().strftime('%Y-%m-%d')}"
            
            body = f"""
WiFi Automation System Status Report

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System Status:
- Running: {status_data.get('is_running', 'Unknown')}
- Last Execution: {status_data.get('last_execution', 'Never')}
- Files Processed Today: {status_data.get('files_processed', 0)}
- Errors Today: {status_data.get('errors_count', 0)}

Schedule Status:
- Next Slot 1 (9:30 AM): {status_data.get('next_slot1', 'Not scheduled')}
- Next Slot 2 (1:00 PM): {status_data.get('next_slot2', 'Not scheduled')}
- Next Slot 3 (3:00 PM): {status_data.get('next_slot3', 'Not scheduled')}

Recent Activity:
{status_data.get('recent_activity', 'No recent activity')}

This is an automated status report from the WiFi User Data Automation System.
            """.strip()
            
            # Set email properties
            mail.Subject = subject
            mail.Body = body
            mail.To = "admin@company.com"
            
            # Send email
            mail.Send()
            
            logger.success("Status report email sent", "EmailService", self.execution_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send status report: {str(e)}", "EmailService", self.execution_id, e)
            return False
    
    def test_email_service(self):
        """Test email service functionality"""
        try:
            logger.info("Testing email service", "EmailService", self.execution_id)
            
            # Setup Outlook
            if not self.setup_outlook():
                return False
            
            # Create test email
            mail = self.outlook.CreateItem(0)
            
            subject = "WiFi Automation System - Email Service Test"
            body = f"""
This is a test email from the WiFi User Data Automation System.

Test performed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you receive this email, the email service is working correctly.

This is an automated test message.
            """.strip()
            
            # Set email properties
            mail.Subject = subject
            mail.Body = body
            mail.To = "admin@company.com"
            
            # Send email
            mail.Send()
            
            logger.success("Email service test completed successfully", "EmailService", self.execution_id)
            return True
            
        except Exception as e:
            logger.error(f"Email service test failed: {str(e)}", "EmailService", self.execution_id, e)
            return False

# Test function
def test_email_service():
    """Test the email service functionality"""
    service = EmailService("email-test")
    return service.test_email_service()

if __name__ == "__main__":
    test_email_service()