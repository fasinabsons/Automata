#!/usr/bin/env python3
"""
Working Email Notifications for WiFi Automation
Direct Gmail integration for CSV downloads and Excel generation
"""

import os
import sys
import time
import smtplib
import logging
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class WorkingEmailNotifications:
    """Working email notifications with direct Gmail integration"""
    
    def __init__(self):
        # Direct Gmail configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "fasin.absons@gmail.com"
        self.sender_password = "zrxj vfjt wjos wkwy"
        self.recipient_email = "faseenm@gmail.com"
        
        self.logger = self._setup_logging()
        self.logger.info("Working Email Notifications initialized")
    
    def _setup_logging(self):
        """Setup logging"""
        logger = logging.getLogger("WorkingEmail")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def send_email(self, subject: str, body: str, attachments: list = None) -> bool:
        """Send email with direct Gmail SMTP"""
        try:
            self.logger.info(f"📧 Sending email: {subject}")
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # Add attachments if provided
            if attachments:
                for attachment_path in attachments:
                    if Path(attachment_path).exists():
                        self._attach_file(message, attachment_path)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            self.logger.info(f"✅ Email sent successfully to {self.recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Email sending failed: {e}")
            return False
    
    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Attach file to email"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {Path(file_path).name}'
            )
            message.attach(part)
            
        except Exception as e:
            self.logger.warning(f"Failed to attach file {file_path}: {e}")
    
    def send_csv_download_notification(self, slot_name: str, files_downloaded: int, 
                                     total_files: int, success: bool = True) -> bool:
        """Send CSV download notification"""
        try:
            if success:
                subject = f"✅ CSV Download Completed - {slot_name} - {datetime.now().strftime('%d/%m/%Y')}"
                body = f"""CSV download has been completed successfully!

Download Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🕐 Time Slot: {slot_name}
📁 Files Downloaded: {files_downloaded}
📊 Total Files Today: {total_files}
🎯 Excel Trigger: {total_files}/8 files

Status: ✅ SUCCESS

Networks Monitored:
• EHC TV Network
• EHC-15 Network  
• Reception Hall-Mobile Network
• Reception Hall-TV Network

Progress:
{'✅ Excel will be generated soon!' if total_files >= 8 else f'Need {8 - total_files} more files for Excel generation'}

Next Download Schedule:
{self._get_next_schedule_info()}

The system is working correctly and will automatically:
📊 Generate Excel file when 8 files are reached
📧 Send notifications for all activities
🔄 Continue monitoring at scheduled times

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department

---
This is an automated notification from the WiFi Monitoring System.
System Status: OPERATIONAL ✅
"""
            else:
                subject = f"❌ CSV Download Failed - {slot_name} - {datetime.now().strftime('%d/%m/%Y')}"
                body = f"""CSV download has failed!

Download Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🕐 Time Slot: {slot_name}
📁 Files Downloaded: 0
📊 Total Files Today: {total_files}

Status: ❌ FAILED

The system will automatically retry at the next scheduled time.
Please check system logs for detailed error information.

Next Retry Schedule:
{self._get_next_schedule_info()}

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department

---
This is an automated error notification.
System Status: MONITORING ⚠️
"""
            
            return self.send_email(subject, body)
            
        except Exception as e:
            self.logger.error(f"Error sending CSV download notification: {e}")
            return False
    
    def send_excel_generation_notification(self, excel_file: str, records_count: int) -> bool:
        """Send Excel generation notification"""
        try:
            subject = f"📊 Excel File Generated - {datetime.now().strftime('%d/%m/%Y')}"
            body = f"""Excel file has been generated successfully!

Excel Generation Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
📁 File: {excel_file}
📊 Total Records: {records_count:,}
🎯 Trigger: 8 CSV files reached (2 downloads/day × 4 files)

File Information:
📂 Location: EHC_Data_Merge/{datetime.now().strftime('%d%b').lower()}/
📋 Headers: Hostname, IP_Address, MAC_Address, Package, AP_MAC, Upload, Download
🔄 Processing: Duplicates removed, data cleaned

Next Steps:
✅ Excel file is ready for VBS integration
📄 PDF generation will follow
📧 Daily PDF report will be sent to General Manager

Schedule Summary:
🌅 Morning: 09:30 AM (CSV download)
🌞 Afternoon: 13:00 PM (CSV download + backup at 13:30 PM)
📊 Excel: Generated automatically after 8 files
📄 PDF: Generated from Excel data
📧 Reports: Sent daily to management

The WiFi automation system is operating successfully and collecting comprehensive network usage data for MoonFlower Hotel.

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department

---
This is an automated notification for Excel file generation.
System Status: OPERATIONAL ✅
File Ready for VBS Processing: ✅
"""
            
            # Try to attach Excel file if it exists
            attachments = []
            excel_path = Path(excel_file)
            if excel_path.exists() and excel_path.stat().st_size < 25 * 1024 * 1024:  # < 25MB
                attachments = [str(excel_path)]
            
            return self.send_email(subject, body, attachments)
            
        except Exception as e:
            self.logger.error(f"Error sending Excel generation notification: {e}")
            return False
    
    def send_daily_folder_notification(self, folder_path: str) -> bool:
        """Send daily folder creation notification"""
        try:
            folder_name = Path(folder_path).name
            subject = f"📁 Daily Folder Created - {folder_name}"
            body = f"""Daily folder has been created successfully!

Folder Creation Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
📁 Folder: {folder_name}
📂 Full Path: {folder_path}
🌅 Trigger: Midnight daily folder creation

Folder Structure:
📂 EHC_Data/{folder_name}/ - CSV files storage
📂 EHC_Data_Merge/{folder_name}/ - Excel files storage  
📂 EHC_Data_Pdf/{folder_name}/ - PDF files storage

Daily Schedule:
🌅 Morning: 09:30 AM (CSV download)
🌞 Afternoon: 13:00 PM (CSV download + backup at 13:30 PM)
📊 Excel: Generated automatically after 8 files
📄 PDF: Generated from Excel data
📧 Reports: Sent daily to management

The WiFi automation system has successfully created today's folder structure and is ready for data collection.

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department

---
This is an automated notification for daily folder creation.
System Status: OPERATIONAL ✅
Ready for Data Collection: ✅
"""
            
            return self.send_email(subject, body)
            
        except Exception as e:
            self.logger.error(f"Error sending daily folder notification: {e}")
            return False
    
    def send_service_startup_notification(self) -> bool:
        """Send service startup notification"""
        try:
            subject = f"🚀 WiFi Service Started - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            body = f"""WiFi Automation Service has started successfully!

