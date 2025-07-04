import psutil
import time
import subprocess
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path
from config.settings import LOGS_DIR, FILE_CONFIG
from core.logger import logger

class SystemMonitor:
    def __init__(self, execution_id=None):
        self.execution_id = execution_id
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start system monitoring in background thread"""
        try:
            if self.monitoring_active:
                logger.warning("System monitoring is already active", "SystemMonitor", self.execution_id)
                return
            
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("System monitoring started", "SystemMonitor", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to start system monitoring: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        try:
            self.monitoring_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            logger.info("System monitoring stopped", "SystemMonitor", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to stop system monitoring: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.monitoring_active:
                # Perform health checks every 5 minutes
                self._perform_health_checks()
                
                # Sleep for 5 minutes
                for _ in range(300):  # 5 minutes = 300 seconds
                    if not self.monitoring_active:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Monitoring loop error: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        try:
            # Check system resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Log resource usage
            logger.info(f"System resources - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%", 
                       "SystemMonitor", self.execution_id)
            
            # Check for resource warnings
            if cpu_percent > 80:
                logger.warning(f"High CPU usage detected: {cpu_percent}%", "SystemMonitor", self.execution_id)
            
            if memory.percent > 85:
                logger.warning(f"High memory usage detected: {memory.percent}%", "SystemMonitor", self.execution_id)
            
            if disk.percent > 90:
                logger.warning(f"High disk usage detected: {disk.percent}%", "SystemMonitor", self.execution_id)
            
            # Check network connectivity
            self._check_network_connectivity()
            
            # Check disk space for automation directories
            self._check_automation_disk_space()
            
            # Check for zombie processes
            self._check_processes()
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def _check_network_connectivity(self):
        """Check network connectivity to critical services"""
        try:
            # Test WiFi interface connectivity
            wifi_url = "51.38.163.73"
            result = subprocess.run(['ping', '-n', '1', wifi_url], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("WiFi interface connectivity: OK", "SystemMonitor", self.execution_id)
            else:
                logger.warning("WiFi interface connectivity: FAILED", "SystemMonitor", self.execution_id)
                
        except Exception as e:
            logger.warning(f"Network connectivity check failed: {str(e)}", "SystemMonitor", self.execution_id)
    
    def _check_automation_disk_space(self):
        """Check disk space for automation directories"""
        try:
            from config.settings import CSV_DIR, MERGED_DIR, REPORTS_DIR
            
            directories = [CSV_DIR, MERGED_DIR, REPORTS_DIR, LOGS_DIR]
            
            for directory in directories:
                if directory.exists():
                    # Calculate directory size
                    total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)
                    
                    logger.info(f"Directory size - {directory.name}: {size_mb:.2f} MB", "SystemMonitor", self.execution_id)
                    
                    # Check if directory is getting too large
                    if size_mb > 1000:  # 1GB warning
                        logger.warning(f"Large directory detected: {directory.name} ({size_mb:.2f} MB)", 
                                     "SystemMonitor", self.execution_id)
                        
        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def _check_processes(self):
        """Check for automation-related processes"""
        try:
            current_process = psutil.Process()
            
            # Check memory usage of current process
            memory_info = current_process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            logger.info(f"Automation process memory usage: {memory_mb:.2f} MB", "SystemMonitor", self.execution_id)
            
            if memory_mb > 500:  # 500MB warning
                logger.warning(f"High memory usage by automation process: {memory_mb:.2f} MB", 
                             "SystemMonitor", self.execution_id)
            
            # Check for Chrome processes (from web scraping)
            chrome_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if chrome_processes:
                logger.info(f"Found {len(chrome_processes)} Chrome processes", "SystemMonitor", self.execution_id)
                
        except Exception as e:
            logger.error(f"Process check failed: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def perform_maintenance(self):
        """Perform system maintenance tasks"""
        try:
            logger.info("Starting system maintenance", "SystemMonitor", self.execution_id)
            
            # Clean up old files
            self._cleanup_old_files()
            
            # Rotate log files
            self._rotate_log_files()
            
            # Clean up temporary files
            self._cleanup_temp_files()
            
            # Optimize system performance
            self._optimize_system()
            
            logger.success("System maintenance completed", "SystemMonitor", self.execution_id)
            
        except Exception as e:
            logger.error(f"System maintenance failed: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def _cleanup_old_files(self):
        """Clean up old automation files"""
        try:
            from config.settings import CSV_DIR, MERGED_DIR, REPORTS_DIR
            
            retention_days = FILE_CONFIG['retention_days']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            directories = [CSV_DIR, MERGED_DIR, REPORTS_DIR]
            total_deleted = 0
            total_size_freed = 0
            
            for directory in directories:
                if directory.exists():
                    for file_path in directory.rglob('*'):
                        if file_path.is_file():
                            file_mtime = file_path.stat().st_mtime
                            if file_mtime < cutoff_timestamp:
                                try:
                                    file_size = file_path.stat().st_size
                                    file_path.unlink()
                                    total_deleted += 1
                                    total_size_freed += file_size
                                except Exception as e:
                                    logger.warning(f"Could not delete old file {file_path}: {str(e)}", 
                                                  "SystemMonitor", self.execution_id)
            
            size_freed_mb = total_size_freed / (1024 * 1024)
            logger.info(f"File cleanup completed: {total_deleted} files deleted, {size_freed_mb:.2f} MB freed", 
                       "SystemMonitor", self.execution_id)
            
        except Exception as e:
            logger.error(f"File cleanup failed: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def _rotate_log_files(self):
        """Rotate log files if they get too large"""
        try:
            log_files = list(LOGS_DIR.glob("*.log"))
            max_size = 10 * 1024 * 1024  # 10MB
            
            for log_file in log_files:
                if log_file.stat().st_size > max_size:
                    # Create backup
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{log_file.stem}_{timestamp}.log"
                    backup_path = LOGS_DIR / backup_name
                    
                    log_file.rename(backup_path)
                    logger.info(f"Rotated log file: {log_file.name} -> {backup_name}", 
                               "SystemMonitor", self.execution_id)
            
        except Exception as e:
            logger.error(f"Log rotation failed: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            temp_dirs = [
                Path.home() / "AppData" / "Local" / "Temp",
                Path("C:/Windows/Temp"),
                Path("/tmp")  # For cross-platform compatibility
            ]
            
            total_cleaned = 0
            
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    # Clean up Chrome temp files
                    chrome_temp_pattern = "*chrome*"
                    for temp_file in temp_dir.glob(chrome_temp_pattern):
                        try:
                            if temp_file.is_file() and temp_file.stat().st_mtime < (time.time() - 3600):  # 1 hour old
                                temp_file.unlink()
                                total_cleaned += 1
                        except Exception:
                            pass  # Ignore errors for temp file cleanup
            
            if total_cleaned > 0:
                logger.info(f"Cleaned up {total_cleaned} temporary files", "SystemMonitor", self.execution_id)
                
        except Exception as e:
            logger.warning(f"Temp file cleanup failed: {str(e)}", "SystemMonitor", self.execution_id)
    
    def _optimize_system(self):
        """Perform system optimization tasks"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear DNS cache (Windows)
            try:
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, timeout=30)
                logger.info("DNS cache flushed", "SystemMonitor", self.execution_id)
            except Exception:
                pass  # Ignore if not on Windows or command fails
            
            logger.info("System optimization completed", "SystemMonitor", self.execution_id)
            
        except Exception as e:
            logger.warning(f"System optimization failed: {str(e)}", "SystemMonitor", self.execution_id)
    
    def schedule_system_restart(self):
        """Schedule system restart for maintenance"""
        try:
            logger.info("Scheduling system restart for maintenance", "SystemMonitor", self.execution_id)
            
            # Schedule restart for 1:00 AM
            restart_time = "01:00"
            
            # Create Windows scheduled task for restart
            task_command = f'schtasks /create /tn "WiFiAutomationRestart" /tr "shutdown /r /t 60" /sc daily /st {restart_time} /f'
            
            result = subprocess.run(task_command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.success(f"System restart scheduled for {restart_time} daily", "SystemMonitor", self.execution_id)
            else:
                logger.warning(f"Failed to schedule system restart: {result.stderr}", "SystemMonitor", self.execution_id)
                
        except Exception as e:
            logger.error(f"Failed to schedule system restart: {str(e)}", "SystemMonitor", self.execution_id, e)
    
    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            # System resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network status
            network_stats = psutil.net_io_counters()
            
            # Process information
            current_process = psutil.Process()
            process_memory = current_process.memory_info().rss / (1024 * 1024)
            
            # Uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = uptime_seconds / 3600
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3),
                    'uptime_hours': round(uptime_hours, 2)
                },
                'process': {
                    'memory_mb': round(process_memory, 2),
                    'pid': current_process.pid
                },
                'network': {
                    'bytes_sent': network_stats.bytes_sent,
                    'bytes_recv': network_stats.bytes_recv
                },
                'monitoring_active': self.monitoring_active
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}", "SystemMonitor", self.execution_id, e)
            return {'error': str(e)}

# Test function
def test_system_monitor():
    """Test system monitoring functionality"""
    monitor = SystemMonitor("test-execution")
    
    # Get system status
    status = monitor.get_system_status()
    print(f"System status: {status}")
    
    # Perform maintenance
    monitor.perform_maintenance()
    
    # Test monitoring (brief)
    monitor.start_monitoring()
    time.sleep(10)  # Monitor for 10 seconds
    monitor.stop_monitoring()

if __name__ == "__main__":
    test_system_monitor()