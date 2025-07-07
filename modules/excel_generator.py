#!/usr/bin/env python3
"""
Enhanced Excel Generator Module
Converts CSV files to Excel 2007 (.xls) format with proper header mapping
Based on csvtoexcel.txt reference implementation
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd
import re

# Excel generation with xlwt for .xls format (Excel 2007 compatibility)
try:
    import xlwt
    XLWT_AVAILABLE = True
except ImportError:
    XLWT_AVAILABLE = False
    logging.warning("xlwt not available - attempting to install")

# Fallback to openpyxl if needed
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

class EnhancedExcelGenerator:
    """Enhanced Excel generation engine with xlwt for .xls format"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self._ensure_xlwt_available()
        
        # CSV to Excel header mapping (exact format required)
        self.HEADER_MAPPING = {
            'Hostname': 'Hostname',
            'IP Address': 'IP_Address',
            'MAC Address': 'MAC_Address',
            'WLAN (SSID)': 'Package',
            'AP MAC': 'AP_MAC',
            'Data Rate (up)': 'Upload',
            'Data Rate (down)': 'Download'
        }
        
        # Excel headers in exact order
        self.EXCEL_HEADERS = [
            'Hostname', 'IP_Address', 'MAC_Address', 'Package', 
            'AP_MAC', 'Upload', 'Download'
        ]
        
        # CSV headers we expect to find
        self.CSV_HEADERS = list(self.HEADER_MAPPING.keys())
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Excel generator"""
        logger = logging.getLogger("ExcelGenerator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _ensure_xlwt_available(self):
        """Ensure xlwt library is available"""
        if not XLWT_AVAILABLE:
            self.logger.warning("xlwt library not found - attempting to install")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "xlwt"])
                # Try importing again after installation
                import xlwt
                globals()['xlwt'] = xlwt
                globals()['XLWT_AVAILABLE'] = True
                self.logger.info("xlwt library installed successfully")
            except Exception as e:
                self.logger.error(f"Failed to install xlwt: {e}")
                raise ImportError("xlwt library not found and could not be installed. Install manually with: pip install xlwt")
    
    def process_csv_files(self, csv_directory: Union[str, Path]) -> List[Dict[str, Any]]:
        """Process all CSV files in a directory and return consolidated data"""
        try:
            csv_dir = Path(csv_directory)
            if not csv_dir.exists():
                self.logger.error(f"CSV directory does not exist: {csv_dir}")
                return []
            
            # Find all CSV files
            csv_files = list(csv_dir.glob("*.csv"))
            if not csv_files:
                self.logger.warning(f"No CSV files found in directory: {csv_dir}")
                return []
            
            self.logger.info(f"Found {len(csv_files)} CSV files to process")
            
            all_data = []
            processed_files = 0
            
            for csv_file in csv_files:
                try:
                    self.logger.info(f"Processing: {csv_file.name}")
                    
                    # Read CSV file with multiple encoding attempts
                    df = self._read_csv_file(csv_file)
                    
                    if df is None or df.empty:
                        self.logger.warning(f"Empty or unreadable CSV file: {csv_file.name}")
                        continue
                    
                    # Standardize headers
                    df = self._standardize_headers(df)
                    
                    # Validate required columns
                    if not self._validate_required_columns(df):
                        self.logger.warning(f"Missing required columns in: {csv_file.name}")
                        continue
                    
                    # Clean and process data
                    df = self._clean_data(df)
                    
                    # Extract only the columns we need
                    df = self._extract_required_columns(df)
                    
                    # Convert to list of dictionaries
                    file_data = df.to_dict('records')
                    
                    # Add source file information
                    for row in file_data:
                        row['_source_file'] = csv_file.name
                    
                    all_data.extend(file_data)
                    processed_files += 1
                    
                    self.logger.info(f"Processed {len(file_data)} rows from {csv_file.name}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing {csv_file.name}: {e}")
                    continue
            
            # Remove duplicates based on MAC address
            if all_data:
                all_data = self._remove_duplicates(all_data)
            
            self.logger.info(f"Successfully processed {processed_files} files with {len(all_data)} total records")
            return all_data
            
        except Exception as e:
            self.logger.error(f"CSV processing failed: {e}")
            return []
    
    def _read_csv_file(self, csv_file: Path) -> Optional[pd.DataFrame]:
        """Read CSV file with multiple encoding attempts"""
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file, encoding=encoding, low_memory=False)
                if not df.empty:
                    self.logger.debug(f"Successfully read {csv_file.name} with {encoding} encoding")
                    return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.warning(f"Error reading {csv_file.name} with {encoding}: {e}")
                continue
        
        self.logger.error(f"Could not read {csv_file.name} with any encoding")
        return None
    
    def _standardize_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize CSV headers to match expected format"""
        # Create a mapping of possible variations to standard headers
        header_variations = {
            'Hostname': [
                'hostname', 'host name', 'host_name', 'device name', 'device_name',
                'client name', 'client_name', 'name', 'device', 'client'
            ],
            'IP Address': [
                'ip address', 'ip_address', 'ipaddress', 'ip addr', 'ip_addr',
                'ip', 'address', 'client ip', 'client_ip'
            ],
            'MAC Address': [
                'mac address', 'mac_address', 'macaddress', 'mac addr', 'mac_addr',
                'mac', 'client mac', 'client_mac', 'hardware address'
            ],
            'WLAN (SSID)': [
                'wlan (ssid)', 'wlan ssid', 'wlan_ssid', 'ssid', 'network name', 
                'network_name', 'wlan', 'wireless network', 'wifi name'
            ],
            'AP MAC': [
                'ap mac', 'ap_mac', 'apmac', 'access point mac', 'access_point_mac',
                'ap mac address', 'ap_mac_address', 'bssid'
            ],
            'Data Rate (up)': [
                'data rate (up)', 'data_rate_up', 'upload rate', 'upload_rate',
                'up rate', 'up_rate', 'tx rate', 'tx_rate', 'upstream'
            ],
            'Data Rate (down)': [
                'data rate (down)', 'data_rate_down', 'download rate', 'download_rate',
                'down rate', 'down_rate', 'rx rate', 'rx_rate', 'downstream'
            ]
        }
        
        # Create column mapping
        column_mapping = {}
        current_columns = [col.strip().lower() for col in df.columns]
        
        for standard_header, variations in header_variations.items():
            for variation in variations:
                if variation.lower() in current_columns:
                    original_col = df.columns[current_columns.index(variation.lower())]
                    column_mapping[original_col] = standard_header
                    break
        
        # Apply mapping
        if column_mapping:
            df = df.rename(columns=column_mapping)
            self.logger.debug(f"Applied header mapping: {column_mapping}")
        
        return df
    
    def _validate_required_columns(self, df: pd.DataFrame) -> bool:
        """Validate that required columns are present"""
        required_columns = ['Hostname', 'IP Address', 'MAC Address', 'WLAN (SSID)']
        available_columns = list(df.columns)
        
        missing_columns = [col for col in required_columns if col not in available_columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            self.logger.error(f"Available columns: {available_columns}")
            return False
        
        return True
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Clean specific columns
        if 'Hostname' in df.columns:
            df['Hostname'] = df['Hostname'].astype(str).str.strip()
            # Replace 'nan' strings with empty strings
            df['Hostname'] = df['Hostname'].replace('nan', '')
        
        if 'IP Address' in df.columns:
            df['IP Address'] = df['IP Address'].astype(str).str.strip()
            # Clean IP addresses - remove /:: suffix if present
            df['IP Address'] = df['IP Address'].str.replace('/::$', '', regex=True)
        
        if 'MAC Address' in df.columns:
            df['MAC Address'] = df['MAC Address'].astype(str).str.strip()
            # Standardize MAC address format
            df['MAC Address'] = df['MAC Address'].apply(self._standardize_mac_address)
        
        if 'WLAN (SSID)' in df.columns:
            df['WLAN (SSID)'] = df['WLAN (SSID)'].astype(str).str.strip()
        
        if 'AP MAC' in df.columns:
            df['AP MAC'] = df['AP MAC'].astype(str).str.strip()
            df['AP MAC'] = df['AP MAC'].apply(self._standardize_mac_address)
        
        # Clean data rate columns - ensure they are numeric
        for rate_col in ['Data Rate (up)', 'Data Rate (down)']:
            if rate_col in df.columns:
                df[rate_col] = pd.to_numeric(df[rate_col], errors='coerce').fillna(0)
        
        # Remove rows with invalid MAC addresses (critical field)
        if 'MAC Address' in df.columns:
            df = df[df['MAC Address'].str.len() > 0]
            df = df[df['MAC Address'] != 'nan']
        
        return df
    
    def _standardize_mac_address(self, mac_str: str) -> str:
        """Standardize MAC address to XX:XX:XX:XX:XX:XX format"""
        try:
            if pd.isna(mac_str) or str(mac_str).strip() == '' or str(mac_str) == 'nan':
                return ''
            
            mac_str = str(mac_str).strip().upper()
            
            # Remove all separators and keep only hex characters
            mac_clean = re.sub(r'[^0-9A-F]', '', mac_str)
            
            if len(mac_clean) == 12:
                # Format as XX:XX:XX:XX:XX:XX
                return ':'.join([mac_clean[i:i+2] for i in range(0, 12, 2)])
            else:
                # Return original if can't standardize
                return mac_str
        except Exception:
            return str(mac_str) if not pd.isna(mac_str) else ''
    
    def _extract_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract only the columns we need for Excel output"""
        required_columns = list(self.HEADER_MAPPING.keys())
        
        # Keep only required columns
        df_filtered = df[required_columns].copy()
        
        return df_filtered
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entries based on MAC address"""
        if not data:
            return data
        
        seen_macs = set()
        unique_data = []
        
        for record in data:
            mac_address = record.get('MAC Address', '').strip()
            if mac_address and mac_address not in seen_macs and mac_address != 'nan':
                seen_macs.add(mac_address)
                unique_data.append(record)
        
        duplicates_removed = len(data) - len(unique_data)
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate records")
        
        return unique_data
    
    def generate_excel_file(self, data: List[Dict[str, Any]], output_path: Union[str, Path]) -> Dict[str, Any]:
        """Generate Excel file from processed data"""
        try:
            if not data:
                return {"success": False, "error": "No data provided for Excel generation"}
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Generating Excel file: {output_file}")
            
            # Create workbook
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('WSG_Data', cell_overwrite_ok=True)
            
            # Define styles
            header_style = xlwt.XFStyle()
            header_font = xlwt.Font()
            header_font.name = 'Arial'
            header_font.bold = True
            header_font.height = 220  # 11pt
            header_style.font = header_font
            
            # Header background
            header_pattern = xlwt.Pattern()
            header_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            header_pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
            header_style.pattern = header_pattern
            
            # Data cell style
            data_style = xlwt.XFStyle()
            data_font = xlwt.Font()
            data_font.name = 'Arial'
            data_font.height = 200  # 10pt
            data_style.font = data_font
            
            # Write headers (Excel format)
            for col_idx, excel_header in enumerate(self.EXCEL_HEADERS):
                worksheet.write(0, col_idx, excel_header, header_style)
                # Set column width based on header length
                worksheet.col(col_idx).width = max(len(excel_header) * 300, 3000)
            
            # Write data rows
            for row_idx, row_data in enumerate(data, start=1):
                for col_idx, excel_header in enumerate(self.EXCEL_HEADERS):
                    # Find corresponding CSV header
                    csv_header = None
                    for csv_h, excel_h in self.HEADER_MAPPING.items():
                        if excel_h == excel_header:
                            csv_header = csv_h
                            break
                    
                    if csv_header:
                        cell_value = row_data.get(csv_header, '')
                        
                        # Handle different data types
                        if cell_value is None or pd.isna(cell_value):
                            cell_value = ''
                        elif isinstance(cell_value, (int, float)):
                            # Keep numeric values as numbers for Upload/Download columns
                            if excel_header in ['Upload', 'Download']:
                                cell_value = float(cell_value) if cell_value != 0 else 0.0
                            else:
                                cell_value = str(cell_value)
                        else:
                            cell_value = str(cell_value).strip()
                        
                        worksheet.write(row_idx, col_idx, cell_value, data_style)
            
            # Save workbook
            workbook.save(str(output_file))
            
            # Get file statistics
            file_stats = output_file.stat()
            
            result = {
                "success": True,
                "file_path": str(output_file),
                "file_size_bytes": file_stats.st_size,
                "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "rows_written": len(data),
                "columns_written": len(self.EXCEL_HEADERS),
                "headers": self.EXCEL_HEADERS,
                "created_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Excel file generated successfully: {output_file}")
            self.logger.info(f"File size: {result['file_size_mb']} MB, Rows: {result['rows_written']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Excel generation failed: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": error_msg}
    
    def generate_excel_from_csv_directory(self, csv_directory: Union[str, Path], 
                                        output_path: Union[str, Path] = None) -> Dict[str, Any]:
        """Generate Excel file from CSV directory (complete workflow)"""
        try:
            self.logger.info("Starting CSV to Excel conversion workflow")
            
            # Process CSV files
            processed_data = self.process_csv_files(csv_directory)
            
            if not processed_data:
                return {"success": False, "error": "No data available after CSV processing"}
            
            # Generate output path if not provided
            if output_path is None:
                csv_dir = Path(csv_directory)
                date_folder = csv_dir.name
                
                # Create merge directory structure
                merge_dir = Path("EHC_Data_Merge") / date_folder
                merge_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate filename with date
                today = datetime.now()
                filename = f"EHC_Upload_Mac_{today.strftime('%d%m%Y')}.xls"
                output_path = merge_dir / filename
            
            # Generate Excel file
            result = self.generate_excel_file(processed_data, output_path)
            
            if result.get("success"):
                self.logger.info("CSV to Excel conversion completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"CSV to Excel workflow failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

# Convenience functions for external use
def generate_excel_from_csv_directory(csv_directory: Union[str, Path], 
                                    output_path: Union[str, Path] = None) -> Dict[str, Any]:
    """Generate Excel file from CSV directory"""
    generator = EnhancedExcelGenerator()
    return generator.generate_excel_from_csv_directory(csv_directory, output_path)

def test_excel_generation():
    """Test Excel generation with current CSV files"""
    generator = EnhancedExcelGenerator()
    
    # Test with EHC_Data/04july directory
    csv_dir = Path("EHC_Data/04july")
    
    if csv_dir.exists():
        print(f"\n🧪 Testing Excel Generation")
        print(f"📁 CSV Directory: {csv_dir}")
        print(f"📄 CSV Files: {len(list(csv_dir.glob('*.csv')))}")
        
        result = generator.generate_excel_from_csv_directory(csv_dir)
        
        print(f"\n📊 Results:")
        print(f"✅ Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"📄 Excel File: {result.get('file_path', 'N/A')}")
            print(f"📏 File Size: {result.get('file_size_mb', 0)} MB")
            print(f"📝 Rows: {result.get('rows_written', 0)}")
            print(f"🏷️ Headers: {result.get('headers', [])}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        print(f"❌ CSV directory not found: {csv_dir}")

if __name__ == "__main__":
    test_excel_generation()