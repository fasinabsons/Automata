import os
from pathlib import Path
from cryptography.fernet import Fernet

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# Production directory structure
CSV_DIR = Path(os.getenv('WIFI_CSV_DIR', r"C:\Users\Lenovo\Videos\Automata\EHC_Data"))
MERGED_DIR = Path(os.getenv('WIFI_MERGED_DIR', r"C:\Users\Lenovo\Videos\Automata\EHC_Data_Merge"))
REPORTS_DIR = Path(os.getenv('WIFI_REPORTS_DIR', r"C:\Users\Lenovo\Videos\Automata\EHC_Data_Pdf"))

# Encryption key for credentials (generate with: Fernet.generate_key())
ENCRYPTION_KEY = os.getenv('WIFI_ENCRYPTION_KEY', b'your-encryption-key-here')

def encrypt_credential(credential):
    """Encrypt a credential"""
    if isinstance(ENCRYPTION_KEY, str):
        key = ENCRYPTION_KEY.encode()
    else:
        key = ENCRYPTION_KEY
    
    f = Fernet(key)
    return f.encrypt(credential.encode()).decode()

def decrypt_credential(encrypted_credential):
    """Decrypt a credential"""
    if isinstance(ENCRYPTION_KEY, str):
        key = ENCRYPTION_KEY.encode()
    else:
        key = ENCRYPTION_KEY
    
    f = Fernet(key)
    return f.decrypt(encrypted_credential.encode()).decode()

# WiFi Interface Configuration - Production
WIFI_CONFIG = {
    'target_url': os.getenv('WIFI_TARGET_URL', 'https://51.38.163.73:8443/wsg/'),
    'username': os.getenv('WIFI_USERNAME', 'admin'),
    'password': os.getenv('WIFI_PASSWORD', 'AdminFlower@123'),  # Use environment variable in production
    'timeout': int(os.getenv('WIFI_TIMEOUT', '30')),
    'retry_attempts': int(os.getenv('WIFI_RETRY_ATTEMPTS', '3')),
    'download_timeout': int(os.getenv('WIFI_DOWNLOAD_TIMEOUT', '600'))
}

# VBS Application Configuration - Production
VBS_CONFIG = {
    'primary_path': os.getenv('VBS_PRIMARY_PATH', r'C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk'),
    'fallback_path': os.getenv('VBS_FALLBACK_PATH', r'\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe'),
    'username': os.getenv('VBS_USERNAME', 'Vj'),
    'password': os.getenv('VBS_PASSWORD', ''),  # Use environment variable in production
    'default_date': os.getenv('VBS_DEFAULT_DATE', '01/01/2023'),
    'timeout': int(os.getenv('VBS_TIMEOUT', '60')),
    'retry_attempts': int(os.getenv('VBS_RETRY_ATTEMPTS', '2'))
}

# Email Configuration - Production
EMAIL_CONFIG = {
    'recipients': os.getenv('EMAIL_RECIPIENTS', 'admin@company.com,manager@company.com').split(','),
    'sender_name': os.getenv('EMAIL_SENDER_NAME', 'WiFi Automation System'),
    'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
    'smtp_username': os.getenv('EMAIL_SMTP_USERNAME', ''),
    'smtp_password': os.getenv('EMAIL_SMTP_PASSWORD', ''),  # Use app password for Gmail
    'use_outlook': os.getenv('EMAIL_USE_OUTLOOK', 'true').lower() == 'true'
}

# Scheduling Configuration - Production
SCHEDULE_CONFIG = {
    'slot1_time': os.getenv('SCHEDULE_SLOT1_TIME', '09:30'),
    'slot2_time': os.getenv('SCHEDULE_SLOT2_TIME', '13:00'),
    'slot3_time': os.getenv('SCHEDULE_SLOT3_TIME', '15:00'),
    'processing_time': os.getenv('SCHEDULE_PROCESSING_TIME', '15:05'),
    'email_time': os.getenv('SCHEDULE_EMAIL_TIME', '09:00'),
    'restart_time': os.getenv('SCHEDULE_RESTART_TIME', '01:00'),
    
    # Enhanced configuration
    'retry_on_failure': os.getenv('SCHEDULE_RETRY_ON_FAILURE', 'true').lower() == 'true',
    'retry_delay_minutes': int(os.getenv('SCHEDULE_RETRY_DELAY_MINUTES', '30')),
    'max_retries': int(os.getenv('SCHEDULE_MAX_RETRIES', '3')),
    'timezone': os.getenv('SCHEDULE_TIMEZONE', 'local')
}

# Chrome Driver Configuration - Production
CHROME_CONFIG = {
    'headless': os.getenv('CHROME_HEADLESS', 'false').lower() == 'true',
    'disable_gpu': os.getenv('CHROME_DISABLE_GPU', 'true').lower() == 'true',
    'no_sandbox': os.getenv('CHROME_NO_SANDBOX', 'true').lower() == 'true',
    'disable_dev_shm_usage': os.getenv('CHROME_DISABLE_DEV_SHM_USAGE', 'true').lower() == 'true',
    'disable_extensions': os.getenv('CHROME_DISABLE_EXTENSIONS', 'true').lower() == 'true',
    'disable_plugins': os.getenv('CHROME_DISABLE_PLUGINS', 'true').lower() == 'true',
    'disable_images': os.getenv('CHROME_DISABLE_IMAGES', 'false').lower() == 'true',
    'window_size': os.getenv('CHROME_WINDOW_SIZE', '1920,1080')
}

