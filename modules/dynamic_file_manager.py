#!/usr/bin/env python3
"""
Dynamic File Manager for WiFi Automation System
Handles date-based folder creation and file organization
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from core.logger import logger

class DynamicFileManager:
    """
    Dynamic file manager for organizing WiFi automation files
    Creates date-based folders and manages file movement
    """
    
    def __init__(self, base_data_dir: str = "EHC_Data", 
                 base_merge_dir: str = "EHC_Data_Merge",
                 base_pdf_dir: str = "EHC_Data_Pdf"):
        """
        Initialize the dynamic file manager
        
        Args:
            base_data_dir: Base directory for CSV files
            base_merge_dir: Base directory for Excel files  
            base_pdf_dir: Base directory for PDF files
        """
        self.base_data_dir = Path(base_data_dir)
        self.base_merge_dir = Path(base_merge_dir)
        self.base_pdf_dir = Path(base_pdf_dir)
        
        # Create base directories if they don't exist
        self.base_data_dir.mkdir(parents=True, exist_ok=True)
        self.base_merge_dir.mkdir(parents=True, exist_ok=True)
        self.base_pdf_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Dynamic File Manager initialized with base directories:", "FileManager")
        logger.info(f"  CSV: {self.base_data_dir}", "FileManager")
        logger.info(f"  Excel: {self.base_merge_dir}", "FileManager")
        logger.info(f"  PDF: {self.base_pdf_dir}", "FileManager")
    
    def get_date_folder_name(self, date: Optional[datetime] = None) -> str:
        """
        Get the date folder name in the format DDmonth (e.g., 01aug, 02aug, 15oct)
        
        Args:
            date: Date to use, defaults to today
            
        Returns:
            Date folder name string
        """
        if date is None:
            date = datetime.now()
        
        # Format: DDmonth (e.g., 01aug, 02aug, 15oct, 31dec)
        # Use %d for day (01-31) and %b for abbreviated month (jan, feb, mar, etc.)
        return date.strftime("%d%b").lower()
    
    def create_date_directories(self, date: Optional[datetime] = None) -> Dict[str, Path]:
        """
        Create date-based directories for all file types
        
        Args:
            date: Date to use, defaults to today
            
        Returns:
            Dictionary with paths for each directory type
        """
        date_folder = self.get_date_folder_name(date)
        
        # Create date-specific directories
        csv_dir = self.base_data_dir / date_folder
        merge_dir = self.base_merge_dir / date_folder
        pdf_dir = self.base_pdf_dir / date_folder
        
        # Create directories
        csv_dir.mkdir(parents=True, exist_ok=True)
        merge_dir.mkdir(parents=True, exist_ok=True)
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        directories = {
            'csv': csv_dir,
            'merge': merge_dir,
            'pdf': pdf_dir,
            'date_folder': date_folder
        }
        
        logger.info(f"Created date directories for {date_folder}:", "FileManager")
        for dir_type, path in directories.items():
            if dir_type != 'date_folder':
                logger.info(f"  {dir_type.upper()}: {path}", "FileManager")
        
        return directories
    
    def get_download_directory(self, date: Optional[datetime] = None) -> Path:
        """
        Get the download directory for CSV files
        
        Args:
            date: Date to use, defaults to today
            
        Returns:
            Path to CSV download directory
        """
        date_folder = self.get_date_folder_name(date)
        csv_dir = self.base_data_dir / date_folder
        csv_dir.mkdir(parents=True, exist_ok=True)
        return csv_dir
    
    def get_merge_directory(self, date: Optional[datetime] = None) -> Path:
        """
        Get the merge directory for Excel files
        
        Args:
            date: Date to use, defaults to today
            
        Returns:
            Path to Excel merge directory
        """
        date_folder = self.get_date_folder_name(date)
        merge_dir = self.base_merge_dir / date_folder
        merge_dir.mkdir(parents=True, exist_ok=True)
        return merge_dir
    
    def get_pdf_directory(self, date: Optional[datetime] = None) -> Path:
        """
        Get the PDF directory for report files
        
        Args:
            date: Date to use, defaults to today
            
        Returns:
            Path to PDF report directory
        """
        date_folder = self.get_date_folder_name(date)
        pdf_dir = self.base_pdf_dir / date_folder
        pdf_dir.mkdir(parents=True, exist_ok=True)
        return pdf_dir
    
    def move_files_to_date_folder(self, source_dir: Union[str, Path], 
                                 target_type: str = 'csv',
                                 date: Optional[datetime] = None,
                                 file_pattern: str = "*.csv") -> List[Path]:
        """
        Move files from source directory to date-based target directory
        
        Args:
            source_dir: Source directory containing files to move
            target_type: Type of target directory ('csv', 'merge', 'pdf')
            date: Date to use, defaults to today
            file_pattern: Pattern to match files (e.g., "*.csv", "*.xlsx")
            
        Returns:
            List of moved file paths
        """
        source_path = Path(source_dir)
        
        if not source_path.exists():
            logger.warning(f"Source directory does not exist: {source_path}", "FileManager")
            return []
        
        # Get target directory
        if target_type == 'csv':
            target_dir = self.get_download_directory(date)
        elif target_type == 'merge':
            target_dir = self.get_merge_directory(date)
        elif target_type == 'pdf':
            target_dir = self.get_pdf_directory(date)
        else:
            raise ValueError(f"Invalid target_type: {target_type}")
        
        # Find files to move
        files_to_move = list(source_path.glob(file_pattern))
        moved_files = []
        
        logger.info(f"Moving {len(files_to_move)} files from {source_path} to {target_dir}", "FileManager")
        
        for file_path in files_to_move:
            try:
                # Create unique filename if file already exists
                target_file = target_dir / file_path.name
                counter = 1
                while target_file.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    target_file = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Move the file
                shutil.move(str(file_path), str(target_file))
                moved_files.append(target_file)
                logger.info(f"Moved: {file_path.name} → {target_file.name}", "FileManager")
                
            except Exception as e:
                logger.error(f"Failed to move {file_path.name}: {e}", "FileManager")
        
        logger.info(f"Successfully moved {len(moved_files)} files", "FileManager")
        return moved_files
    
    def organize_downloaded_files(self, temp_download_dir: Union[str, Path],
                                date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Organize downloaded files from temporary directory to date-based structure
        
        Args:
            temp_download_dir: Temporary download directory
            date: Date to use, defaults to today
            
        Returns:
            Dictionary with organization results
        """
        temp_dir = Path(temp_download_dir)
        
        if not temp_dir.exists():
            return {"success": False, "error": "Temporary download directory does not exist"}
        
        try:
            # Create date directories
            directories = self.create_date_directories(date)
            
            # Move CSV files
            csv_files = self.move_files_to_date_folder(
                temp_dir, 'csv', date, "*.csv"
            )
            
            # Clean up temporary directory
            remaining_files = list(temp_dir.glob("*"))
            if not remaining_files:
                try:
                    temp_dir.rmdir()
                    logger.info(f"Removed empty temporary directory: {temp_dir}", "FileManager")
                except:
                    pass  # Don't fail if we can't remove the directory
            
            return {
                "success": True,
                "csv_files_moved": len(csv_files),
                "target_directory": str(directories['csv']),
                "date_folder": directories['date_folder'],
                "moved_files": [str(f) for f in csv_files]
            }
            
        except Exception as e:
            error_msg = f"File organization failed: {e}"
            logger.error(error_msg, "FileManager")
            return {"success": False, "error": error_msg}
    
    def get_excel_filename(self, date: Optional[datetime] = None) -> str:
        """
        Generate Excel filename with date
        
        Args:
            date: Date to use, defaults to today
            
        Returns:
            Excel filename string
        """
        if date is None:
            date = datetime.now()
        
        # Format: EHC_Upload_Mac_DDMMYYYY.xls
        return f"EHC_Upload_Mac_{date.strftime('%d%m%Y')}.xls"
    
    def get_pdf_filename(self, date: Optional[datetime] = None) -> str:
        """
        Generate PDF filename with date
        
        Args:
            date: Date to use, defaults to today
            
        Returns:
            PDF filename string
        """
        if date is None:
            date = datetime.now()
        
        # Format: moon flower active users_DDMMYYYY.pdf
        return f"moon flower active users_{date.strftime('%d%m%Y')}.pdf"
    
    def cleanup_old_files(self, days_to_keep: int = 60) -> Dict[str, Any]:
        """
        Clean up old files older than specified days (default: 60 days = 2 months)
        This gives enough time for manual backup to external hard disk
        
        Args:
            days_to_keep: Number of days to keep files (default: 60 days = 2 months)
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cleanup_stats = {
                'csv_files_deleted': 0,
                'excel_files_deleted': 0,
                'pdf_files_deleted': 0,
                'directories_removed': 0,
                'total_space_freed_mb': 0,
                'errors': []
            }
            
            logger.info(f"Starting cleanup of files older than {days_to_keep} days (cutoff: {cutoff_date.strftime('%Y-%m-%d')})", "FileManager")
            
            # Clean up each directory type
            for base_dir, file_type in [(self.base_data_dir, 'csv'), 
                                       (self.base_merge_dir, 'excel'), 
                                       (self.base_pdf_dir, 'pdf')]:
                
                if not base_dir.exists():
                    continue
                
                for date_dir in base_dir.iterdir():
                    if not date_dir.is_dir():
                        continue
                    
                    try:
                        # Parse date from folder name (e.g., "06jul" -> July 6)
                        folder_date = self._parse_date_folder(date_dir.name)
                        
                        if folder_date and folder_date < cutoff_date:
                            # Calculate space before deletion
                            dir_size = sum(f.stat().st_size for f in date_dir.rglob('*') if f.is_file())
                            
                            # Count files by type
                            if file_type == 'csv':
                                file_count = len(list(date_dir.glob('*.csv')))
                                cleanup_stats['csv_files_deleted'] += file_count
                            elif file_type == 'excel':
                                file_count = len(list(date_dir.glob('*.xls*')))
                                cleanup_stats['excel_files_deleted'] += file_count
                            elif file_type == 'pdf':
                                file_count = len(list(date_dir.glob('*.pdf')))
                                cleanup_stats['pdf_files_deleted'] += file_count
                            
                            # Remove directory and all contents
                            shutil.rmtree(date_dir)
                            cleanup_stats['directories_removed'] += 1
                            cleanup_stats['total_space_freed_mb'] += dir_size / (1024 * 1024)
                            
                            logger.info(f"Removed old directory: {date_dir} ({file_count} files, {dir_size/(1024*1024):.1f}MB)", "FileManager")
                    
                    except Exception as e:
                        error_msg = f"Error cleaning {date_dir}: {e}"
                        cleanup_stats['errors'].append(error_msg)
                        logger.error(error_msg, "FileManager")
            
            logger.info(f"Cleanup completed: {cleanup_stats['directories_removed']} directories, {cleanup_stats['total_space_freed_mb']:.1f}MB freed", "FileManager")
            
            return {
                "success": True,
                "days_to_keep": days_to_keep,
                "cutoff_date": cutoff_date.strftime('%Y-%m-%d'),
                "statistics": cleanup_stats
            }
            
        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            logger.error(error_msg, "FileManager")
            return {"success": False, "error": error_msg}
    
    def _parse_date_folder(self, folder_name: str) -> Optional[datetime]:
        """
        Parse date folder name (e.g., "06jul") back to datetime
        
        Args:
            folder_name: Folder name in format DDmon (e.g., "06jul")
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Map abbreviated month names to numbers
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            if len(folder_name) >= 5:  # e.g., "06jul"
                day_str = folder_name[:2]
                month_str = folder_name[2:5].lower()
                
                if month_str in month_map:
                    current_year = datetime.now().year
                    day = int(day_str)
                    month = month_map[month_str]
                    
                    # Create datetime object
                    folder_date = datetime(current_year, month, day)
                    
                    # If folder date is in the future, it's probably from last year
                    if folder_date > datetime.now():
                        folder_date = datetime(current_year - 1, month, day)
                    
                    return folder_date
            
            return None
            
        except Exception:
            return None
    
    def schedule_monthly_cleanup(self) -> bool:
        """
        Schedule automatic monthly cleanup (to be called by main service)
        This ensures old files are cleaned up automatically after 2 months
        
        Returns:
            True if cleanup was successful
        """
        try:
            logger.info("Running scheduled monthly cleanup (2-month retention)", "FileManager")
            result = self.cleanup_old_files(days_to_keep=60)  # 2 months
            
            if result.get('success'):
                stats = result.get('statistics', {})
                logger.info(f"Monthly cleanup completed: {stats.get('directories_removed', 0)} directories removed", "FileManager")
                return True
            else:
                logger.error(f"Monthly cleanup failed: {result.get('error')}", "FileManager")
                return False
                
        except Exception as e:
            logger.error(f"Scheduled cleanup error: {e}", "FileManager")
            return False
    
    def get_file_statistics(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get file statistics for a specific date
        
        Args:
            date: Date to check, defaults to today
            
        Returns:
            Dictionary with file statistics
        """
        date_folder = self.get_date_folder_name(date)
        
        stats = {
            "date_folder": date_folder,
            "csv_files": 0,
            "excel_files": 0,
            "pdf_files": 0,
            "total_size_mb": 0,
            "directories_exist": {}
        }
        
        # Check each directory type
        for base_dir, file_pattern, key in [
            (self.base_data_dir, "*.csv", "csv_files"),
            (self.base_merge_dir, "*.xls*", "excel_files"),
            (self.base_pdf_dir, "*.pdf", "pdf_files")
        ]:
            date_dir = base_dir / date_folder
            stats["directories_exist"][key] = date_dir.exists()
            
            if date_dir.exists():
                files = list(date_dir.glob(file_pattern))
                stats[key] = len(files)
                
                # Calculate total size
                for file_path in files:
                    try:
                        stats["total_size_mb"] += file_path.stat().st_size / (1024 * 1024)
                    except:
                        pass
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        return stats
    
    def should_create_new_folder(self) -> bool:
        """
        Check if we should create a new folder (at 12:00 AM daily)
        
        Returns:
            True if it's time to create a new folder
        """
        now = datetime.now()
        
        # Check if it's past midnight (12:00 AM)
        if now.hour == 0 and now.minute < 30:  # Within 30 minutes of midnight
            date_folder = self.get_date_folder_name(now)
            csv_dir = self.base_data_dir / date_folder
            
            # If today's folder doesn't exist, create it
            if not csv_dir.exists():
                logger.info(f"Creating new daily folder at {now.strftime('%H:%M:%S')}: {date_folder}", "FileManager")
                return True
        
        return False
    
    def create_daily_folders_if_needed(self) -> bool:
        """
        Create daily folders if it's 12:00 AM and folders don't exist
        
        Returns:
            True if folders were created
        """
        if self.should_create_new_folder():
            self.create_date_directories()
            logger.info("Daily folders created successfully", "FileManager")
            return True
        return False
    
    def count_csv_files_today(self) -> int:
        """
        Count CSV files in today's folder (not yesterday's)
        
        Returns:
            Number of CSV files in today's folder
        """
        today_dir = self.get_download_directory()  # Gets today's folder
        
        if not today_dir.exists():
            logger.info(f"Today's folder doesn't exist yet: {today_dir}", "FileManager")
            return 0
        
        csv_files = list(today_dir.glob("*.csv"))
        count = len(csv_files)
        
        logger.info(f"CSV files in today's folder ({today_dir.name}): {count}", "FileManager")
        return count
    
    def get_current_date_folder_status(self) -> Dict[str, Any]:
        """
        Get status of current date folder
        
        Returns:
            Dictionary with folder status information
        """
        today = datetime.now()
        date_folder = self.get_date_folder_name(today)
        
        csv_dir = self.get_download_directory()
        merge_dir = self.get_merge_directory()
        pdf_dir = self.get_pdf_directory()
        
        csv_count = len(list(csv_dir.glob("*.csv"))) if csv_dir.exists() else 0
        excel_count = len(list(merge_dir.glob("*.xlsx"))) if merge_dir.exists() else 0
        pdf_count = len(list(pdf_dir.glob("*.pdf"))) if pdf_dir.exists() else 0
        
        status = {
            'date_folder': date_folder,
            'csv_dir': str(csv_dir),
            'merge_dir': str(merge_dir),
            'pdf_dir': str(pdf_dir),
            'csv_count': csv_count,
            'excel_count': excel_count,
            'pdf_count': pdf_count,
            'csv_dir_exists': csv_dir.exists(),
            'merge_dir_exists': merge_dir.exists(),
            'pdf_dir_exists': pdf_dir.exists()
        }
        
        logger.info(f"Current date folder status: {date_folder}", "FileManager")
        logger.info(f"  CSV files: {csv_count}", "FileManager")
        logger.info(f"  Excel files: {excel_count}", "FileManager")
        logger.info(f"  PDF files: {pdf_count}", "FileManager")
        
        return status

# Convenience functions for external use
def get_today_directories() -> Dict[str, Path]:
    """Get today's directories"""
    manager = DynamicFileManager()
    return manager.create_date_directories()

def get_download_directory() -> Path:
    """Get today's download directory"""
    manager = DynamicFileManager()
    return manager.get_download_directory()

def organize_files(temp_dir: Union[str, Path]) -> Dict[str, Any]:
    """Organize files from temporary directory"""
    manager = DynamicFileManager()
    return manager.organize_downloaded_files(temp_dir)

if __name__ == "__main__":
    # Test the dynamic file manager
    manager = DynamicFileManager()
    
    # Create today's directories
    dirs = manager.create_date_directories()
    print("Created directories:", dirs)
    
    # Get statistics
    stats = manager.get_file_statistics()
    print("File statistics:", stats) 