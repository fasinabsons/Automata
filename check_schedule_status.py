#!/usr/bin/env python3
"""
Schedule Status Checker
Shows current schedule and upcoming tasks
"""

import schedule
from datetime import datetime
import sys

def check_schedule_status():
    """Check and display current schedule status"""
    current_time = datetime.now()
    
    print("🕐 WiFi Automation Schedule Status")
    print("=" * 50)
    print(f"📅 Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Show all scheduled jobs
    jobs = schedule.jobs
    if jobs:
        print(f"📋 Scheduled Jobs ({len(jobs)} total):")
        print("-" * 30)
        
        for i, job in enumerate(jobs, 1):
            next_run = job.next_run
            if next_run:
                time_until = next_run - current_time
                hours, remainder = divmod(time_until.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"{i}. Next run: {next_run.strftime('%H:%M:%S')}")
                print(f"   Time until: {int(hours)}h {int(minutes)}m {int(seconds)}s")
                print(f"   Job: {job.job_func}")
                print(f"   Tags: {job.tags}")
                print()
        
        # Show next upcoming job
        next_job = schedule.next_run()
        if next_job:
            time_until = next_job - current_time
            hours, remainder = divmod(time_until.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            print("🚀 NEXT SCHEDULED TASK:")
            print(f"   ⏰ Time: {next_job.strftime('%H:%M:%S')}")
            print(f"   ⏳ In: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    else:
        print("❌ No jobs currently scheduled")
    
    print("=" * 50)
    
    # Check for 9:11 PM specifically
    target_time = current_time.replace(hour=21, minute=11, second=0, microsecond=0)
    if current_time < target_time:
        time_until = target_time - current_time
        minutes, seconds = divmod(time_until.total_seconds(), 60)
        print(f"🎯 Target 9:11 PM test in: {int(minutes)}m {int(seconds)}s")
    elif current_time.hour == 21 and current_time.minute >= 11 and current_time.minute <= 15:
        print("🎯 We're in the 9:11 PM test window!")
    else:
        print("⏰ 9:11 PM test time has passed")

if __name__ == "__main__":
    check_schedule_status() 