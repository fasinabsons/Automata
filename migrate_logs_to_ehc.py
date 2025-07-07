#!/usr/bin/env python3
"""
Log Migration Script
Migrates existing logs to EHC_Logs folder and implements 7-day cleanup
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import glob

def migrate_logs_to_ehc():
    """Migrate all existing logs to EHC_Logs folder"""
    print("🔄 Starting log migration to EHC_Logs folder...")
    
    # Create EHC_Logs directory
    ehc_logs_dir = Path("EHC_Logs")
    ehc_logs_dir.mkdir(exist_ok=True)
    
    # Directories to check for logs
    log_sources = [
        Path("logs"),
        Path("."),  # Root directory
        Path("modules"),
        Path("config"),
        Path("core"),
        Path("server"),
        Path("api")
    ]
    
    migrated_count = 0
    total_size = 0
    
    for source_dir in log_sources:
        if source_dir.exists() and source_dir != ehc_logs_dir:
            print(f"📁 Checking {source_dir}...")
            
            # Find all log files
            log_files = []
            if source_dir == Path("."):
                # Root directory - only get .log files directly
                log_files = list(source_dir.glob("*.log"))
            else:
                # Other directories - get all .log files recursively
                log_files = list(source_dir.rglob("*.log"))
            
            for log_file in log_files:
                try:
                    # Skip if already in EHC_Logs
                    if ehc_logs_dir in log_file.parents or log_file.parent == ehc_logs_dir:
                        continue
                    
                    # Create new filename with source directory info
                    if source_dir == Path("."):
                        new_name = f"migrated_{log_file.name}"
                    else:
                        new_name = f"migrated_{source_dir.name}_{log_file.name}"
                    
                    # Add timestamp if file already exists
                    new_path = ehc_logs_dir / new_name
                    if new_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        stem = new_path.stem
                        suffix = new_path.suffix
                        new_name = f"{stem}_{timestamp}{suffix}"
                        new_path = ehc_logs_dir / new_name
                    
                    # Get file size before moving
                    file_size = log_file.stat().st_size
                    
                    # Move the file
                    shutil.move(str(log_file), str(new_path))
                    
                    migrated_count += 1
                    total_size += file_size
                    
                    print(f"✅ Migrated: {log_file} -> {new_name}")
                    
                except Exception as e:
                    print(f"❌ Error migrating {log_file}: {e}")
    
    if migrated_count > 0:
        size_mb = total_size / (1024 * 1024)
        print(f"\n🎉 Migration completed!")
        print(f"📊 Files migrated: {migrated_count}")
        print(f"💾 Total size: {size_mb:.2f} MB")
    else:
        print("ℹ️ No log files found to migrate")
    
    return migrated_count

def cleanup_old_logs():
    """Clean up log files older than 7 days"""
    print("\n🧹 Starting 7-day log cleanup...")
    
    ehc_logs_dir = Path("EHC_Logs")
    if not ehc_logs_dir.exists():
        print("❌ EHC_Logs directory not found")
        return 0
    
    # Calculate cutoff date (7 days ago)
    cutoff_date = datetime.now() - timedelta(days=7)
    cutoff_timestamp = cutoff_date.timestamp()
    
    deleted_count = 0
    freed_space = 0
    
    # Find all log files
    log_files = list(ehc_logs_dir.glob("*.log*"))
    
    print(f"📋 Found {len(log_files)} log files to check")
    print(f"🗓️ Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    for log_file in log_files:
        try:
            # Get file modification time
            file_mtime = log_file.stat().st_mtime
            file_date = datetime.fromtimestamp(file_mtime)
            
            if file_mtime < cutoff_timestamp:
                file_size = log_file.stat().st_size
                log_file.unlink()
                deleted_count += 1
                freed_space += file_size
                print(f"🗑️ Deleted: {log_file.name} (from {file_date.strftime('%Y-%m-%d')})")
            else:
                print(f"✅ Kept: {log_file.name} (from {file_date.strftime('%Y-%m-%d')})")
        
        except Exception as e:
            print(f"❌ Error processing {log_file.name}: {e}")
    
    if deleted_count > 0:
        freed_mb = freed_space / (1024 * 1024)
        print(f"\n🎉 Cleanup completed!")
        print(f"🗑️ Files deleted: {deleted_count}")
        print(f"💾 Space freed: {freed_mb:.2f} MB")
    else:
        print("ℹ️ No old log files to delete")
    
    return deleted_count

def setup_log_cleanup_schedule():
    """Set up automatic log cleanup schedule"""
    print("\n⏰ Setting up automatic log cleanup schedule...")
    
    try:
        import schedule
        import threading
        import time
        
        def run_cleanup():
            print(f"\n🕐 Scheduled cleanup starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            cleanup_old_logs()
        
        # Schedule cleanup daily at 2 AM
        schedule.every().day.at("02:00").do(run_cleanup)
        
        def scheduler_thread():
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Check every hour
        
        # Start scheduler in background thread
        cleanup_thread = threading.Thread(target=scheduler_thread, daemon=True)
        cleanup_thread.start()
        
        print("✅ Automatic log cleanup scheduled for 2:00 AM daily")
        return True
        
    except ImportError:
        print("❌ Schedule module not available - install with: pip install schedule")
        return False
    except Exception as e:
        print(f"❌ Error setting up schedule: {e}")
        return False

def show_log_statistics():
    """Show current log statistics"""
    print("\n📊 Current Log Statistics:")
    print("-" * 40)
    
    ehc_logs_dir = Path("EHC_Logs")
    if not ehc_logs_dir.exists():
        print("❌ EHC_Logs directory not found")
        return
    
    log_files = list(ehc_logs_dir.glob("*.log*"))
    
    if not log_files:
        print("ℹ️ No log files found")
        return
    
    total_size = sum(f.stat().st_size for f in log_files)
    total_files = len(log_files)
    
    # Recent logs (last 24 hours)
    recent_cutoff = datetime.now() - timedelta(hours=24)
    recent_files = [
        f for f in log_files 
        if datetime.fromtimestamp(f.stat().st_mtime) > recent_cutoff
    ]
    
    # Old logs (older than 7 days)
    old_cutoff = datetime.now() - timedelta(days=7)
    old_files = [
        f for f in log_files 
        if datetime.fromtimestamp(f.stat().st_mtime) < old_cutoff
    ]
    
    print(f"📁 Total log files: {total_files}")
    print(f"💾 Total size: {total_size / (1024 * 1024):.2f} MB")
    print(f"🆕 Recent files (24h): {len(recent_files)}")
    print(f"🗑️ Old files (>7 days): {len(old_files)}")
    
    if log_files:
        oldest = min(log_files, key=lambda f: f.stat().st_mtime)
        newest = max(log_files, key=lambda f: f.stat().st_mtime)
        
        oldest_date = datetime.fromtimestamp(oldest.stat().st_mtime)
        newest_date = datetime.fromtimestamp(newest.stat().st_mtime)
        
        print(f"📅 Oldest log: {oldest.name} ({oldest_date.strftime('%Y-%m-%d')})")
        print(f"📅 Newest log: {newest.name} ({newest_date.strftime('%Y-%m-%d')})")

def main():
    """Main function"""
    print("🚀 EHC Logs Migration and Cleanup Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "migrate":
            migrate_logs_to_ehc()
        elif command == "cleanup":
            cleanup_old_logs()
        elif command == "stats":
            show_log_statistics()
        elif command == "schedule":
            setup_log_cleanup_schedule()
            print("Schedule started - press Ctrl+C to stop")
            try:
                while True:
                    import time
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n👋 Scheduler stopped")
        else:
            print("❌ Unknown command. Use: migrate, cleanup, stats, or schedule")
    else:
        # Run all operations
        print("🔄 Running complete log management setup...")
        
        # 1. Migrate existing logs
        migrated = migrate_logs_to_ehc()
        
        # 2. Clean up old logs
        deleted = cleanup_old_logs()
        
        # 3. Show statistics
        show_log_statistics()
        
        # 4. Set up schedule
        setup_log_cleanup_schedule()
        
        print(f"\n🎉 Log management setup completed!")
        print(f"📊 Summary:")
        print(f"   - Files migrated: {migrated}")
        print(f"   - Files deleted: {deleted}")
        print(f"   - Automatic cleanup: Scheduled for 2:00 AM daily")
        print(f"   - Retention period: 7 days")

if __name__ == "__main__":
    main() 