Service Configuration:
📅 Start Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🌅 Morning Download: 09:30 AM
🌞 Afternoon Download: 13:00 PM (backup: 13:30 PM)
🚫 Evening Downloads: DISABLED (day-only operation)

Features Enabled:
✅ Automatic WiFi data collection
✅ Excel file generation (8-file trigger)
✅ Email notifications
✅ Health monitoring
✅ Crash prevention
✅ Auto-restart capability
✅ Background operation

You will receive email notifications for:
📁 Successful CSV downloads
❌ Failed download attempts
📊 Excel file generation
🚨 System crashes or errors
🏥 Health status updates

Networks Being Monitored:
• EHC TV Network
• EHC-15 Network  
• Reception Hall-Mobile Network
• Reception Hall-TV Network

The service is now actively monitoring WiFi networks and will collect data at scheduled times. All activities will be logged and reported via email.

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department

---
This is an automated startup notification.
Service Status: ACTIVE ✅
Email Notifications: ENABLED ✅
"""
            
            return self.send_email(subject, body)
            
        except Exception as e:
            self.logger.error(f"Error sending startup notification: {e}")
            return False
    
    def _get_next_schedule_info(self) -> str:
        """Get next schedule information"""
        try:
            current_hour = datetime.now().hour
            
            if current_hour < 9:
                return "09:30 AM (Morning Download)"
            elif current_hour < 13:
                return "13:00 PM (Afternoon Download)"
            elif current_hour < 13.5:
                return "13:30 PM (Afternoon Backup)"
            else:
                return "09:30 AM Tomorrow (Morning Download)"
        except:
            return "Check schedule configuration"

def test_working_notifications():
    """Test the working notification system"""
    print("🧪 TESTING WORKING EMAIL NOTIFICATIONS")
    print("=" * 50)
    
    notifications = WorkingEmailNotifications()
    
    # Test 1: CSV Download Notification
    print("\n📁 Testing CSV Download Notification...")
    csv_result = notifications.send_csv_download_notification(
        slot_name="morning",
        files_downloaded=4,
        total_files=4,
        success=True
    )
    
    if csv_result:
        print("✅ CSV download notification sent!")
    else:
        print("❌ CSV download notification failed")
    
    time.sleep(2)
    
    # Test 2: Excel Generation Notification
    print("\n📊 Testing Excel Generation Notification...")
    excel_result = notifications.send_excel_generation_notification(
        excel_file="EHC_Data_Merge/05july/EHC_Upload_Mac_05072025.xlsx",
        records_count=3809
    )
    
    if excel_result:
        print("✅ Excel generation notification sent!")
    else:
        print("❌ Excel generation notification failed")
    
    time.sleep(2)
    
    # Test 3: Service Startup Notification
    print("\n🚀 Testing Service Startup Notification...")
    startup_result = notifications.send_service_startup_notification()
    
    if startup_result:
        print("✅ Service startup notification sent!")
    else:
        print("❌ Service startup notification failed")
    
    # Summary
    print("\n" + "=" * 50)
    if csv_result and excel_result and startup_result:
        print("🎉 ALL EMAIL NOTIFICATIONS WORKING!")
        print("📧 Check faseenm@gmail.com for all test emails")
        print("\n✅ Email notifications are ready for:")
        print("   📁 CSV download completion")
        print("   📊 Excel file generation") 
        print("   🚀 Service startup/status")
    else:
        print("❌ Some email notifications failed")
    print("=" * 50)

def main():
    """Main function"""
    print("📧 WORKING EMAIL NOTIFICATIONS FOR WIFI AUTOMATION")
    print("=" * 60)
    print("Direct Gmail integration - bypasses configuration issues")
    print("Recipient: faseenm@gmail.com")
    print("=" * 60)
    
    user_input = input("Press Enter to test all notifications (or 'q' to quit): ").strip().lower()
    if user_input == 'q':
        return
    
    test_working_notifications()

if __name__ == "__main__":
    main() 