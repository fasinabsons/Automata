#!/usr/bin/env python3
"""
Log Management System for WiFi Automation
Centralizes all logs in EHC_Logs folder and implements automatic cleanup
"""

import os
import sys
import time
import logging
import logging.handlers
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import glob
import threading
import schedule

class LogManager:
    """Centralized log management system"""
    
    def __init__(self):
        self.log_directory = Path("EHC_Logs")
        self.log_directory.mkdir(exist_ok=True)
        
        # Log retention settings
        self.retention_days = 7
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        
        # Active loggers registry
        self.active_loggers = {}
        
        # Start cleanup scheduler
        self._start_cleanup_scheduler()
    
    def get_logger(self, name: str, component: str = None) -> logging.Logger:
        """Get a centralized logger instance"""
        logger_key = f"{name}_{component}" if component else name
        
        if logger_key not in self.active_loggers:
            logger = self._create_logger(name, component)
            self.active_loggers[logger_key] = logger
        
        return self.active_loggers[logger_key]
    
    def _create_logger(self, name: str, component: str = None) -> logging.Logger:
        """Create a new logger with centralized configuration"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create log filename
        if component:
            log_filename = f"{component}_{datetime.now().strftime('%Y%m%d')}.log"
        else:
            log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        log_file = self.log_directory / log_filename
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def cleanup_old_logs(self):
        """Clean up log files older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            deleted_count = 0
            freed_space = 0
            
            # Find all log files in EHC_Logs directory
            log_files = list(self.log_directory.glob("*.log*"))
            
            for log_file in log_files:
                try:
                    # Check file modification time
                    file_mtime = log_file.stat().st_mtime
                    
                    if file_mtime < cutoff_timestamp:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        deleted_count += 1
                        freed_space += file_size
                        print(f"Deleted old log: {log_file.name}")
                
                except Exception as e:
                    print(f"Error deleting {log_file.name}: {e}")
            
            if deleted_count > 0:
                freed_mb = freed_space / (1024 * 1024)
                print(f"Log cleanup completed: {deleted_count} files deleted, {freed_mb:.2f} MB freed")
            else:
                print("No old log files to delete")
                
        except Exception as e:
            print(f"Log cleanup error: {e}")
    
    def _start_cleanup_scheduler(self):
        """Start the automatic log cleanup scheduler"""
        def run_cleanup():
            try:
                self.cleanup_old_logs()
            except Exception as e:
                print(f"Scheduled cleanup error: {e}")
        
        # Schedule cleanup daily at 2 AM
        schedule.every().day.at("02:00").do(run_cleanup)
        
        # Start scheduler in background thread
        def scheduler_thread():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        cleanup_thread = threading.Thread(target=scheduler_thread, daemon=True)
        cleanup_thread.start()
    
    def get_log_stats(self) -> Dict:
        """Get statistics about log files"""
        try:
            log_files = list(self.log_directory.glob("*.log*"))
            
            total_size = sum(f.stat().st_size for f in log_files)
            total_files = len(log_files)
            
            # Recent logs (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_files = [
                f for f in log_files 
                if datetime.fromtimestamp(f.stat().st_mtime) > recent_cutoff
            ]
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'recent_files': len(recent_files),
                'oldest_file': min(log_files, key=lambda f: f.stat().st_mtime).name if log_files else None,
                'newest_file': max(log_files, key=lambda f: f.stat().st_mtime).name if log_files else None
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def migrate_existing_logs(self):
        """Migrate existing logs from other directories to EHC_Logs"""
        try:
            # Common log directories to check
            log_dirs = [
                Path("logs"),
                Path("."),  # Root directory
                Path("modules"),
                Path("config")
            ]
            
            migrated_count = 0
            
            for log_dir in log_dirs:
                if log_dir.exists() and log_dir != self.log_directory:
                    # Find all log files
                    log_files = list(log_dir.glob("*.log*"))
                    
                    for log_file in log_files:
                        try:
                            # Don't migrate if it's already in EHC_Logs
                            if log_file.parent == self.log_directory:
                                continue
                            
                            # Create new filename with timestamp
                            new_name = f"migrated_{log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                            new_path = self.log_directory / new_name
                            
                            # Move the file
                            log_file.rename(new_path)
                            migrated_count += 1
                            print(f"Migrated log: {log_file.name} -> {new_name}")
                            
                        except Exception as e:
                            print(f"Error migrating {log_file.name}: {e}")
            
            if migrated_count > 0:
                print(f"Log migration completed: {migrated_count} files migrated to EHC_Logs")
            else:
                print("No log files to migrate")
                
        except Exception as e:
            print(f"Log migration error: {e}")

# Global log manager instance
log_manager = LogManager()

def get_centralized_logger(name: str, component: str = None) -> logging.Logger:
    """Get a centralized logger - convenience function"""
    return log_manager.get_logger(name, component)

def cleanup_logs():
    """Manual log cleanup - convenience function"""
    log_manager.cleanup_old_logs()

def migrate_logs():
    """Manual log migration - convenience function"""
    log_manager.migrate_existing_logs()

if __name__ == "__main__":
    # Test the log manager
    print("Testing Log Manager...")
    
    # Test logger creation
    test_logger = get_centralized_logger("test", "log_manager")
    test_logger.info("Test log message")
    
    # Test migration
    migrate_logs()
    
    # Test cleanup
    cleanup_logs()
    
    # Show stats
    stats = log_manager.get_log_stats()
    print(f"Log stats: {stats}")
    
    print("Log Manager test completed!") 