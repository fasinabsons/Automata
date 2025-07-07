#!/usr/bin/env python3
"""
Simple Email Test for WiFi Automation System
Tests email functionality with current configuration
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def test_email_simple():
    """Test email sending with current configuration"""
    
    # Email configuration (from config/email_config.py)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_address = "fasin.absons@gmail.com"
    email_password = "zrxj vfjt wjos wkwy"  # App password
    recipient_email = "faseenm@gmail.com"
    
    print("🧪 Testing email configuration...")
    print(f"   SMTP Server: {smtp_server}:{smtp_port}")
    print(f"   From: {email_address}")
    print(f"   To: {recipient_email}")
    print()
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = recipient_email
        message["Subject"] = f"🧪 WiFi System Email Test - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Email body
        body = f"""This is a test email from the WiFi Automation System.

Test Details:
📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🔧 System: WiFi Data Collection
📧 Configuration: Gmail SMTP
🎯 Purpose: Email notification testing

If you receive this email, the email system is working correctly!

Features being tested:
✅ SMTP connection
✅ Authentication
✅ Message formatting
✅ Delivery to faseenm@gmail.com

Next steps:
- CSV download notifications
- Excel generation alerts
- System status updates

Best regards,
WiFi Automation System
MoonFlower Hotel IT Department
"""
        
        message.attach(MIMEText(body, "plain"))
        
        print("📧 Creating SMTP connection...")
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        
        print("🔐 Authenticating...")
        server.login(email_address, email_password)
        
        print("📤 Sending email...")
        text = message.as_string()
        server.sendmail(email_address, recipient_email, text)
        server.quit()
        
        print("✅ Email sent successfully!")
        print(f"   📧 Check {recipient_email} for the test email")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        print()
        
        # Provide troubleshooting info
        print("🔍 Troubleshooting:")
        print("   1. Check Gmail App Password is correct")
        print("   2. Verify 2-factor authentication is enabled")
        print("   3. Ensure 'Less secure app access' is not blocking")
        print("   4. Check internet connection")
        print("   5. Verify recipient email address")
        print()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   WiFi Automation System - Email Test")
    print("=" * 60)
    print()
    
    success = test_email_simple()
    
    if success:
        print("🎉 Email system is working correctly!")
        print("   You can now run the WiFi automation service")
        print("   and receive email notifications.")
    else:
        print("🚨 Email system needs attention!")
        print("   Please fix the configuration before running")
        print("   the automation service.")
    
    print()
    print("=" * 60) 