#!/usr/bin/env python3
"""
Test Email Notification System
Test CSV download and Excel generation notifications
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

def test_email_config():
    """Test email configuration directly"""
    print("🔧 TESTING EMAIL CONFIGURATION")
    print("=" * 40)
    
    try:
        from config.email_config import EMAIL_CONFIG
        
        print(f"📧 Email Address: {EMAIL_CONFIG.get('email_address', 'NOT SET')}")
        print(f"📨 Recipient: {EMAIL_CONFIG.get('recipient_email', 'NOT SET')}")
        print(f"🌐 SMTP Server: {EMAIL_CONFIG.get('smtp_server', 'NOT SET')}")
        print(f"🔑 Password: {'SET' if EMAIL_CONFIG.get('email_password') else 'NOT SET'}")
        
        return EMAIL_CONFIG
        
    except Exception as e:
        print(f"❌ Error loading email config: {e}")
        return None

def test_csv_download_notification():
    """Test CSV download notification"""
    print("\n📁 TESTING CSV DOWNLOAD NOTIFICATION")
    print("=" * 40)
    
    try:
        # Import and test email service
        from modules.email_service import EmailService
        
        # Create email service
        email_service = EmailService()
        
        # Test download notification
        result = email_service.send_download_notification(
            slot_name="test_morning",
            files_downloaded=4,
            total_files=4,
            success=True
        )
        
        if result:
            print("✅ CSV download notification sent successfully!")
            print("📧 Check faseenm@gmail.com for notification email")
        else:
            print("❌ CSV download notification failed")
            
        return result
        
    except Exception as e:
        print(f"❌ Error testing download notification: {e}")
        return False

def test_excel_generation_notification():
    """Test Excel generation notification"""
    print("\n📊 TESTING EXCEL GENERATION NOTIFICATION")
    print("=" * 40)
    
    try:
        from modules.email_service import EmailService
        
        email_service = EmailService()
        
        # Test Excel generation notification
        subject = f"📊 Excel File Generated - {datetime.now().strftime('%d/%m/%Y')}"
        body = f"""Excel file has been generated successfully after reaching 8 CSV files!

File Details:
📁 File: EHC_Upload_Mac_05072025.xlsx
📊 Records: 3,809 unique records
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🎯 Trigger: 8 files reached (2 downloads per day)

Headers included: Hostname, IP_Address, MAC_Address, Package, AP_MAC, Upload, Download

The Excel file is ready for VBS integration and PDF generation.

Best regards,
WiFi Automation System
"""
        
        result = email_service.send_email(subject=subject, body=body)
        
        if result:
            print("✅ Excel generation notification sent successfully!")
            print("📧 Check faseenm@gmail.com for notification email")
        else:
            print("❌ Excel generation notification failed")
            
        return result
        
    except Exception as e:
        print(f"❌ Error testing Excel notification: {e}")
        return False

def test_direct_email():
    """Test direct email using Gmail SMTP"""
    print("\n📧 TESTING DIRECT EMAIL")
    print("=" * 40)
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Direct Gmail configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "fasin.absons@gmail.com"
        sender_password = "zrxj vfjt wjos wkwy"
        recipient_email = "faseenm@gmail.com"
        
        print(f"📧 From: {sender_email}")
        print(f"📨 To: {recipient_email}")
        print(f"🌐 Server: {smtp_server}:{smtp_port}")
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "🧪 WiFi Automation Test - Email Notifications Working"
        
        body = f"""This is a test email from the WiFi Automation System.

Test Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🧪 Test: Email notification system verification
✅ Status: Email notifications are working correctly

This confirms that:
✅ Gmail SMTP connection is working
✅ Email credentials are correct
✅ Notifications will be sent for:
   - CSV download completion
   - Excel file generation
   - System status updates

You will receive automatic notifications when:
📁 CSV files are downloaded (morning/afternoon)
📊 Excel files are generated (8-file trigger)
🚨 System errors occur

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department
"""
        
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        print("🔄 Connecting to Gmail SMTP...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("🔐 Authenticating...")
            server.login(sender_email, sender_password)
            print("📤 Sending test email...")
            server.send_message(message)
            
        print("✅ DIRECT EMAIL SENT SUCCESSFULLY!")
        print("📧 Check faseenm@gmail.com for test email")
        return True
        
    except Exception as e:
        print(f"❌ Direct email test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 EMAIL NOTIFICATION SYSTEM TEST")
    print("=" * 50)
    print("Testing email notifications for CSV downloads and Excel generation")
    print("Recipient: faseenm@gmail.com")
    print("=" * 50)
    
    # Test 1: Email Configuration
    config = test_email_config()
    if not config:
        print("❌ Cannot proceed without email configuration")
        return
    
    # Test 2: Direct Email (bypass email service issues)
    print("\n" + "=" * 50)
    direct_result = test_direct_email()
    
    if direct_result:
        print("\n✅ EMAIL SYSTEM IS WORKING!")
        print("📧 You should receive a test email at faseenm@gmail.com")
        
        # Test notifications
        user_input = input("\nPress Enter to test CSV download notification (or 'q' to quit): ").strip().lower()
        if user_input != 'q':
            test_csv_download_notification()
        
        user_input = input("\nPress Enter to test Excel generation notification (or 'q' to quit): ").strip().lower()
        if user_input != 'q':
            test_excel_generation_notification()
            
        print("\n🎉 EMAIL NOTIFICATION TESTS COMPLETED!")
        print("📧 Check faseenm@gmail.com for all test emails")
        
    else:
        print("\n❌ EMAIL SYSTEM NOT WORKING")
        print("Please check Gmail credentials and settings")

if __name__ == "__main__":
    main() 