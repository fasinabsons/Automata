#!/usr/bin/env python3
"""
Simple Background WiFi Automation Runner
Uses only working components for reliable operation
"""

import os
import sys
import time
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import schedule

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from corrected_wifi_app import CorrectedWiFiApp

class SimpleBackgroundRunner:
    """Simple background runner for WiFi automation"""
    
    def __init__(self):
        self.running = False
        self.setup_logging()
        self.wifi_app = CorrectedWiFiApp()
        
        self.logger.info("🚀 Simple Background Runner initialized")
    
    def setup_logging(self):
        """Setup logging"""
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "simple_runner.log"
        
        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("SimpleRunner")
    
    def add_to_startup(self):
        """Add to Windows startup"""
        try:
            import winreg
            
            # Get current script path
            script_path = sys.executable
            startup_args = f'"{__file__}"'
            
            # Registry key for startup
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Add to startup
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(
                    reg_key,
                    "SimpleWiFiRunner",
                    0,
                    winreg.REG_SZ,
                    f'"{script_path}" {startup_args}'
                )
            
            self.logger.info("✅ Added to Windows startup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add to startup: {e}")
            return False
    
    def remove_from_startup(self):
        """Remove from Windows startup"""
        try:
            import winreg
            
            # Registry key for startup
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Remove from startup
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, "SimpleWiFiRunner")
            
            self.logger.info("✅ Removed from Windows startup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove from startup: {e}")
            return False
    
    def run_wifi_download(self, slot_name="scheduled"):
        """Run WiFi download"""
        self.logger.info(f"🔄 Starting WiFi download - {slot_name}")
        
        try:
            # Run WiFi automation
            result = self.wifi_app.run_corrected_automation()
            
            if result.get('success', False):
                files_downloaded = result.get('files_downloaded', 0)
                self.logger.info(f"✅ WiFi download completed: {files_downloaded} files downloaded")
                return True
            else:
                self.logger.error(f"❌ WiFi download failed for {slot_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ WiFi download error: {e}")
            return False
    
    def schedule_tasks(self):
        """Schedule the automation tasks"""
        self.logger.info("🕐 Scheduling tasks...")
        
        # Schedule morning slot (09:30)
        schedule.every().day.at("09:30").do(self.run_wifi_download, "morning")
        
        # Schedule evening slot (13:00)
        schedule.every().day.at("13:00").do(self.run_wifi_download, "evening")
        
        self.logger.info("✅ Tasks scheduled:")
        self.logger.info("   🌅 Morning slot: 09:30")
        self.logger.info("   🌆 Evening slot: 13:00")
    
    def start(self):
        """Start the background runner"""
        self.logger.info("🚀 Starting Simple Background Runner...")
        
        try:
            self.running = True
            
            # Add to startup
            self.add_to_startup()
            
            # Schedule tasks
            self.schedule_tasks()
            
            self.logger.info("✅ Background runner started successfully")
            self.logger.info("🔄 System will run continuously in background")
            self.logger.info("🔒 Will work even when PC is locked")
            self.logger.info("📅 Daily downloads at 09:30 and 13:00")
            
            # Keep running and check schedule
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Received stop signal")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ Background runner error: {e}")
            raise
    
    def stop(self):
        """Stop the background runner"""
        self.logger.info("🛑 Stopping background runner...")
        self.running = False
        self.logger.info("✅ Background runner stopped")

def main():
    """Main function"""
    print("🚀 Simple WiFi Background Runner")
    print("=" * 40)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        runner = SimpleBackgroundRunner()
        
        if command == "test":
            print("🧪 Running test download...")
            result = runner.run_wifi_download("test")
            if result:
                print("✅ Test download completed successfully")
            else:
                print("❌ Test download failed")
            return
        
        elif command == "add-startup":
            print("📝 Adding to Windows startup...")
            if runner.add_to_startup():
                print("✅ Added to Windows startup successfully")
            else:
                print("❌ Failed to add to startup")
            return
        
        elif command == "remove-startup":
            print("🗑️ Removing from Windows startup...")
            if runner.remove_from_startup():
                print("✅ Removed from Windows startup successfully")
            else:
                print("❌ Failed to remove from startup")
            return
        
        elif command == "morning":
            print("🌅 Running morning slot...")
            result = runner.run_wifi_download("morning")
            if result:
                print("✅ Morning slot completed")
            else:
                print("❌ Morning slot failed")
            return
        
        elif command == "evening":
            print("🌆 Running evening slot...")
            result = runner.run_wifi_download("evening")
            if result:
                print("✅ Evening slot completed")
            else:
                print("❌ Evening slot failed")
            return
        
        else:
            print("Usage: python simple_background_runner.py [test|add-startup|remove-startup|morning|evening]")
            return
    
    # Default - start the background runner
    runner = SimpleBackgroundRunner()
    
    print("🔄 Starting background runner...")
    print("Press Ctrl+C to stop")
    print("")
    
    try:
        runner.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        runner.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        runner.stop()

if __name__ == "__main__":
    main() 