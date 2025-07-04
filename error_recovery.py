#!/usr/bin/env python3
"""
Error Recovery System for WiFi Automation
Monitors the main application and restarts system if critical errors occur
"""

import os
import sys
import time
import logging
import subprocess
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import config

class ErrorRecoverySystem:
    """Monitor and recover from critical errors in WiFi automation"""
    
    def __init__(self):
        self.config = config
        self.logger = self._setup_logging()
        self.process_name = "python.exe"
        self.app_script = "wifi_automation_app.py"
        self.max_restart_attempts = 3
        self.restart_attempts = 0
        self.last_restart_time = None
        self.monitoring_interval = 300  # 5 minutes
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for error recovery"""
        logger = logging.getLogger("ErrorRecoverySystem")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = self.config.get_log_directory()
        log_file = log_dir / f"error_recovery_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not logger.handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def is_wifi_automation_running(self) -> bool:
        """Check if WiFi automation is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == self.process_name:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(self.app_script in arg for arg in cmdline):
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking process status: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, any]:
        """Get system health metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network connectivity test
            network_ok = self._test_network_connectivity()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "network_ok": network_ok,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {}
    
    def _test_network_connectivity(self) -> bool:
        """Test network connectivity to WiFi interface"""
        try:
            # Test connectivity to WiFi interface
            result = subprocess.run(
                ["ping", "-n", "1", "51.38.163.73"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Network connectivity test failed: {e}")
            return False
    
    def restart_wifi_automation(self) -> bool:
        """Restart WiFi automation application"""
        try:
            self.logger.info("Attempting to restart WiFi automation")
            
            # Kill existing processes
            self._kill_wifi_automation_processes()
            
            # Wait a moment
            time.sleep(5)
            
            # Start new process
            app_path = project_root / self.app_script
            cmd = [sys.executable, str(app_path), "--tray"]
            
            process = subprocess.Popen(
                cmd,
                cwd=str(project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # Wait a moment and check if it started
            time.sleep(10)
            
            if self.is_wifi_automation_running():
                self.logger.info("WiFi automation restarted successfully")
                self.restart_attempts = 0
                return True
            else:
                self.logger.error("Failed to restart WiFi automation")
                return False
                
        except Exception as e:
            self.logger.error(f"Error restarting WiFi automation: {e}")
            return False
    
    def _kill_wifi_automation_processes(self):
        """Kill all WiFi automation processes"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == self.process_name:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(self.app_script in arg for arg in cmdline):
                        self.logger.info(f"Killing process PID: {proc.info['pid']}")
                        proc.kill()
        except Exception as e:
            self.logger.error(f"Error killing processes: {e}")
    
    def restart_system(self, reason: str = "Critical error recovery"):
        """Restart the entire system"""
        try:
            self.logger.critical(f"Restarting system: {reason}")
            
            # Log the restart
            restart_log = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "restart_attempts": self.restart_attempts,
                "system_health": self.get_system_health()
            }
            
            self.logger.info(f"System restart log: {restart_log}")
            
            # Restart system with 60 second delay
            subprocess.run([
                "shutdown", "/r", "/t", "60", 
                "/c", f"WiFi Automation Error Recovery: {reason}"
            ], check=True)
            
        except Exception as e:
            self.logger.error(f"Error restarting system: {e}")
    
    def monitor_and_recover(self):
        """Main monitoring and recovery loop"""
        self.logger.info("Starting error recovery monitoring")
        
        while True:
            try:
                # Check if WiFi automation is running
                if not self.is_wifi_automation_running():
                    self.logger.warning("WiFi automation not running")
                    
                    # Increment restart attempts
                    self.restart_attempts += 1
                    
                    if self.restart_attempts <= self.max_restart_attempts:
                        self.logger.info(f"Restart attempt {self.restart_attempts}/{self.max_restart_attempts}")
                        
                        if self.restart_wifi_automation():
                            self.logger.info("WiFi automation recovered successfully")
                        else:
                            self.logger.error("Failed to restart WiFi automation")
                            
                            # If we've reached max attempts, restart system
                            if self.restart_attempts >= self.max_restart_attempts:
                                self.restart_system("Max restart attempts reached")
                                break
                    else:
                        self.restart_system("Max restart attempts exceeded")
                        break
                else:
                    # Reset restart attempts if running normally
                    if self.restart_attempts > 0:
                        self.logger.info("WiFi automation running normally, resetting restart attempts")
                        self.restart_attempts = 0
                
                # Check system health
                health = self.get_system_health()
                
                # Log health metrics
                if health:
                    self.logger.debug(f"System health: CPU={health.get('cpu_percent', 0):.1f}%, "
                                    f"Memory={health.get('memory_percent', 0):.1f}%, "
                                    f"Disk={health.get('disk_percent', 0):.1f}%, "
                                    f"Network={health.get('network_ok', False)}")
                    
                    # Check for critical resource usage
                    if health.get('memory_percent', 0) > 90:
                        self.logger.warning("High memory usage detected")
                        
                    if health.get('disk_percent', 0) > 95:
                        self.logger.warning("High disk usage detected")
                        
                    if not health.get('network_ok', False):
                        self.logger.warning("Network connectivity issues detected")
                
                # Wait before next check
                time.sleep(self.monitoring_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Error recovery monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def run_health_check(self) -> Dict[str, any]:
        """Run a comprehensive health check"""
        self.logger.info("Running comprehensive health check")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "wifi_automation_running": self.is_wifi_automation_running(),
            "system_health": self.get_system_health(),
            "restart_attempts": self.restart_attempts,
            "last_restart": self.last_restart_time.isoformat() if self.last_restart_time else None
        }
        
        # Check log files
        log_dir = self.config.get_log_directory()
        log_files = list(log_dir.glob("*.log"))
        health_report["log_files"] = [str(f) for f in log_files]
        
        # Check download directory
        download_dir = self.config.get_download_directory()
        if download_dir.exists():
            csv_files = list(download_dir.glob("*.csv"))
            health_report["recent_downloads"] = len(csv_files)
        else:
            health_report["recent_downloads"] = 0
        
        # Check merged directory
        merged_dir = self.config.get_merged_directory()
        if merged_dir.exists():
            excel_files = list(merged_dir.glob("*.xls*"))
            health_report["recent_excel_files"] = len(excel_files)
        else:
            health_report["recent_excel_files"] = 0
        
        self.logger.info(f"Health check complete: {health_report}")
        return health_report

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WiFi Automation Error Recovery System")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring mode")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument("--restart-app", action="store_true", help="Restart WiFi automation app")
    
    args = parser.parse_args()
    
    recovery_system = ErrorRecoverySystem()
    
    if args.monitor:
        recovery_system.monitor_and_recover()
    elif args.health_check:
        health_report = recovery_system.run_health_check()
        print("\n" + "="*50)
        print("WIFI AUTOMATION HEALTH CHECK REPORT")
        print("="*50)
        for key, value in health_report.items():
            print(f"{key}: {value}")
        print("="*50)
    elif args.restart_app:
        success = recovery_system.restart_wifi_automation()
        if success:
            print("WiFi automation restarted successfully")
        else:
            print("Failed to restart WiFi automation")
    else:
        print("Use --monitor, --health-check, or --restart-app")

if __name__ == "__main__":
    main() 