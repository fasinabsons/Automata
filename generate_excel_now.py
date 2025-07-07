#!/usr/bin/env python3
"""
Generate Excel file from current CSV files using dynamic file system
Works with actual CSV headers from EHC system
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.dynamic_file_manager import DynamicFileManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_excel_from_csvs():
    """Generate Excel file from current CSV files using dynamic file system"""
    try:
        # Initialize dynamic file manager
        file_manager = DynamicFileManager()
        
        # Get today's CSV directory
        csv_dir = file_manager.get_download_directory()
        logger.info(f"Using dynamic CSV directory: {csv_dir}")
        
        if not csv_dir.exists():
            logger.error(f"CSV directory not found: {csv_dir}")
            return False
        
        # Get all CSV files
        csv_files = list(csv_dir.glob("*.csv"))
        logger.info(f"Found {len(csv_files)} CSV files")
        
        if len(csv_files) == 0:
            logger.error("No CSV files found")
            return False
        
        # Process all CSV files
        all_data = []
        
        for csv_file in csv_files:
            try:
                logger.info(f"Processing: {csv_file.name}")
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                
                # Select only the columns we need
                required_cols = ['Hostname', 'IP Address', 'MAC Address', 'WLAN (SSID)', 'AP MAC', 'Data Rate (up)', 'Data Rate (down)']
                
                # Check if all required columns exist
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    logger.warning(f"Missing columns in {csv_file.name}: {missing_cols}")
                    continue
                
                # Select and rename columns
                df_selected = df[required_cols].copy()
                
                # Rename columns for Excel
                df_selected = df_selected.rename(columns={
                    'Hostname': 'Hostname',
                    'IP Address': 'IP_Address',
                    'MAC Address': 'MAC_Address',
                    'WLAN (SSID)': 'Package',
                    'AP MAC': 'AP_MAC',
                    'Data Rate (up)': 'Upload',
                    'Data Rate (down)': 'Download'
                })
                
                # Clean data
                df_selected = df_selected.dropna(subset=['MAC_Address'])  # Remove rows without MAC
                df_selected = df_selected.fillna('')  # Fill NaN with empty string
                
                # Add to all data
                all_data.append(df_selected)
                logger.info(f"Added {len(df_selected)} records from {csv_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {csv_file.name}: {e}")
                continue
        
        if not all_data:
            logger.error("No data processed from CSV files")
            return False
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined data: {len(combined_df)} total records")
        
        # Remove duplicates based on MAC address
        combined_df = combined_df.drop_duplicates(subset=['MAC_Address'], keep='first')
        logger.info(f"After removing duplicates: {len(combined_df)} records")
        
        # Get output directory using dynamic file manager
        output_dir = file_manager.get_merge_directory()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Excel filename using dynamic file manager
        excel_filename = file_manager.get_excel_filename()
        excel_path = output_dir / excel_filename
        
        # Save to Excel
        combined_df.to_excel(excel_path, index=False, engine='openpyxl')
        
        logger.info(f"✅ Excel file generated: {excel_path}")
        logger.info(f"📊 Total records: {len(combined_df)}")
        
        # Print summary
        print("\n" + "="*60)
        print("   EXCEL GENERATION COMPLETED")
        print("="*60)
        print(f"📁 Source: {csv_dir}")
        print(f"📄 Files processed: {len(csv_files)}")
        print(f"📊 Total records: {len(combined_df)}")
        print(f"💾 Output: {excel_path}")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating Excel: {e}")
        return False

if __name__ == "__main__":
    success = generate_excel_from_csvs()
    if success:
        print("\n🎉 Excel generation successful!")
    else:
        print("\n❌ Excel generation failed!") 