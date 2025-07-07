#!/usr/bin/env python3
"""
Test Email PDF Functionality
Tests the email service with PDF attachment from the EHC_Data_Pdf directory
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date

# Add project root to path
sys.path.append('.')

from modules.email_service import EmailService

def test_email_with_pdf():
    """Test email service with existing PDF"""
    print("📧 Testing Email Service with PDF Attachment")
    print("=" * 60)
    
    # Initialize email service
    email_service = EmailService()
    
    # Test email connection first
    print("🔍 Testing email connection...")
    connection_result = email_service.test_email_connection()
    
    if not connection_result["success"]:
        print(f"❌ Email connection failed: {connection_result['error']}")
        return False
    
    print("✅ Email connection successful")
    
    # Look for existing PDF file
    pdf_dir = Path("EHC_Data_Pdf/04july")
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return False
    
    # Find PDF files
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        return False
    
    # Use the first PDF file found
    pdf_path = pdf_files[0]
    print(f"📄 Found PDF file: {pdf_path.name}")
    print(f"📁 File size: {pdf_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Send email with PDF
    print("📧 Sending email with PDF attachment...")
    
    report_date = date.today()
    result = email_service.send_pdf_report(pdf_path, report_date)
    
    if result["success"]:
        print("✅ Email sent successfully!")
        print(f"📧 Recipients: {result.get('recipients', [])}")
        print(f"🕐 Sent at: {result.get('timestamp', 'Unknown')}")
        
        # Show email details
        print("\n📧 Email Details:")
        print(f"   From: fasin.absons@gmail.com")
        print(f"   To: faseenm@gmail.com")
        print(f"   Subject: WiFi Active Users Report - {report_date.strftime('%B %d, %Y')} | MoonFlower Hotel")
        print(f"   Attachment: {pdf_path.name}")
        
        return True
    else:
        print(f"❌ Email sending failed: {result['error']}")
        return False

def test_email_configuration():
    """Test email configuration"""
    print("\n🔧 Testing Email Configuration:")
    print("-" * 40)
    
    email_service = EmailService()
    
    # Test basic connection
    connection_test = email_service.test_email_connection()
    print(f"Connection Test: {'✅ PASS' if connection_test['success'] else '❌ FAIL'}")
    
    if not connection_test["success"]:
        print(f"Error: {connection_test['error']}")

def main():
    """Main test function"""
    print("🧪 WiFi Email System Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test configuration
    test_email_configuration()
    
    # Test email with PDF
    success = test_email_with_pdf()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("📧 Email service is working correctly")
        print("📄 PDF attachment functionality verified")
        print("\n🎯 Ready for production use!")
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Please check email configuration")
        print("📋 Verify SMTP settings and credentials")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 