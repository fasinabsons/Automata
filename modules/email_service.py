#!/usr/bin/env python3
"""
Email Service Module for WiFi Automation System
Sends automated PDF reports via email with Outlook integration
"""

import os
import sys
import time
import logging
import smtplib
import ssl
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import config with fallback
try:
    from config.email_config import EMAIL_CONFIG, get_email_config, validate_email_config
    from config.settings import config
except ImportError:
    # Create fallback email config
    EMAIL_CONFIG = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "use_tls": True,
        "email_address": "your-email@gmail.com",
        "email_password": "your-app-password",
        "recipient_email": "recipient@company.com",
        "subject_template": "WiFi Active Users Report - {date}",
        "body_template": "Please find attached the WiFi active users report for {date}.",
        "max_retry_attempts": 3,
        "retry_delay_seconds": 60
    }
    
    class SimpleConfig:
        def get_log_directory(self):
            return Path("logs")
        
        LOGGING_CONFIG = {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    
    config = SimpleConfig()

class EmailService:
    """Email service for automated PDF report delivery"""
    
    def __init__(self):
        self.config = config
        self.email_config = EMAIL_CONFIG
        self.logger = self._setup_logging()
        
        # Validate email configuration
        self._validate_configuration()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for email service"""
        logger = logging.getLogger("EmailService")
        logger.setLevel(getattr(logging, self.config.LOGGING_CONFIG["level"]))
        
        # Use existing log directory
        log_dir = self.config.get_log_directory()
        log_file = log_dir / f"email_service_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not logger.handlers:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(self.config.LOGGING_CONFIG["format"])
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _validate_configuration(self):
        """Validate email configuration"""
        try:
            required_fields = [
                "smtp_server", "smtp_port", "email_address", 
                "email_password", "recipient_email"
            ]
            
            missing_fields = []
            for field in required_fields:
                if not self.email_config.get(field) or self.email_config[field] == "your-email@gmail.com":
                    missing_fields.append(field)
            
            if missing_fields:
                self.logger.warning(f"Email configuration incomplete. Missing: {', '.join(missing_fields)}")
                self.logger.warning("Please update config/email_config.py with your actual email settings")
            else:
                self.logger.info("Email configuration validated successfully")
                
        except Exception as e:
            self.logger.error(f"Error validating email configuration: {e}")
    
    def send_pdf_report(self, pdf_path: Path, report_date: date = None) -> Dict[str, Any]:
        """Send PDF report via email"""
        try:
            if report_date is None:
                report_date = date.today()
            
            self.logger.info(f"Sending PDF report: {pdf_path}")
            
            # Check if PDF file exists
            if not pdf_path.exists():
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}"
                }
            
            # Check file size
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            max_size_mb = self.email_config.get("max_attachment_size_mb", 25)
            
            if file_size_mb > max_size_mb:
                return {
                    "success": False,
                    "error": f"PDF file too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)"
                }
            
            # Create email message
            message = self._create_email_message(pdf_path, report_date, file_size_mb)
            
            # Send email with retry logic
            result = self._send_email_with_retry(message)
            
            if result["success"]:
                self.logger.info(f"PDF report sent successfully to {self.email_config['recipient_email']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to send PDF report: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": error_msg}
    
    def _create_email_message(self, pdf_path: Path, report_date: date, file_size_mb: float) -> MIMEMultipart:
        """Create email message with PDF attachment"""
        try:
            # Create message
            message = MIMEMultipart()
            
            # Email headers
            message["From"] = self.email_config["email_address"]
            message["To"] = self.email_config["recipient_email"]
            
            # Add CC and BCC if configured
            if self.email_config.get("cc_emails"):
                message["Cc"] = ", ".join(self.email_config["cc_emails"])
            
            # Subject with date
            date_str = report_date.strftime("%B %d, %Y")
            subject = self.email_config["subject_template"].format(date=date_str)
            message["Subject"] = subject
            
            # Email body
            body_text = self._create_email_body(report_date, file_size_mb, pdf_path)
            message.attach(MIMEText(body_text, "plain"))
            
            # Attach PDF
            self._attach_pdf(message, pdf_path)
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error creating email message: {e}")
            raise
    
    def _create_email_body(self, report_date: date, file_size_mb: float, pdf_path: Path = None) -> str:
        """Create email body text with enhanced information"""
        try:
            # Get template or use default
            template = self.email_config.get("body_template", 
                "Please find attached the WiFi active users report for {date}.")
            
            # Format date
            date_str = report_date.strftime("%B %d, %Y")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get user count from PDF filename if available
            total_users = "N/A"
            if pdf_path and pdf_path.exists():
                # Try to extract user count from filename if it contains user info
                filename = pdf_path.name
                if "active users" in filename.lower():
                    try:
                        # Look for numbers in filename that might indicate user count
                        import re
                        numbers = re.findall(r'\d+', filename)
                        if numbers:
                            total_users = numbers[0]  # Take first number found
                    except:
                        pass
            
            # Generate unique report ID
            report_id = f"{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
            
            # Format the email body using template
            try:
                body = template.format(
                    date=date_str,
                    total_users=total_users,
                    timestamp=timestamp,
                    file_size_mb=f"{file_size_mb:.1f}",
                    report_id=report_id
                )
            except KeyError as e:
                # Fallback if template has missing keys
                self.logger.warning(f"Template formatting issue: {e}, using simplified template")
                body = f"""Dear Management Team,

Please find attached the WiFi Active Users Report for {date_str}.

This automated report contains comprehensive data on WiFi usage across all monitored networks at MoonFlower Hotel.

Report Details:
- Report Date: {date_str}
- File Size: {file_size_mb:.1f} MB
- Generated: {timestamp}
- Report ID: {report_id}

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department

---
This is an automated email generated by the WiFi Monitoring System.
For technical support or questions, please contact: fasin.absons@gmail.com"""
            
            return body
            
        except Exception as e:
            self.logger.error(f"Error creating email body: {e}")
            return f"""Dear Management Team,

Please find attached the WiFi Active Users Report for {report_date.strftime('%B %d, %Y')}.

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department"""
    
    def _attach_pdf(self, message: MIMEMultipart, pdf_path: Path):
        """Attach PDF file to email message"""
        try:
            with open(pdf_path, "rb") as attachment:
                # Create MIMEBase object
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            # Encode file
            encoders.encode_base64(part)
            
            # Add header
            filename = pdf_path.name
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            # Attach to message
            message.attach(part)
            
            self.logger.info(f"PDF attached: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error attaching PDF: {e}")
            raise
    
    def _send_email_with_retry(self, message: MIMEMultipart) -> Dict[str, Any]:
        """Send email with retry logic"""
        max_attempts = self.email_config.get("max_retry_attempts", 3)
        retry_delay = self.email_config.get("retry_delay_seconds", 60)
        
        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.info(f"Email send attempt {attempt}/{max_attempts}")
                
                # Create SMTP connection
                result = self._send_via_smtp(message)
                
                if result["success"]:
                    return result
                else:
                    if attempt < max_attempts:
                        self.logger.warning(f"Attempt {attempt} failed: {result['error']}")
                        self.logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        return result
                        
            except Exception as e:
                error_msg = f"Email send attempt {attempt} failed: {e}"
                self.logger.error(error_msg)
                
                if attempt < max_attempts:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    return {"success": False, "error": error_msg}
        
        return {"success": False, "error": "All retry attempts failed"}
    
    def _send_via_smtp(self, message: MIMEMultipart) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Create SMTP connection
            server = smtplib.SMTP(
                self.email_config["smtp_server"], 
                self.email_config["smtp_port"]
            )
            
            # Enable TLS if configured
            if self.email_config.get("use_tls", True):
                server.starttls()
            
            # Login
            server.login(
                self.email_config["email_address"],
                self.email_config["email_password"]
            )
            
            # Get recipients
            recipients = [self.email_config["recipient_email"]]
            
            # Add CC recipients
            if self.email_config.get("cc_emails"):
                recipients.extend(self.email_config["cc_emails"])
            
            # Add BCC recipients
            if self.email_config.get("bcc_emails"):
                recipients.extend(self.email_config["bcc_emails"])
            
            # Send email
            text = message.as_string()
            server.sendmail(
                self.email_config["email_address"],
                recipients,
                text
            )
            
            # Close connection
            server.quit()
            
            return {
                "success": True,
                "recipients": recipients,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"SMTP send failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def test_email_connection(self) -> Dict[str, Any]:
        """Test email connection and configuration"""
        try:
            self.logger.info("Testing email connection...")
            
            # Test SMTP connection
            server = smtplib.SMTP(
                self.email_config["smtp_server"], 
                self.email_config["smtp_port"]
            )
            
            if self.email_config.get("use_tls", True):
                server.starttls()
            
            # Test login
            server.login(
                self.email_config["email_address"],
                self.email_config["email_password"]
            )
            
            server.quit()
            
            self.logger.info("Email connection test successful")
            return {
                "success": True,
                "message": "Email connection and authentication successful"
            }
            
        except Exception as e:
            error_msg = f"Email connection test failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def send_test_email(self) -> Dict[str, Any]:
        """Send a test email to verify configuration"""
        try:
            self.logger.info("Sending test email...")
            
            # Create simple test message
            message = MIMEMultipart()
            message["From"] = self.email_config["email_address"]
            message["To"] = self.email_config["recipient_email"]
            message["Subject"] = "WiFi Automation System - Test Email"
            
            body = f"""This is a test email from the WiFi Automation System.

Test Details:
- Sent: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- From: {self.email_config["email_address"]}
- To: {self.email_config["recipient_email"]}
- SMTP Server: {self.email_config["smtp_server"]}:{self.email_config["smtp_port"]}

If you received this email, the email configuration is working correctly.

Best regards,
WiFi Automation System
"""
            
            message.attach(MIMEText(body, "plain"))
            
            # Send test email
            result = self._send_via_smtp(message)
            
            if result["success"]:
                self.logger.info("Test email sent successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to send test email: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def send_email(self, subject: str, body: str, attachments: List[Path] = None) -> bool:
        """Send email with subject and body (for notifications)"""
        try:
            self.logger.info(f"Sending notification email: {subject}")
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.email_config["email_address"]
            message["To"] = self.email_config["recipient_email"]
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if attachment.exists():
                        self._attach_pdf(message, attachment)
            
            # Send email
            result = self._send_via_smtp(message)
            
            if result["success"]:
                self.logger.info(f"Notification email sent successfully to {self.email_config['recipient_email']}")
                return True
            else:
                self.logger.error(f"Failed to send notification email: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending notification email: {e}")
            return False
    
    def send_download_notification(self, slot_name: str, files_downloaded: int, 
                                 total_files: int, success: bool = True) -> bool:
        """Send CSV download notification"""
        try:
            if success:
                subject = f"✅ CSV Download Completed - {slot_name} - {datetime.now().strftime('%d/%m/%Y')}"
                body = f"""CSV download has been completed successfully!

Download Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🕐 Slot: {slot_name}
📁 Files downloaded: {files_downloaded}
📊 Total files today: {total_files}

Status: ✅ SUCCESS

The system will automatically generate Excel file when 8 files are reached.
Current progress: {total_files}/8 files

Networks monitored:
• EHC TV Network
• EHC-15 Network  
• Reception Hall-Mobile Network
• Reception Hall-TV Network

Next scheduled download: {self._get_next_schedule_info()}

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department
"""
            else:
                subject = f"❌ CSV Download Failed - {slot_name} - {datetime.now().strftime('%d/%m/%Y')}"
                body = f"""CSV download has failed!

Download Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🕐 Slot: {slot_name}
📁 Files downloaded: 0
📊 Total files today: {total_files}

Status: ❌ FAILED

The system will retry at the next scheduled time.
Current progress: {total_files}/8 files

Please check the system logs for detailed error information.

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department
"""
            
            return self.send_email(subject, body)
            
        except Exception as e:
            self.logger.error(f"Error sending download notification: {e}")
            return False
    
    def _get_next_schedule_info(self) -> str:
        """Get next schedule information"""
        try:
            current_hour = datetime.now().hour
            
            if current_hour < 9:
                return "09:30 AM (Morning)"
            elif current_hour < 13:
                return "13:00 PM (Afternoon)"
            elif current_hour < 13.5:
                return "13:30 PM (Afternoon Backup)"
            else:
                return "09:30 AM Tomorrow (Morning)"
        except:
            return "Check schedule configuration"

# Convenience functions for external use
def send_daily_pdf_report(pdf_path: Path) -> Dict[str, Any]:
    """Send daily PDF report"""
    email_service = EmailService()
    return email_service.send_pdf_report(pdf_path)

def test_email_configuration() -> Dict[str, Any]:
    """Test email configuration"""
    email_service = EmailService()
    return email_service.test_email_connection()

def send_test_email() -> Dict[str, Any]:
    """Send test email"""
    email_service = EmailService()
    return email_service.send_test_email()

# Test function
def test_email_service():
    """Test email service functionality"""
    print("\nEmail Service Test:")
    print("-" * 50)
    
    email_service = EmailService()
    
    # Test connection
    connection_result = email_service.test_email_connection()
    if connection_result["success"]:
        print("✅ Email connection: SUCCESS")
    else:
        print(f"❌ Email connection: FAILED - {connection_result['error']}")
        return
    
    # Test email sending
    test_result = email_service.send_test_email()
    if test_result["success"]:
        print("✅ Test email sent: SUCCESS")
    else:
        print(f"❌ Test email: FAILED - {test_result['error']}")

if __name__ == "__main__":
    test_email_service()