# File Management - Production
FILE_CONFIG = {
    'retention_days': int(os.getenv('FILE_RETENTION_DAYS', '60')),
    'max_file_size': int(os.getenv('FILE_MAX_SIZE', str(100 * 1024 * 1024))),  # 100MB
    'allowed_extensions': os.getenv('FILE_ALLOWED_EXTENSIONS', '.csv,.xlsx,.pdf').split(','),
    'backup_enabled': os.getenv('FILE_BACKUP_ENABLED', 'true').lower() == 'true',
    'backup_directory': os.getenv('FILE_BACKUP_DIRECTORY', str(BASE_DIR / 'backups'))
}

# Logging Configuration - Production
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'max_file_size': int(os.getenv('LOG_MAX_FILE_SIZE', str(10 * 1024 * 1024))),  # 10MB
    'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5')),
    'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    'console_output': os.getenv('LOG_CONSOLE_OUTPUT', 'true').lower() == 'true',
    'file_output': os.getenv('LOG_FILE_OUTPUT', 'true').lower() == 'true'
}

# Security Configuration - Production
SECURITY_CONFIG = {
    'encrypt_credentials': os.getenv('SECURITY_ENCRYPT_CREDENTIALS', 'true').lower() == 'true',
    'ssl_verify': os.getenv('SECURITY_SSL_VERIFY', 'false').lower() == 'true',  # False for self-signed certs
    'api_authentication': os.getenv('SECURITY_API_AUTH', 'false').lower() == 'true',
    'api_key': os.getenv('SECURITY_API_KEY', ''),
    'session_timeout': int(os.getenv('SECURITY_SESSION_TIMEOUT', '3600')),  # 1 hour
    'max_login_attempts': int(os.getenv('SECURITY_MAX_LOGIN_ATTEMPTS', '3'))
}

# Monitoring Configuration - Production
MONITORING_CONFIG = {
    'health_check_interval': int(os.getenv('MONITORING_HEALTH_CHECK_INTERVAL', '300')),  # 5 minutes
    'disk_space_threshold': int(os.getenv('MONITORING_DISK_SPACE_THRESHOLD', '85')),  # 85%
    'memory_threshold': int(os.getenv('MONITORING_MEMORY_THRESHOLD', '80')),  # 80%
    'cpu_threshold': int(os.getenv('MONITORING_CPU_THRESHOLD', '90')),  # 90%
    'alert_email': os.getenv('MONITORING_ALERT_EMAIL', 'admin@company.com'),
    'enable_alerts': os.getenv('MONITORING_ENABLE_ALERTS', 'true').lower() == 'true'
}

# Performance Configuration - Production
PERFORMANCE_CONFIG = {
    'max_concurrent_downloads': int(os.getenv('PERFORMANCE_MAX_CONCURRENT_DOWNLOADS', '4')),
    'download_chunk_size': int(os.getenv('PERFORMANCE_DOWNLOAD_CHUNK_SIZE', '8192')),
    'processing_batch_size': int(os.getenv('PERFORMANCE_PROCESSING_BATCH_SIZE', '1000')),
    'memory_limit_mb': int(os.getenv('PERFORMANCE_MEMORY_LIMIT_MB', '512')),
    'enable_caching': os.getenv('PERFORMANCE_ENABLE_CACHING', 'true').lower() == 'true'
}

# Create directories
for directory in [DATA_DIR, LOGS_DIR, DOWNLOADS_DIR, CSV_DIR, MERGED_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Create backup directory if enabled
if FILE_CONFIG['backup_enabled']:
    Path(FILE_CONFIG['backup_directory']).mkdir(parents=True, exist_ok=True)

# Environment variable template for .env file
ENV_TEMPLATE = """
# WiFi Automation System - Environment Variables
# Copy this to .env and update with your actual values

# WiFi Interface Settings
WIFI_TARGET_URL=https://51.38.163.73:8443/wsg/
WIFI_USERNAME=admin
WIFI_PASSWORD=AdminFlower@123

# VBS Application Settings
VBS_PRIMARY_PATH=C:\\Users\\Lenovo\\Music\\moonflower\\AbsonsItERP.exe - Shortcut.lnk
VBS_FALLBACK_PATH=\\\\192.168.10.16\\e\\ArabianLive\\ArabianLive_MoonFlower\\AbsonsItERP.exe
VBS_USERNAME=Vj
VBS_PASSWORD=

# Email Settings
EMAIL_RECIPIENTS=admin@company.com,manager@company.com
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password

# Security Settings
WIFI_ENCRYPTION_KEY=generate-with-fernet-generate-key
SECURITY_API_KEY=your-api-key-here

# Monitoring Settings
MONITORING_ALERT_EMAIL=admin@company.com
"""

def create_env_template():
    """Create .env template file"""
    env_file = BASE_DIR / '.env.template'
    with open(env_file, 'w') as f:
        f.write(ENV_TEMPLATE.strip())
    print(f"Environment template created: {env_file}")

def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"Environment variables loaded from: {env_file}")
        except ImportError:
            print("python-dotenv not installed. Install with: pip install python-dotenv")
        except Exception as e:
            print(f"Error loading environment file: {e}")

def validate_configuration():
    """Validate production configuration"""
    issues = []
    
    # Check required environment variables
    required_vars = [
        'WIFI_PASSWORD',
        'EMAIL_RECIPIENTS',
        'WIFI_ENCRYPTION_KEY'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"Missing required environment variable: {var}")
    
    # Check directory permissions
    for directory in [CSV_DIR, MERGED_DIR, REPORTS_DIR]:
        if not directory.exists():
            issues.append(f"Directory does not exist: {directory}")
        elif not os.access(directory, os.W_OK):
            issues.append(f"No write permission for directory: {directory}")
    
    return issues

if __name__ == "__main__":
    create_env_template()
    load_environment()
    
    issues = validate_configuration()
    if issues:
        print("Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration validation passed!") 