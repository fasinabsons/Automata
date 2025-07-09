#!/usr/bin/env python3
"""
Efficient Slot Controller - Single Optimized Scraper Interface
Eliminates redundant scrapers and provides intelligent slot management
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from corrected_wifi_app import CorrectedWiFiApp
from modules.dynamic_file_manager import DynamicFileManager

class EfficientSlotController:
    """
    Single, optimized scraper controller that eliminates redundancy
    """
    
    def __init__(self):
        print("⚡ Initializing Efficient Slot Controller...")
        
        # Use ONLY the corrected_wifi_app (proven working)
        self.primary_scraper = CorrectedWiFiApp()
        
        # File management
        self.file_manager = DynamicFileManager()
        
        # Performance tracking
        self.performance_stats = {
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_files_downloaded": 0,
            "average_download_time": 0,
            "last_successful_run": None
        }
        
        print("✅ Efficient Slot Controller ready")
        print("🎯 Using: corrected_wifi_app (proven working)")
    
    def get_active_scrapers(self) -> Dict[str, str]:
        """Get list of active vs redundant scrapers"""
        return {
            "active_scrapers": [
                "corrected_wifi_app.py - PRIMARY (proven working)",
                "modules/csv_to_excel_processor.py - Excel generation",
                "modules/dynamic_file_manager.py - File management"
            ],
            "redundant_scrapers": [
                "modules/web_scraper.py - REDUNDANT (replaced by corrected_wifi_app)",
                "modules/enhanced_web_scraper.py - REDUNDANT (unnecessary complexity)",
                "modules/hybrid_web_scraper.py - REDUNDANT (over-engineered)"
            ],
            "recommendation": "Keep only corrected_wifi_app.py for scraping"
        }
    
    def run_optimized_download(self, slot_name: str) -> Dict[str, Any]:
        """Run optimized download using only the proven working scraper"""
        start_time = time.time()
        
        print(f"⚡ Starting optimized download for {slot_name}...")
        print("🎯 Using: corrected_wifi_app (proven working)")
        
        try:
            # Count files before
            files_before = self.file_manager.count_csv_files_today()
            
            # Run the ONLY working scraper
            result = self.primary_scraper.run_robust_automation()
            
            # Count files after
            files_after = self.file_manager.count_csv_files_today()
            new_files = files_after - files_before
            
            download_time = time.time() - start_time
            
            if result and result.get("success") and new_files > 0:
                # Update performance stats
                self.performance_stats["successful_downloads"] += 1
                self.performance_stats["total_files_downloaded"] += new_files
                self.performance_stats["last_successful_run"] = datetime.now().isoformat()
                
                # Update average download time
                total_downloads = self.performance_stats["successful_downloads"]
                current_avg = self.performance_stats["average_download_time"]
                new_avg = ((current_avg * (total_downloads - 1)) + download_time) / total_downloads
                self.performance_stats["average_download_time"] = new_avg
                
                print(f"✅ Optimized download successful!")
                print(f"📁 Files downloaded: {new_files}")
                print(f"⏱️ Download time: {download_time:.1f}s")
                print(f"📊 Total files today: {files_after}")
                
                return {
                    "success": True,
                    "slot_name": slot_name,
                    "files_downloaded": new_files,
                    "total_files": files_after,
                    "download_time": download_time,
                    "scraper_used": "corrected_wifi_app"
                }
            else:
                self.performance_stats["failed_downloads"] += 1
                error_msg = result.get("error", "Unknown error") if result else "No result"
                
                print(f"❌ Optimized download failed: {error_msg}")
                
                return {
                    "success": False,
                    "slot_name": slot_name,
                    "error": error_msg,
                    "download_time": download_time,
                    "scraper_used": "corrected_wifi_app"
                }
                
        except Exception as e:
            download_time = time.time() - start_time
            self.performance_stats["failed_downloads"] += 1
            
            print(f"❌ Download error: {e}")
            
            return {
                "success": False,
                "slot_name": slot_name,
                "error": str(e),
                "download_time": download_time,
                "scraper_used": "corrected_wifi_app"
            }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_attempts = (self.performance_stats["successful_downloads"] + 
                         self.performance_stats["failed_downloads"])
        
        success_rate = 0
        if total_attempts > 0:
            success_rate = (self.performance_stats["successful_downloads"] / total_attempts) * 100
        
        return {
            "total_attempts": total_attempts,
            "successful_downloads": self.performance_stats["successful_downloads"],
            "failed_downloads": self.performance_stats["failed_downloads"],
            "success_rate": f"{success_rate:.1f}%",
            "total_files_downloaded": self.performance_stats["total_files_downloaded"],
            "average_download_time": f"{self.performance_stats['average_download_time']:.1f}s",
            "last_successful_run": self.performance_stats["last_successful_run"],
            "primary_scraper": "corrected_wifi_app.py",
            "redundant_scrapers_count": 3
        }
    
    def cleanup_redundant_files(self) -> Dict[str, Any]:
        """Identify redundant files for cleanup (DO NOT DELETE - just report)"""
        redundant_files = [
            "modules/web_scraper.py",
            "modules/enhanced_web_scraper.py", 
            "modules/hybrid_web_scraper.py"
        ]
        
        existing_redundant = []
        for file_path in redundant_files:
            if Path(file_path).exists():
                existing_redundant.append(file_path)
        
        return {
            "redundant_files_found": existing_redundant,
            "recommendation": "These files can be removed as corrected_wifi_app.py handles all scraping",
            "action": "REPORT ONLY - No files deleted (as requested)",
            "primary_scraper": "corrected_wifi_app.py",
            "note": "Keep corrected_wifi_app.py - it's working perfectly"
        }

def test_efficient_controller():
    """Test the efficient slot controller"""
    controller = EfficientSlotController()
    
    print("\n" + "="*50)
    print("EFFICIENT SLOT CONTROLLER TEST")
    print("="*50)
    
    # Show active vs redundant scrapers
    scrapers = controller.get_active_scrapers()
    print("\n📊 SCRAPER ANALYSIS:")
    print("✅ Active Scrapers:")
    for scraper in scrapers["active_scrapers"]:
        print(f"   {scraper}")
    
    print("\n❌ Redundant Scrapers:")
    for scraper in scrapers["redundant_scrapers"]:
        print(f"   {scraper}")
    
    print(f"\n💡 Recommendation: {scrapers['recommendation']}")
    
    # Show cleanup analysis
    cleanup = controller.cleanup_redundant_files()
    print(f"\n🧹 CLEANUP ANALYSIS:")
    print(f"📁 Redundant files found: {len(cleanup['redundant_files_found'])}")
    for file in cleanup['redundant_files_found']:
        print(f"   {file}")
    print(f"💡 {cleanup['recommendation']}")
    print(f"⚠️ {cleanup['action']}")
    
    # Performance report
    report = controller.get_performance_report()
    print(f"\n📈 PERFORMANCE REPORT:")
    print(f"🎯 Primary scraper: {report['primary_scraper']}")
    print(f"📊 Success rate: {report['success_rate']}")
    print(f"⏱️ Average download time: {report['average_download_time']}")
    
    print("\n✅ Efficient Slot Controller test complete")

if __name__ == "__main__":
    test_efficient_controller() 