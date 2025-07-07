#!/usr/bin/env python3
"""
Cleanup Analysis Script
Identifies files that can be safely deleted from the project
"""

import os
from pathlib import Path
from datetime import datetime
import json

class CleanupAnalyzer:
    """
    Analyzes project files and identifies what can be safely deleted
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_results = {
            "safe_to_delete": [],
            "keep_files": [],
            "image_files": [],
            "demo_files": [],
            "log_files": [],
            "temp_files": [],
            "analysis_date": datetime.now().isoformat()
        }
    
    def analyze_project(self):
        """
        Perform comprehensive project analysis
        """
        print("🔍 Analyzing project files...")
        
        # Define file categories
        self.categorize_files()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save analysis results
        self.save_analysis()
        
        print("✅ Analysis complete!")
        return self.analysis_results
    
    def categorize_files(self):
        """
        Categorize all files in the project
        """
        # Files that are safe to delete (debug, temporary, old test files)
        safe_to_delete_patterns = [
            # Debug and screenshot files
            "*.png",
            "debug_*.html",
            "debug_*.py",
            "login_debug_*.png",
            "after_login_*.png",
            "wireless_nav_*.png",
            "debug_*.png",
            
            # Old test files (based on deleted_files list)
            "test_complete_system.py",
            "test_hybrid_scraper.py", 
            "test_login_enhanced.py",
            "test_optimized_login.py",
            "test_direct_scraping.py",
            "test_simple_login.py",
            "test_navigation_fix.py",
            "test_core_functionality.py",
            "test_login_only.py",
            "test_navigation_after_login.py",
            "test_chrome_only.py",
            "test_vbs_login.py",
            
            # Old app versions
            "demo_complete_app.py",
            "clickflow_after_login.py",
            "simple_navigation_test.py",
            "fixed_clickflow.py",
            "working_app.py",
            "robust_wifi_app.py",
            "final_wifi_app.py",
            "visible_wifi_app.py",
            "persistent_wifi_app.py",
            
            # Old monitoring files
            "monitor_downloads.py",
            "download_csv_files.py",
            
            # Old documentation
            "COMPLETION_SUMMARY.md",
            "ENHANCED_SERVICE_STATUS.md",
            "PRODUCTION_CHECKLIST.md",
            
            # Log files
            "*.log",
            "vbs_automation.log",
            
            # Temporary text files
            "clickshtml.txt",
            "clickflow.txt",
            "Loginfix.txt",
            "stepstodownloadcsv.txt",
            "AfterLogin.txt",
            "csvtoexcel.txt",
            "vbs.txt",
            "login fix.txt",
            "steps.txt",
            
            # Demo and sample files
            "demo_data.csv"
        ]
        
        # Files to keep (essential system files)
        keep_files_patterns = [
            # Core system files
            "main.py",
            "userinput.py",
            "requirements.txt",
            "install.py",
            "automata.txt",
            
            # Active modules
            "modules/*.py",
            "config/*.py",
            "core/*.py",
            "server/**/*.js",
            "src/**/*",
            
            # Configuration files
            "package.json",
            "package-lock.json",
            "tsconfig*.json",
            "vite.config.ts",
            "tailwind.config.js",
            "eslint.config.js",
            "postcss.config.js",
            
            # Active batch files
            "start_enhanced_service.bat",
            "restart_if_needed.bat",
            
            # Active Python files
            "enhanced_service_runner.py",
            "wifi_automation_app.py",
            "corrected_wifi_app.py",
            "error_recovery.py",
            
            # Test files (current)
            "test_email_pdf.py",
            "test_complete_workflow.py",
            "test_email_simple.py",
            "verify_excel_format.py",
            "fix_email_auth.py",
            "check_schedule_status.py",
            
            # Task and status files
            "vbs_task_list.txt",
            "TASKS2.txt",
            "tasks.txt",
            "analysis.txt",
            
            # Current documentation
            "CURRENT_STATUS.md",
            "FINAL_STATUS.md",
            "SETUP_COMPLETE.md",
            "SYSTEM_STATUS_SUMMARY.md",
            "CURSOR_CLOSE_GUIDE.md",
            "BACKEND_TASKS.md",
            
            # Data directories
            "EHC_Data/**/*",
            "EHC_Data_Merge/**/*",
            "EHC_Data_Pdf/**/*",
            "data/**/*",
            "logs/**/*"
        ]
        
        # Scan all files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.project_root)
                
                # Skip hidden directories and files
                if any(part.startswith('.') for part in relative_path.parts):
                    continue
                
                # Skip node_modules
                if 'node_modules' in relative_path.parts:
                    continue
                
                # Categorize file
                if self.matches_patterns(relative_path, safe_to_delete_patterns):
                    self.analysis_results["safe_to_delete"].append(str(relative_path))
                elif self.matches_patterns(relative_path, keep_files_patterns):
                    self.analysis_results["keep_files"].append(str(relative_path))
                elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                    self.analysis_results["image_files"].append(str(relative_path))
                elif file_path.suffix.lower() == '.log':
                    self.analysis_results["log_files"].append(str(relative_path))
                elif 'demo' in file_path.name.lower() or 'sample' in file_path.name.lower():
                    self.analysis_results["demo_files"].append(str(relative_path))
                elif file_path.suffix.lower() in ['.tmp', '.temp', '.bak']:
                    self.analysis_results["temp_files"].append(str(relative_path))
    
    def matches_patterns(self, file_path: Path, patterns: list) -> bool:
        """
        Check if file matches any of the given patterns
        """
        for pattern in patterns:
            if file_path.match(pattern) or str(file_path).endswith(pattern.replace('*', '')):
                return True
        return False
    
    def generate_recommendations(self):
        """
        Generate cleanup recommendations
        """
        print("\n📋 CLEANUP ANALYSIS RESULTS")
        print("=" * 50)
        
        print(f"\n🗑️  SAFE TO DELETE ({len(self.analysis_results['safe_to_delete'])} files):")
        print("These files are debug/test files that can be safely removed:")
        for file in sorted(self.analysis_results['safe_to_delete']):
            print(f"  - {file}")
        
        print(f"\n🖼️  IMAGE FILES ({len(self.analysis_results['image_files'])} files):")
        print("These are screenshot/debug images that can be deleted:")
        for file in sorted(self.analysis_results['image_files']):
            print(f"  - {file}")
        
        print(f"\n📝 LOG FILES ({len(self.analysis_results['log_files'])} files):")
        print("These are log files that can be archived or deleted:")
        for file in sorted(self.analysis_results['log_files']):
            print(f"  - {file}")
        
        print(f"\n🧪 DEMO FILES ({len(self.analysis_results['demo_files'])} files):")
        print("These are demo/sample files that can be deleted:")
        for file in sorted(self.analysis_results['demo_files']):
            print(f"  - {file}")
        
        print(f"\n📦 TEMP FILES ({len(self.analysis_results['temp_files'])} files):")
        print("These are temporary files that can be deleted:")
        for file in sorted(self.analysis_results['temp_files']):
            print(f"  - {file}")
        
        print(f"\n✅ KEEP FILES ({len(self.analysis_results['keep_files'])} files):")
        print("These are essential files that should be kept:")
        for file in sorted(self.analysis_results['keep_files'])[:10]:  # Show first 10
            print(f"  - {file}")
        if len(self.analysis_results['keep_files']) > 10:
            print(f"  ... and {len(self.analysis_results['keep_files']) - 10} more")
        
        # Calculate space savings
        total_deletable = (
            len(self.analysis_results['safe_to_delete']) +
            len(self.analysis_results['image_files']) +
            len(self.analysis_results['log_files']) +
            len(self.analysis_results['demo_files']) +
            len(self.analysis_results['temp_files'])
        )
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total files analyzed: {len(self.analysis_results['keep_files']) + total_deletable}")
        print(f"  Files to keep: {len(self.analysis_results['keep_files'])}")
        print(f"  Files safe to delete: {total_deletable}")
        print(f"  Potential cleanup: {total_deletable} files")
    
    def save_analysis(self):
        """
        Save analysis results to JSON file
        """
        output_file = self.project_root / "cleanup_analysis.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {output_file}")
    
    def execute_cleanup(self, dry_run: bool = True):
        """
        Execute the cleanup (with dry run option)
        """
        if dry_run:
            print("\n🧪 DRY RUN MODE - No files will be deleted")
        else:
            print("\n🗑️  EXECUTING CLEANUP - Files will be deleted!")
        
        files_to_delete = (
            self.analysis_results['safe_to_delete'] +
            self.analysis_results['image_files'] +
            self.analysis_results['log_files'] +
            self.analysis_results['demo_files'] +
            self.analysis_results['temp_files']
        )
        
        deleted_count = 0
        for file_path in files_to_delete:
            full_path = self.project_root / file_path
            
            if full_path.exists():
                print(f"  {'[DRY RUN] Would delete' if dry_run else 'Deleting'}: {file_path}")
                
                if not dry_run:
                    try:
                        full_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"    ❌ Error deleting {file_path}: {e}")
                else:
                    deleted_count += 1
        
        print(f"\n✅ {'Would delete' if dry_run else 'Deleted'} {deleted_count} files")
        
        if dry_run:
            print("\nTo execute actual cleanup, run:")
            print("python cleanup_analysis.py --execute")

def main():
    """
    Main function
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze and cleanup project files")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default is dry run)")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    analyzer = CleanupAnalyzer(args.project_root)
    analyzer.analyze_project()
    
    if args.execute:
        confirm = input("\n⚠️  Are you sure you want to delete these files? (yes/no): ")
        if confirm.lower() == 'yes':
            analyzer.execute_cleanup(dry_run=False)
        else:
            print("❌ Cleanup cancelled")
    else:
        analyzer.execute_cleanup(dry_run=True)

if __name__ == "__main__":
    main() 