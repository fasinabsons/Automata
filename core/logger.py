import logging
import logging.handlers
from pathlib import Path
from config.settings import LOGGING_CONFIG
import json
from datetime import datetime
import re

class AutomationLogger:
    def __init__(self, name="WiFiAutomation"):
        # Use EHC_Logs directory instead of LOGS_DIR
        self.log_directory = Path("EHC_Logs")
        self.log_directory.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _sanitize_message(self, message):
        """
        Sanitize message to remove emoji characters that cause encoding issues
        
        Args:
            message: Original message string
            
        Returns:
            Sanitized message string
        """
        # Remove emoji characters that cause encoding issues
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # other symbols
            "\U000024C2-\U0001F251"  # enclosed characters
            "]+", 
            flags=re.UNICODE
        )
        
        # Replace emojis with text equivalents
        sanitized = emoji_pattern.sub('', message)
        
        # Replace common emoji with text
        replacements = {
            '🏥': '[HEALTH]',
            '🔍': '[SEARCH]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🚀': '[START]',
            '📊': '[STATS]',
            '📁': '[FOLDER]',
            '📄': '[FILE]',
            '🔄': '[PROCESS]',
            '💾': '[SAVE]',
            '📧': '[EMAIL]',
            '⏰': '[TIME]',
            '🎯': '[TARGET]',
            '🔧': '[TOOL]',
            '🖱️': '[CLICK]',
            '⌨️': '[TYPE]',
            '🔐': '[SECURITY]',
            '📝': '[FORM]',
            '📅': '[DATE]',
            '👤': '[USER]',
            '🔒': '[LOCK]',
            '🧹': '[CLEAN]',
            '🔻': '[MINIMIZE]'
        }
        
        for emoji, replacement in replacements.items():
            sanitized = sanitized.replace(emoji, replacement)
        
        return sanitized.strip()
    
    def _setup_handlers(self):
        # File handler with rotation and UTF-8 encoding - now in EHC_Logs
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_directory / "automation.log",
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count'],
            encoding='utf-8'  # Explicitly set UTF-8 encoding
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Error file handler with UTF-8 encoding - now in EHC_Logs
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_directory / "errors.log",
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count'],
            encoding='utf-8'  # Explicitly set UTF-8 encoding
        )
        error_handler.setLevel(logging.ERROR)
        
        # Formatter
        formatter = logging.Formatter(LOGGING_CONFIG['format'])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
    
    def info(self, message, component="System", execution_id=None):
        sanitized_message = self._sanitize_message(str(message))
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(f"[{component}] {sanitized_message} | {json.dumps(log_data)}")
    
    def warning(self, message, component="System", execution_id=None):
        sanitized_message = self._sanitize_message(str(message))
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.warning(f"[{component}] {sanitized_message} | {json.dumps(log_data)}")
    
    def error(self, message, component="System", execution_id=None, exception=None):
        sanitized_message = self._sanitize_message(str(message))
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat(),
            'exception': str(exception) if exception else None
        }
        self.logger.error(f"[{component}] {sanitized_message} | {json.dumps(log_data)}")
    
    def success(self, message, component="System", execution_id=None):
        sanitized_message = self._sanitize_message(str(message))
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(f"[{component}] SUCCESS: {sanitized_message} | {json.dumps(log_data)}")

# Global logger instance
logger = AutomationLogger()

# Log cleanup function for 7-day retention
def cleanup_old_logs():
    """Clean up log files older than 7 days in EHC_Logs directory"""
    try:
        from datetime import timedelta
        
        log_directory = Path("EHC_Logs")
        if not log_directory.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=7)
        cutoff_timestamp = cutoff_date.timestamp()
        
        deleted_count = 0
        freed_space = 0
        
        # Find all log files
        log_files = list(log_directory.glob("*.log*"))
        
        for log_file in log_files:
            try:
                # Check file modification time
                file_mtime = log_file.stat().st_mtime
                
                if file_mtime < cutoff_timestamp:
                    file_size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_count += 1
                    freed_space += file_size
            
            except Exception as e:
                logger.warning(f"Error deleting old log {log_file.name}: {e}")
        
        if deleted_count > 0:
            freed_mb = freed_space / (1024 * 1024)
            logger.info(f"Log cleanup completed: {deleted_count} files deleted, {freed_mb:.2f} MB freed")
    
    except Exception as e:
        logger.error(f"Log cleanup error: {e}")

# Schedule automatic cleanup
import schedule
import threading
import time

def start_log_cleanup_scheduler():
    """Start the automatic log cleanup scheduler"""
    def run_cleanup():
        cleanup_old_logs()
    
    # Schedule cleanup daily at 2 AM
    schedule.every().day.at("02:00").do(run_cleanup)
    
    # Start scheduler in background thread
    def scheduler_thread():
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    
    cleanup_thread = threading.Thread(target=scheduler_thread, daemon=True)
    cleanup_thread.start()
    logger.info("Log cleanup scheduler started - will clean logs older than 7 days daily at 2 AM")

# Start the cleanup scheduler when module is imported
start_log_cleanup_scheduler()