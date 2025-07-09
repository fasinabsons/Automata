#!/usr/bin/env python3
"""
CSV to Excel Processor for WiFi Data
Handles 8-file trigger logic and proper header mapping
FIXED: Consistent folder naming and unified file storage
"""

import os
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import re
import traceback

# Excel generation with xlwt for .xls format
try:
    import xlwt
    XLWT_AVAILABLE = True
except ImportError:
    XLWT_AVAILABLE = False

# Import dynamic file manager for consistent folder naming
from modules.dynamic_file_manager import DynamicFileManager

class CSVToExcelProcessor:
    """Enhanced CSV to Excel processor with consistent folder naming - FIXED"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.processed_data = []
        self.file_count = 0
        
        # Initialize dynamic file manager for consistent folder naming
        self.file_manager = DynamicFileManager()
        
        # Required columns mapping (CSV -> Excel) - FIXED to match actual CSV format
        self.REQUIRED_COLUMNS = [
            'Hostname',
            'IP Address', 
            'MAC Address',
            'WLAN (SSID)',  # This is the exact column name in CSV files
            'AP MAC',
            'Data Rate (up)',
            'Data Rate (down)'
        ]
        
        # Column name variations to handle different CSV formats - ENHANCED
        self.COLUMN_MAPPINGS = {
            'Hostname': ['hostname', 'host name', 'host_name', 'device name', 'device_name'],
            'IP Address': ['ip address', 'ip_address', 'ipaddress', 'ip addr', 'ip_addr'],
            'MAC Address': ['mac address', 'mac_address', 'macaddress', 'mac addr', 'mac_addr'],
            'WLAN (SSID)': ['wlan (ssid)', 'wlan ssid', 'wlan_ssid', 'ssid', 'network name', 'network_name'],
            'AP MAC': ['ap mac', 'ap_mac', 'apmac', 'access point mac', 'access_point_mac'],
            'Data Rate (up)': ['data rate (up)', 'data_rate_up', 'upload rate', 'upload_rate', 'up rate', 'up_rate'],
            'Data Rate (down)': ['data rate (down)', 'data_rate_down', 'download rate', 'download_rate', 'down rate', 'down_rate']
        }
        
        # Excel header mapping (CSV -> Excel format)
        self.EXCEL_HEADER_MAPPING = {
            'Hostname': 'Hostname',
            'IP Address': 'IP_Address',
            'MAC Address': 'MAC_Address',
            'WLAN (SSID)': 'Package',
            'AP MAC': 'AP_MAC',
            'Data Rate (up)': 'Upload',
            'Data Rate (down)': 'Download'
        }
        
        if not XLWT_AVAILABLE:
            self.logger.warning("xlwt not available - attempting to install")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "xlwt"])
                import xlwt
                globals()['xlwt'] = xlwt
                globals()['XLWT_AVAILABLE'] = True
                self.logger.info("xlwt installed successfully")
            except Exception as e:
                self.logger.error(f"Failed to install xlwt: {e}")
                raise ImportError("xlwt required for Excel generation")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for CSV processor"""
        logger = logging.getLogger("CSVToExcelProcessor")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"csv_excel_processor_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not logger.handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def get_consistent_folder_paths(self, date: Optional[datetime] = None) -> Dict[str, Path]:
        """Get consistent folder paths using dynamic file manager"""
        if date is None:
            date = datetime.now()
        
        # Use dynamic file manager for consistent folder naming (08jul, 09jul, 08aug)
        csv_dir = self.file_manager.get_download_directory(date)
        merge_dir = self.file_manager.get_merge_directory(date)
        pdf_dir = self.file_manager.get_pdf_directory(date)
        
        return {
            'csv': csv_dir,
            'merge': merge_dir,
            'pdf': pdf_dir,
            'date_folder': self.file_manager.get_date_folder_name(date)
        }
    
    def count_csv_files(self, directory: Union[str, Path]) -> int:
        """Count CSV files in directory"""
        try:
            csv_dir = Path(directory)
            if not csv_dir.exists():
                return 0
            
            csv_files = list(csv_dir.glob("*.csv"))
            return len(csv_files)
        except Exception as e:
            self.logger.error(f"Error counting CSV files: {e}")
            return 0
    
    def should_generate_excel(self, csv_directory: Union[str, Path]) -> bool:
        """Check if we should generate Excel (8 files reached)"""
        file_count = self.count_csv_files(csv_directory)
        self.logger.info(f"CSV files found: {file_count}")
        
        if file_count >= 8:
            self.logger.info("8 files reached - Excel generation triggered!")
            return True
        else:
            self.logger.info(f"Need {8 - file_count} more files for Excel generation")
            return False
    
    def normalize_headers(self, headers: List[str]) -> Dict[str, str]:
        """Normalize CSV headers to standard format - FIXED"""
        header_mapping = {}
        
        # Debug: Print available headers
        self.logger.info(f"Available CSV headers: {headers}")
        
        # First, try exact matches for required columns
        for required_col in self.REQUIRED_COLUMNS:
            if required_col in headers:
                header_mapping[required_col] = required_col
                self.logger.info(f"Exact match found: {required_col}")
                continue
        
        # Then try variations for missing columns
        for standard_header, variations in self.COLUMN_MAPPINGS.items():
            if standard_header in header_mapping.values():
                continue  # Already mapped
                
            for header in headers:
                header_lower = header.strip().lower()
                for variation in variations:
                    if variation.lower() == header_lower:
                        header_mapping[header] = standard_header
                        self.logger.info(f"Variation match found: {header} -> {standard_header}")
                        break
                if header in header_mapping:
                    break
        
        # Final mapping result
        self.logger.info(f"Final header mapping: {header_mapping}")
        
        return header_mapping
    
    def process_csv_file(self, csv_file: Path) -> List[Dict[str, Any]]:
        """Process a single CSV file - ENHANCED with better error handling"""
        try:
            self.logger.info(f"Processing CSV file: {csv_file.name}")
            
            # Try different encodings
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    self.logger.info(f"Successfully read {csv_file.name} with encoding: {encoding}")
                    break
                except Exception as e:
                    self.logger.warning(f"Failed to read {csv_file.name} with encoding {encoding}: {e}")
                    continue
            
            if df is None:
                self.logger.error(f"Could not read {csv_file.name} with any encoding")
                return []
            
            if df.empty:
                self.logger.warning(f"Empty CSV file: {csv_file.name}")
                return []
            
            # Log the actual columns found
            self.logger.info(f"Columns in {csv_file.name}: {list(df.columns)}")
            
            # Normalize headers
            header_mapping = self.normalize_headers(list(df.columns))
            
            if not header_mapping:
                self.logger.warning(f"No recognized headers in {csv_file.name}")
                # Try to use the file anyway with available columns
                available_cols = [col for col in df.columns if col in self.REQUIRED_COLUMNS]
                if available_cols:
                    self.logger.info(f"Using available columns: {available_cols}")
                    header_mapping = {col: col for col in available_cols}
                else:
                    return []
            
            # Apply header mapping
            df_renamed = df.rename(columns=header_mapping)
            
            # Clean and validate data
            df_clean = self._clean_data(df_renamed)
            
            # Convert to list of dictionaries
            records = df_clean.to_dict('records')
            
            # Add source file information
            for record in records:
                record['_source_file'] = csv_file.name
                record['_processed_timestamp'] = datetime.now().isoformat()
            
            self.logger.info(f"Processed {len(records)} records from {csv_file.name}")
            return records
            
        except Exception as e:
            self.logger.error(f"Error processing {csv_file.name}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data with enhanced rules"""
        # Remove completely empty rows
        df_clean = df.dropna(how='all')
        
        # Clean specific columns with enhanced validation
        for col in df_clean.columns:
            if col in self.REQUIRED_COLUMNS:
                # Convert to string and strip whitespace
                df_clean[col] = df_clean[col].astype(str).str.strip()
                
                # Replace 'nan' string with empty string
                df_clean[col] = df_clean[col].replace('nan', '')
                
                # Special cleaning for MAC addresses
                if 'MAC' in col:
                    df_clean[col] = df_clean[col].apply(self._standardize_mac_address)
                    # Remove rows with invalid MAC addresses
                    df_clean = df_clean[df_clean[col].apply(self._is_valid_mac)]
                
                # Special cleaning for IP addresses
                elif 'IP Address' in col:
                    df_clean = df_clean[df_clean[col].apply(self._is_valid_ip)]
                
                # Special cleaning for data rates
                elif 'Data Rate' in col:
                    df_clean[col] = df_clean[col].apply(self._clean_data_rate)
                
                # Special cleaning for hostnames
                elif col == 'Hostname':
                    # Remove rows with empty hostnames
                    df_clean = df_clean[df_clean[col].str.len() > 0]
                
                # Special cleaning for SSID
                elif 'SSID' in col or 'WLAN' in col:
                    # Clean SSID names
                    df_clean[col] = df_clean[col].apply(self._clean_ssid)
        
        return df_clean
    
    def _clean_data_rate(self, rate_str: str) -> str:
        """Clean and standardize data rate values"""
        try:
            if pd.isna(rate_str) or str(rate_str).strip() == '' or str(rate_str).lower() == 'nan':
                return '0'
            
            rate_str = str(rate_str).strip()
            
            # Handle common variations
            if rate_str.lower() in ['n/a', 'na', 'none', '-', '']:
                return '0'
            
            # Extract numeric value from rate string
            numbers = re.findall(r'\d+\.?\d*', rate_str)
            if numbers:
                return str(float(numbers[0]))
            else:
                return '0'
        except Exception:
            return '0'
    
    def _clean_ssid(self, ssid_str: str) -> str:
        """Clean SSID names"""
        try:
            if pd.isna(ssid_str) or str(ssid_str).strip() == '' or str(ssid_str).lower() == 'nan':
                return ''
            
            ssid_str = str(ssid_str).strip()
            
            # Remove quotes if present
            if ssid_str.startswith('"') and ssid_str.endswith('"'):
                ssid_str = ssid_str[1:-1]
            
            return ssid_str
        except Exception:
            return str(ssid_str) if not pd.isna(ssid_str) else ''
    
    def _standardize_mac_address(self, mac_str: str) -> str:
        """Standardize MAC address format"""
        try:
            if pd.isna(mac_str) or str(mac_str).strip() == '':
                return ''
            
            mac_str = str(mac_str).strip().upper()
            
            # Remove all separators and keep only hex characters
            mac_clean = re.sub(r'[^0-9A-F]', '', mac_str)
            
            if len(mac_clean) == 12:
                # Format as XX:XX:XX:XX:XX:XX
                return ':'.join([mac_clean[i:i+2] for i in range(0, 12, 2)])
            else:
                return mac_str
        except Exception:
            return str(mac_str) if not pd.isna(mac_str) else ''
    
    def _is_valid_ip(self, ip_str: str) -> bool:
        """Validate IP address format"""
        try:
            if pd.isna(ip_str) or str(ip_str).strip() == '':
                return False
            
            ip_str = str(ip_str).strip()
            
            # Handle IPv6 format (IP/::)
            if '/' in ip_str:
                ip_str = ip_str.split('/')[0]
            
            parts = ip_str.split('.')
            
            if len(parts) != 4:
                return False
            
            for part in parts:
                if not part.isdigit():
                    return False
                num = int(part)
                if num < 0 or num > 255:
                    return False
            
            return True
        except Exception:
            return False
    
    def _is_valid_mac(self, mac_str: str) -> bool:
        """Enhanced MAC address validation"""
        try:
            if pd.isna(mac_str) or str(mac_str).strip() == '' or str(mac_str).lower() == 'nan':
                return False
            
            mac_str = str(mac_str).strip()
            
            # Check for common MAC address patterns
            mac_patterns = [
                r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',  # XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
                r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$',     # XXXX.XXXX.XXXX
                r'^([0-9A-Fa-f]{12})$'                           # XXXXXXXXXXXX
            ]
            
            for pattern in mac_patterns:
                if re.match(pattern, mac_str):
                    return True
            
            return False
        except Exception:
            return False
    
    def process_all_csv_files(self, csv_directory: Union[str, Path]) -> List[Dict[str, Any]]:
        """Process all CSV files in directory - ENHANCED"""
        try:
            csv_dir = Path(csv_directory)
            if not csv_dir.exists():
                self.logger.error(f"CSV directory not found: {csv_dir}")
                return []
            
            csv_files = list(csv_dir.glob("*.csv"))
            if not csv_files:
                self.logger.warning(f"No CSV files found in {csv_dir}")
                return []
            
            self.logger.info(f"Processing {len(csv_files)} CSV files")
            
            all_data = []
            for csv_file in csv_files:
                file_data = self.process_csv_file(csv_file)
                all_data.extend(file_data)
            
            # Remove duplicates based on MAC address
            unique_data = self._remove_duplicates(all_data)
            
            self.logger.info(f"Total records processed: {len(unique_data)}")
            return unique_data
            
        except Exception as e:
            self.logger.error(f"Error processing CSV files: {e}")
            return []
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates based on MAC address"""
        if not data:
            return []
        
        seen_macs = set()
        unique_data = []
        
        for record in data:
            mac_address = record.get('MAC Address', '').strip()
            if mac_address and mac_address not in seen_macs:
                seen_macs.add(mac_address)
                unique_data.append(record)
        
        duplicates_removed = len(data) - len(unique_data)
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate records")
        
        return unique_data
    
    def generate_excel_file(self, data: List[Dict[str, Any]], output_path: Union[str, Path] = None) -> Dict[str, Any]:
        """Generate Excel file from processed data with consistent folder naming - FIXED"""
        try:
            if not data:
                return {"success": False, "error": "No data to export"}
            
            # Get consistent folder paths
            folders = self.get_consistent_folder_paths()
            
            # Determine output path using consistent naming
            if output_path is None:
                # Use the SAME folder structure as CSV files - merge directory
                date_folder = folders['date_folder']
                excel_filename = f"EHC_Upload_Mac_{date_folder}.xls"
                output_path = folders['merge'] / excel_filename
            
            output_path = Path(output_path)
            
            # Ensure the merge directory exists (same naming as CSV folder)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Generating Excel file: {output_path}")
            self.logger.info(f"Using consistent folder naming: {folders['date_folder']}")
            
            # Create workbook
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('WSG_Data', cell_overwrite_ok=True)
            
            # Define styles
            header_style = xlwt.XFStyle()
            header_font = xlwt.Font()
            header_font.name = 'Arial'
            header_font.bold = True
            header_font.height = 220
            header_style.font = header_font
            
            data_style = xlwt.XFStyle()
            data_font = xlwt.Font()
            data_font.name = 'Arial'
            data_font.height = 200
            data_style.font = data_font
            
            # Excel headers in correct order
            excel_headers = []
            for csv_header in self.REQUIRED_COLUMNS:
                if any(csv_header in record for record in data):
                    excel_header = self.EXCEL_HEADER_MAPPING.get(csv_header, csv_header)
                    excel_headers.append((csv_header, excel_header))
            
            # Write headers
            for col_idx, (csv_header, excel_header) in enumerate(excel_headers):
                worksheet.write(0, col_idx, excel_header, header_style)
                
                # Set column width
                col_width = max(len(excel_header) * 256, 2000)
                worksheet.col(col_idx).width = col_width
            
            # Write data rows
            for row_idx, record in enumerate(data, start=1):
                for col_idx, (csv_header, excel_header) in enumerate(excel_headers):
                    cell_value = record.get(csv_header, '')
                    if cell_value is None:
                        cell_value = ''
                    else:
                        cell_value = str(cell_value).strip()
                    
                    worksheet.write(row_idx, col_idx, cell_value, data_style)
            
            # Save workbook
            workbook.save(str(output_path))
            
            self.logger.info(f"Excel file generated successfully: {output_path}")
            self.logger.info(f"Consistent folder structure maintained: CSV and Excel in {folders['date_folder']}")
            
            return {
                "success": True,
                "file_path": str(output_path),
                "records_written": len(data),
                "columns_written": len(excel_headers),
                "headers": [eh[1] for eh in excel_headers],
                "date_folder": folders['date_folder'],
                "csv_folder": str(folders['csv']),
                "merge_folder": str(folders['merge'])
            }
            
        except Exception as e:
            error_msg = f"Excel generation failed: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": error_msg}
    
    def process_and_generate_excel(self, csv_directory: Union[str, Path] = None, 
                                 output_path: Union[str, Path] = None) -> Dict[str, Any]:
        """Main method: Process CSVs and generate Excel with consistent folder naming - FIXED"""
        try:
            # If no CSV directory specified, use today's consistent folder
            if csv_directory is None:
                folders = self.get_consistent_folder_paths()
                csv_directory = folders['csv']
                self.logger.info(f"Using consistent CSV directory: {csv_directory}")
            
            # Check if we should generate Excel
            if not self.should_generate_excel(csv_directory):
                return {
                    "success": False, 
                    "error": f"Not enough files for Excel generation. Need 8 files, found {self.count_csv_files(csv_directory)}"
                }
            
            # Process all CSV files
            processed_data = self.process_all_csv_files(csv_directory)
            
            if not processed_data:
                return {"success": False, "error": "No data processed from CSV files"}
            
            # Generate Excel file with consistent naming
            excel_result = self.generate_excel_file(processed_data, output_path)
            
            if excel_result.get("success"):
                self.logger.info("Excel generation completed successfully with consistent folder naming!")
                return excel_result
            else:
                return excel_result
                
        except Exception as e:
            error_msg = f"Process and generate Excel failed: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

# Convenience functions
def process_csv_to_excel(csv_directory: Union[str, Path], output_path: Union[str, Path] = None) -> Dict[str, Any]:
    """Process CSV files and generate Excel if 8 files reached"""
    processor = CSVToExcelProcessor()
    return processor.process_and_generate_excel(csv_directory, output_path)

def check_file_count(csv_directory: Union[str, Path]) -> int:
    """Check how many CSV files are in directory"""
    processor = CSVToExcelProcessor()
    return processor.count_csv_files(csv_directory)

# Test function
def test_csv_to_excel():
    """Test CSV to Excel processing with consistent folder naming"""
    processor = CSVToExcelProcessor()
    
    # Test with consistent folder naming
    folders = processor.get_consistent_folder_paths()
    csv_dir = folders['csv']
    
    self.logger.info(f"Testing with consistent folder: {csv_dir}")
    
    if csv_dir.exists():
        result = processor.process_and_generate_excel(csv_dir)
        print(f"Test result: {result}")
        
        if result.get('success'):
            print(f"SUCCESS: Excel file created in consistent folder structure")
            print(f"Date folder: {result.get('date_folder')}")
            print(f"CSV folder: {result.get('csv_folder')}")
            print(f"Merge folder: {result.get('merge_folder')}")
    else:
        print(f"Test directory not found: {csv_dir}")

if __name__ == "__main__":
    test_csv_to_excel() 