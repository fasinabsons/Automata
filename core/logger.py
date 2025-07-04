import logging
import logging.handlers
from pathlib import Path
from config.settings import LOGS_DIR, LOGGING_CONFIG
import json
from datetime import datetime

class AutomationLogger:
    def __init__(self, name="WiFiAutomation"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "automation.log",
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count']
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "errors.log",
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count']
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
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(f"[{component}] {message} | {json.dumps(log_data)}")
    
    def warning(self, message, component="System", execution_id=None):
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.warning(f"[{component}] {message} | {json.dumps(log_data)}")
    
    def error(self, message, component="System", execution_id=None, exception=None):
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat(),
            'exception': str(exception) if exception else None
        }
        self.logger.error(f"[{component}] {message} | {json.dumps(log_data)}")
    
    def success(self, message, component="System", execution_id=None):
        log_data = {
            'component': component,
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(f"[{component}] SUCCESS: {message} | {json.dumps(log_data)}")

# Global logger instance
logger = AutomationLogger()