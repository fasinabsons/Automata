#!/usr/bin/env python3
"""
Email Configuration for WiFi Automation System
Configure SMTP settings for automated PDF report delivery
"""

# Email Configuration
EMAIL_CONFIG = {
    # SMTP Server Settings
    "smtp_server": "smtp.gmail.com",  # Change to your email provider
    "smtp_port": 587,
    "use_tls": True,
    
    # Email Credentials
    "email_address": "your-email@gmail.com",  # Replace with your email
    "email_password": "your-app-password",    # Replace with your app password
    
    # Recipients
    "recipient_email": "recipient@company.com",  # Replace with recipient
    "cc_emails": [],  # Optional CC recipients
    "bcc_emails": [], # Optional BCC recipients
    
    # Email Templates
    "subject_template": "WiFi Active Users Report - {date}",
    "body_template": """
Dear Team,

Please find attached the WiFi active users report for {date}.

Report Summary:
- Total Active Users: {total_users}
- Report Generation Time: {generation_time}
- Networks Monitored: {networks_monitored}

This report includes all active WiFi users across our monitored networks.

Best regards,
WiFi Automation System
    """,
    
    # Attachment Settings
    "attachment_name_template": "WiFi_Users_Report_{date}.pdf",
    "max_attachment_size_mb": 25,  # Maximum attachment size in MB
    
    # Retry Settings
    "max_retry_attempts": 3,
    "retry_delay_seconds": 60,
    
    # Schedule Settings
    "send_time": "08:00",  # Time to send daily reports (24-hour format)
    "send_on_weekends": True,  # Whether to send reports on weekends
    
    # Email Validation
    "validate_recipients": True,
    "require_ssl": True
}

# Email Provider Configurations
EMAIL_PROVIDERS = {
    "gmail": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "use_tls": True,
        "instructions": "Use App Password, not regular password. Enable 2FA first."
    },
    "outlook": {
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "use_tls": True,
        "instructions": "Use regular password or App Password if 2FA enabled."
    },
    "yahoo": {
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "use_tls": True,
        "instructions": "Use App Password. Enable 2FA first."
    },
    "custom": {
        "smtp_server": "your-smtp-server.com",
        "smtp_port": 587,
        "use_tls": True,
        "instructions": "Configure with your custom SMTP settings."
    }
}

# Security Settings
SECURITY_CONFIG = {
    "encrypt_credentials": True,
    "credential_file": "email_credentials.enc",
    "log_email_content": False,  # For privacy
    "mask_email_addresses": True,  # In logs
    "require_authentication": True
}

def get_email_config():
    """Get email configuration"""
    return EMAIL_CONFIG

def get_provider_config(provider_name: str):
    """Get configuration for specific email provider"""
    return EMAIL_PROVIDERS.get(provider_name.lower(), EMAIL_PROVIDERS["custom"])

def validate_email_config():
    """Validate email configuration"""
    required_fields = [
        "smtp_server", "smtp_port", "email_address", 
        "email_password", "recipient_email"
    ]
    
    missing_fields = []
    for field in required_fields:
        if not EMAIL_CONFIG.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "Email configuration is valid"

if __name__ == "__main__":
    # Test email configuration
    valid, message = validate_email_config()
    print(f"Email Configuration Status: {message}")
    
    if valid:
        print("\nEmail Configuration:")
        print(f"SMTP Server: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
        print(f"From: {EMAIL_CONFIG['email_address']}")
        print(f"To: {EMAIL_CONFIG['recipient_email']}")
        print(f"Send Time: {EMAIL_CONFIG['send_time']}")
    else:
        print("\nPlease update the email configuration with your actual settings.")
        print("\nFor Gmail:")
        print("1. Enable 2-Factor Authentication")
        print("2. Generate App Password")
        print("3. Use App Password instead of regular password")
        print("4. Update EMAIL_CONFIG with your details") 