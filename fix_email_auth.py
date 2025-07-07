#!/usr/bin/env python3
"""
Fix Gmail Email Authentication
Guide to regenerate Gmail App Password and test email functionality
"""

import webbrowser
import time
import sys
from pathlib import Path

def fix_gmail_authentication():
    """Guide user through fixing Gmail authentication"""
    
    print("🔧 FIXING GMAIL EMAIL AUTHENTICATION")
    print("=" * 50)
    print()
    
    print("📧 Current Issue:")
    print("   Gmail App Password 'zrxj vfjt wjos wkwy' has been rejected")
    print("   Error 535: Username and Password not accepted")
    print()
    
    print("🛠️ SOLUTION: Generate New App Password")
    print("=" * 50)
    print()
    
    # Step 1: Open Google App Passwords page
    print("STEP 1: Open Google App Passwords")
    print("-" * 30)
    print("I'll open the Google App Passwords page for you...")
    
    try:
        webbrowser.open("https://myaccount.google.com/apppasswords")
        print("✅ Opened: https://myaccount.google.com/apppasswords")
    except:
        print("❌ Could not open browser automatically")
        print("Please manually go to: https://myaccount.google.com/apppasswords")
    
    print()
    input("Press Enter when you're ready to continue...")
    
    # Step 2: Instructions for generating App Password
    print("\nSTEP 2: Generate New App Password")
    print("-" * 30)
    print("1. Sign in to your Google account (fasin.absons@gmail.com)")
    print("2. If you don't see App Passwords, make sure 2-Factor Authentication is enabled")
    print("3. Click 'Generate' or 'Create App Password'")
    print("4. Select 'Mail' as the app")
    print("5. Select 'Windows Computer' as the device")
    print("6. Click 'Generate'")
    print("7. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)")
    print()
    
    # Step 3: Get new password from user
    print("STEP 3: Enter New App Password")
    print("-" * 30)
    print("Please enter the new 16-character App Password:")
    print("(Format: xxxx xxxx xxxx xxxx - include or exclude spaces, both work)")
    print()
    
    new_password = input("New App Password: ").strip()
    
    if not new_password:
        print("❌ No password entered. Please run this script again.")
        return False
    
    # Clean up password (remove spaces)
    clean_password = new_password.replace(" ", "")
    
    if len(clean_password) != 16:
        print(f"⚠️  Warning: Password length is {len(clean_password)}, expected 16 characters")
        print("This might still work, continuing...")
    
    print(f"✅ Password received: {new_password}")
    print(f"✅ Cleaned password: {clean_password}")
    print()
    
    # Step 4: Update configuration file
    print("STEP 4: Updating Configuration")
    print("-" * 30)
    
    config_file = Path("config/email_config.py")
    
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        # Read current config
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace the old password
        old_password = "zrxj vfjt wjos wkwy"
        new_content = content.replace(old_password, clean_password)
        
        # Write updated config
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated {config_file}")
        print(f"   Old password: {old_password}")
        print(f"   New password: {clean_password}")
        print()
        
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        return False
    
    # Step 5: Test email
    print("STEP 5: Testing Email")
    print("-" * 30)
    print("Testing email connection with new password...")
    
    try:
        # Import and test email service
        sys.path.append('.')
        from modules.email_service import EmailService
        
        email_service = EmailService()
        result = email_service.test_email_connection()
        
        if result["success"]:
            print("✅ EMAIL CONNECTION SUCCESSFUL!")
            print("   Gmail authentication is now working")
            print()
            
            # Test sending actual email
            print("Testing PDF email sending...")
            
            # Look for a PDF file to test with
            pdf_dirs = list(Path("EHC_Data_Pdf").glob("*/"))
            pdf_file = None
            
            for pdf_dir in pdf_dirs:
                pdf_files = list(pdf_dir.glob("*.pdf"))
                if pdf_files:
                    pdf_file = pdf_files[0]
                    break
            
            if pdf_file:
                print(f"Found test PDF: {pdf_file.name}")
                
                from datetime import date
                email_result = email_service.send_pdf_report(pdf_file, date.today())
                
                if email_result["success"]:
                    print("✅ TEST EMAIL SENT SUCCESSFULLY!")
                    print(f"   Sent to: faseenm@gmail.com")
                    print(f"   Attachment: {pdf_file.name}")
                    print()
                    print("🎉 EMAIL SYSTEM IS NOW FULLY WORKING!")
                    return True
                else:
                    print(f"❌ Email sending failed: {email_result['error']}")
            else:
                print("⚠️  No PDF file found for testing, but connection works")
                print("✅ Email authentication is fixed!")
                return True
                
        else:
            print(f"❌ Email connection still failing: {result['error']}")
            print("   Please check the App Password and try again")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Gmail Email Authentication Fix Tool")
    print("=" * 50)
    print()
    
    success = fix_gmail_authentication()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ EMAIL AUTHENTICATION FIXED!")
        print("📧 Email system is now ready for production")
        print("🎯 The automation will now send PDF reports automatically")
    else:
        print("❌ EMAIL AUTHENTICATION STILL HAS ISSUES")
        print("🔧 Please check the steps above and try again")
        print("💡 Make sure 2-Factor Authentication is enabled on your Google account")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 