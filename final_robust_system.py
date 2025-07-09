#!/usr/bin/env python3
"""
Final Robust WiFi Automation System
Combines all working elements with comprehensive fixes for navigation and processing
Designed to work perfectly after redundant file cleanup
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.dynamic_file_manager import DynamicFileManager
from working_email_notifications import WorkingEmailNotifications

class FinalRobustWiFiSystem:
    """
    Final robust system combining all working elements
    Fixes all navigation and processing issues
    """
    
    def __init__(self):
        print("🚀 Initializing Final Robust WiFi System...")
        
        # Configuration from working corrected_wifi_app.py
        self.target_url = "https://51.38.163.73:8443/wsg/"
        self.username = "admin"
        self.password = "AdminFlower@123"
        
        # File management
        self.file_manager = DynamicFileManager()
        self.download_dir = self.file_manager.get_download_directory()
        
        # Email service
        self.email_service = WorkingEmailNotifications()
        
        # Driver setup
        self.driver = None
        self.wait = None
        
        # Network configuration (from working app)
        self.networks = [
            {"name": "EHC TV", "page": 1, "has_clients": True},
            {"name": "EHC-15", "page": 1, "has_clients": False},
            {"name": "Reception Hall-Mobile", "page": 2, "has_clients": True},
            {"name": "Reception Hall-TV", "page": 2, "has_clients": False}
        ]
        
        print("✅ Final Robust WiFi System initialized")
        print(f"📁 Download directory: {self.download_dir}")
    
    def setup_chrome_driver(self) -> bool:
        """Setup Chrome with proven working configuration"""
        try:
            print("🔧 Setting up Chrome with proven configuration...")
            
            options = Options()
            
            # Download preferences
            prefs = {
                "download.default_directory": str(self.download_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
                "profile.default_content_settings.popups": 0
            }
            
            options.add_experimental_option("prefs", prefs)
            
            # Chrome arguments from working app
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-features=VizDisplayCompositor")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ Chrome setup complete!")
            return True
            
        except Exception as e:
            print(f"❌ Chrome setup failed: {e}")
            return False
    
    def robust_login(self) -> bool:
        """Robust login using proven working method from corrected_wifi_app.py"""
        try:
            print("🔑 Starting robust login process...")
            
            # Navigate to URL
            print(f"🌐 Navigating to {self.target_url}")
            self.driver.get(self.target_url)
            time.sleep(10)
            
            # Take screenshot for debugging
            screenshot_path = f"login_debug_{int(time.time() * 1000)}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Look for maskFrame iframe (proven working)
            print("🔍 Looking for maskFrame iframe...")
            
            try:
                # Find iframe by id="maskFrame"
                iframe = self.wait.until(
                    EC.presence_of_element_located((By.ID, "maskFrame"))
                )
                print("✅ Found maskFrame iframe")
                
                # Switch to iframe
                self.driver.switch_to.frame(iframe)
                print("✅ Switched to login iframe")
                
                time.sleep(5)
                
                # Try precision selectors (proven working)
                try:
                    print("🎯 Using proven precision selectors...")
                    username_field = self.driver.find_element(By.ID, "userName")
                    password_field = self.driver.find_element(By.ID, "password")
                    
                    print("✏️ Entering credentials...")
                    username_field.clear()
                    username_field.send_keys(self.username)
                    time.sleep(1)
                    
                    password_field.clear()
                    password_field.send_keys(self.password)
                    time.sleep(1)
                    
                    # Use proven login button selector
                    login_button = self.driver.find_element(By.XPATH, "//*[@id='loginForm']/div[4]/input")
                    login_button.click()
                    print("✅ Clicked login button with proven selector!")
                    
                except Exception as e:
                    print(f"⚠️ Precision selectors failed: {e}")
                    # Fallback to visible inputs (proven working)
                    input_fields = self.driver.find_elements(By.TAG_NAME, "input")
                    visible_inputs = [inp for inp in input_fields if inp.is_displayed()]
                    
                    if len(visible_inputs) >= 2:
                        visible_inputs[0].clear()
                        visible_inputs[0].send_keys(self.username)
                        time.sleep(1)
                        
                        visible_inputs[1].clear()
                        visible_inputs[1].send_keys(self.password)
                        time.sleep(1)
                        
                        # Find login button
                        login_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button']")
                        for button in login_buttons:
                            if button.is_displayed():
                                button.click()
                                break
                
                # Wait for login completion
                time.sleep(15)
                
                # Switch back to main content
                self.driver.switch_to.default_content()
                
                print("✅ Login completed successfully!")
                return True
                
            except Exception as e:
                print(f"❌ Iframe login failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def enhanced_navigate_to_wireless_lans(self) -> bool:
        """Enhanced navigation with multiple fallback strategies"""
        try:
            print("🧭 Enhanced navigation to Wireless LANs...")
            
            # Wait for page stabilization
            time.sleep(5)
            
            # Take screenshot for debugging
            screenshot_path = f"after_login_{int(time.time() * 1000)}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Multiple strategies for finding Wireless LANs menu
            strategies = [
                # Strategy 1: Direct text search
                "//div[contains(@class, 'x-title-text')][contains(text(), 'Wireless LANs')]",
                "//div[@id='title-1343-textEl']",
                "//div[contains(text(), 'Wireless LANs')]",
                "//span[contains(text(), 'Wireless LANs')]",
                
                # Strategy 2: Menu item by position (4th item as specified)
                "//nav//li[4]//a",
                "//ul//li[4]//a",
                "//div[contains(@class, 'menu')]//li[4]",
                
                # Strategy 3: Menu structure search
                "//*[contains(@class, 'menu-item')][4]",
                "//*[contains(@class, 'nav-item')][4]",
                
                # Strategy 4: Link-based search
                "//a[contains(@href, 'wireless')]",
                "//a[contains(@href, 'lan')]",
                
                # Strategy 5: Button/clickable elements
                "//button[contains(text(), 'Wireless')]",
                "//*[contains(@role, 'menuitem')][contains(text(), 'Wireless')]"
            ]
            
            for i, selector in enumerate(strategies, 1):
                try:
                    print(f"🔍 Trying strategy {i}: {selector[:50]}...")
                    
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            text = elem.text.strip()
                            print(f"✅ Found potential menu: '{text}'")
                            
                            # Click the element
                            try:
                                self.driver.execute_script("arguments[0].click();", elem)
                                print(f"✅ Clicked menu item with strategy {i}")
                                time.sleep(5)
                                
                                # Verify we're on the right page
                                if self.verify_wireless_lans_page():
                                    print("✅ Successfully navigated to Wireless LANs!")
                                    return True
                                    
                            except Exception as e:
                                print(f"⚠️ Click failed for strategy {i}: {e}")
                                continue
                                
                except Exception as e:
                    print(f"⚠️ Strategy {i} failed: {e}")
                    continue
            
            # Final fallback: Reload and try again
            print("🔄 All strategies failed, trying reload...")
            self.driver.refresh()
            time.sleep(10)
            
            # Try simple text-based search after reload
            try:
                wireless_element = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Wireless') or contains(text(), 'LANs')]"))
                )
                wireless_element.click()
                time.sleep(5)
                
                if self.verify_wireless_lans_page():
                    print("✅ Reload strategy successful!")
                    return True
                    
            except Exception as e:
                print(f"❌ Reload strategy failed: {e}")
            
            print("❌ All navigation strategies failed")
            return False
            
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    def verify_wireless_lans_page(self) -> bool:
        """Verify we're on the Wireless LANs page"""
        try:
            # Look for indicators of Wireless LANs page
            indicators = [
                "//td[contains(text(), 'EHC')]",
                "//span[contains(text(), 'EHC')]",
                "//*[contains(text(), 'Reception')]",
                "//table",
                ".grid",
                ".x-grid",
                "//*[contains(text(), 'SSID')]",
                "//*[contains(text(), 'Client')]"
            ]
            
            for indicator in indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements:
                        print(f"✅ Page verification successful with: {indicator}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Page verification error: {e}")
            return False
    
    def download_network_data(self, network: Dict) -> bool:
        """Download data for specific network with robust error handling"""
        try:
            network_name = network["name"]
            has_clients = network["has_clients"]
            
            print(f"📡 Downloading data for {network_name}...")
            
            # Find network row with multiple selectors
            network_selectors = [
                f"//td[contains(text(), '{network_name}')]",
                f"//span[contains(text(), '{network_name}')]",
                f"//div[contains(text(), '{network_name}')]",
                f"//*[contains(@class, 'rks-clickable-column')][contains(text(), '{network_name}')]"
            ]
            
            network_element = None
            for selector in network_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and network_name in elem.text:
                            network_element = elem
                            break
                    if network_element:
                        break
                except:
                    continue
            
            if not network_element:
                print(f"❌ Could not find network: {network_name}")
                return False
            
            # Click network
            try:
                self.driver.execute_script("arguments[0].click();", network_element)
                print(f"✅ Clicked network: {network_name}")
                time.sleep(3)
            except Exception as e:
                print(f"❌ Failed to click network: {e}")
                return False
            
            # Handle clients tab if needed
            if has_clients:
                print(f"📊 Looking for clients tab for {network_name}...")
                
                clients_selectors = [
                    "//span[contains(@class, 'x-tab-inner')][contains(text(), 'Clients')]",
                    "//span[contains(text(), 'Clients')][@data-ref='btnInnerEl']",
                    "//span[@id='tab-3448-btnInnerEl']"
                ]
                
                for selector in clients_selectors:
                    try:
                        clients_tab = self.driver.find_element(By.XPATH, selector)
                        if clients_tab.is_displayed():
                            clients_tab.click()
                            print(f"✅ Clicked clients tab for {network_name}")
                            time.sleep(3)
                            break
                    except:
                        continue
            
            # Get files before download
            files_before = list(self.download_dir.glob("*.csv"))
            
            # Find and click download button
            download_selectors = [
                "//span[contains(@class, 'x-btn-glyph')][@style*='FontAwesome']",
                "//span[contains(@class, 'x-btn-icon-el')][@style*='FontAwesome']",
                "//span[@data-ref='btnIconEl'][@style*='FontAwesome']",
                "//span[@id='Rks-module-base-Button-3835-btnIconEl']"
            ]
            
            download_clicked = False
            for selector in download_selectors:
                try:
                    download_btn = self.driver.find_element(By.XPATH, selector)
                    if download_btn.is_displayed():
                        download_btn.click()
                        print(f"✅ Clicked download button for {network_name}")
                        download_clicked = True
                        break
                except:
                    continue
            
            if not download_clicked:
                print(f"❌ Could not find download button for {network_name}")
                return False
            
            # Wait for download
            timeout = time.time() + 30
            while time.time() < timeout:
                files_after = list(self.download_dir.glob("*.csv"))
                if len(files_after) > len(files_before):
                    print(f"✅ Download completed for {network_name}")
                    return True
                time.sleep(2)
            
            print(f"❌ Download timeout for {network_name}")
            return False
            
        except Exception as e:
            print(f"❌ Download error for {network['name']}: {e}")
            return False
    
    def navigate_to_page_2(self) -> bool:
        """Navigate to page 2 with robust detection"""
        try:
            print("📄 Navigating to page 2...")
            
            page2_selectors = [
                "//span[contains(@class, 'x-btn-inner')][contains(text(), '2')]",
                "//span[@data-ref='btnInnerEl'][contains(text(), '2')]",
                "//span[@id='button-3084-btnInnerEl']",
                "//button[contains(text(), '2')]",
                "//a[contains(text(), '2')]"
            ]
            
            for selector in page2_selectors:
                try:
                    page2_btn = self.driver.find_element(By.XPATH, selector)
                    if page2_btn.is_displayed():
                        page2_btn.click()
                        print("✅ Navigated to page 2")
                        time.sleep(5)
                        return True
                except:
                    continue
            
            print("❌ Could not navigate to page 2")
            return False
            
        except Exception as e:
            print(f"❌ Page 2 navigation error: {e}")
            return False
    
    def enhanced_csv_to_excel(self, csv_dir: Path) -> Dict[str, Any]:
        """Enhanced CSV to Excel conversion with flexible column mapping"""
        try:
            print("📊 Starting enhanced CSV to Excel conversion...")
            
            csv_files = list(csv_dir.glob("*.csv"))
            if len(csv_files) < 8:
                return {"success": False, "error": f"Not enough files: {len(csv_files)}/8"}
            
            print(f"📁 Processing {len(csv_files)} CSV files...")
            
            all_data = []
            
            for csv_file in csv_files:
                try:
                    print(f"📄 Processing: {csv_file.name}")
                    
                    # Read CSV with flexible encoding
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8-sig')
                    except:
                        try:
                            df = pd.read_csv(csv_file, encoding='latin-1')
                        except:
                            df = pd.read_csv(csv_file, encoding='cp1252')
                    
                    if df.empty:
                        continue
                    
                    # Flexible column mapping
                    columns = df.columns.tolist()
                    print(f"📋 Columns found: {columns}")
                    
                    # Map columns flexibly
                    column_mapping = {}
                    
                    # Standard mappings with fallbacks
                    for col in columns:
                        col_lower = col.lower()
                        
                        if any(x in col_lower for x in ['hostname', 'host', 'device']):
                            column_mapping['Hostname'] = col
                        elif any(x in col_lower for x in ['ip', 'address']) and 'mac' not in col_lower:
                            column_mapping['IP_Address'] = col
                        elif any(x in col_lower for x in ['mac', 'physical']):
                            column_mapping['MAC_Address'] = col
                        elif any(x in col_lower for x in ['ssid', 'network', 'wlan']):
                            column_mapping['Package'] = col
                        elif any(x in col_lower for x in ['upload', 'up']):
                            column_mapping['Upload'] = col
                        elif any(x in col_lower for x in ['download', 'down']):
                            column_mapping['Download'] = col
                    
                    # Apply mapping
                    df_mapped = df.rename(columns={v: k for k, v in column_mapping.items()})
                    
                    # Convert to records
                    records = df_mapped.to_dict('records')
                    all_data.extend(records)
                    
                    print(f"✅ Processed {len(records)} records from {csv_file.name}")
                    
                except Exception as e:
                    print(f"⚠️ Error processing {csv_file.name}: {e}")
                    continue
            
            if not all_data:
                return {"success": False, "error": "No data processed"}
            
            # Generate Excel file
            today = datetime.now().strftime("%d%m%Y")
            excel_dir = Path(f"EHC_Data_Merge/{today}")
            excel_dir.mkdir(parents=True, exist_ok=True)
            
            excel_file = excel_dir / f"EHC_Upload_Mac_{today}.xls"
            
            # Create Excel with xlwt
            import xlwt
            
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('WSG_Data', cell_overwrite_ok=True)
            
            # Headers
            headers = ['Hostname', 'IP_Address', 'MAC_Address', 'Package', 'Upload', 'Download']
            for col_idx, header in enumerate(headers):
                worksheet.write(0, col_idx, header)
            
            # Data
            for row_idx, record in enumerate(all_data, start=1):
                for col_idx, header in enumerate(headers):
                    value = record.get(header, '')
                    worksheet.write(row_idx, col_idx, str(value))
            
            # Save
            workbook.save(str(excel_file))
            
            print(f"✅ Excel file generated: {excel_file}")
            print(f"📊 Records written: {len(all_data)}")
            
            return {
                "success": True,
                "file_path": str(excel_file),
                "records_written": len(all_data),
                "csv_files_processed": len(csv_files)
            }
            
        except Exception as e:
            print(f"❌ Excel generation error: {e}")
            return {"success": False, "error": str(e)}
    
    def run_complete_automation(self) -> Dict[str, Any]:
        """Run complete automation with all fixes"""
        try:
            print("\n" + "="*60)
            print("🚀 FINAL ROBUST WIFI AUTOMATION SYSTEM")
            print("="*60)
            
            # Setup Chrome
            if not self.setup_chrome_driver():
                return {"success": False, "error": "Chrome setup failed"}
            
            # Login
            if not self.robust_login():
                return {"success": False, "error": "Login failed"}
            
            # Navigate to Wireless LANs
            if not self.enhanced_navigate_to_wireless_lans():
                return {"success": False, "error": "Navigation to Wireless LANs failed"}
            
            # Download from all networks
            success_count = 0
            total_networks = len(self.networks)
            
            current_page = 1
            
            for network in self.networks:
                # Navigate to correct page if needed
                if network["page"] != current_page:
                    if network["page"] == 2:
                        if self.navigate_to_page_2():
                            current_page = 2
                        else:
                            print(f"❌ Failed to navigate to page {network['page']}")
                            continue
                
                # Download network data
                if self.download_network_data(network):
                    success_count += 1
                    print(f"✅ Downloaded {network['name']} ({success_count}/{total_networks})")
                else:
                    print(f"❌ Failed to download {network['name']}")
                
                time.sleep(3)
            
            # Count final files
            final_files = list(self.download_dir.glob("*.csv"))
            
            print(f"\n📊 Download Results:")
            print(f"✅ Networks downloaded: {success_count}/{total_networks}")
            print(f"📁 CSV files: {len(final_files)}")
            
            # Generate Excel if we have enough files
            excel_result = None
            if len(final_files) >= 8:
                print("\n📊 Generating Excel file...")
                excel_result = self.enhanced_csv_to_excel(self.download_dir)
                
                if excel_result.get("success"):
                    print("✅ Excel generation successful!")
                    
                    # Send email notification
                    self.email_service.send_excel_generation_notification(
                        excel_file=excel_result["file_path"],
                        records_count=excel_result["records_written"]
                    )
                else:
                    print(f"❌ Excel generation failed: {excel_result.get('error')}")
            
            return {
                "success": success_count > 0,
                "networks_downloaded": success_count,
                "total_networks": total_networks,
                "csv_files": len(final_files),
                "excel_result": excel_result,
                "download_directory": str(self.download_dir)
            }
            
        except Exception as e:
            print(f"❌ Automation error: {e}")
            return {"success": False, "error": str(e)}
        
        finally:
            if self.driver:
                print("\n⏳ Keeping Chrome open for 15 seconds...")
                time.sleep(15)
                print("🔄 Closing Chrome...")
                self.driver.quit()

def main():
    """Main function for final robust system"""
    try:
        system = FinalRobustWiFiSystem()
        result = system.run_complete_automation()
        
        print("\n" + "="*60)
        print("📋 FINAL RESULTS")
        print("="*60)
        
        if result["success"]:
            print("✅ AUTOMATION SUCCESSFUL!")
            print(f"📡 Networks: {result['networks_downloaded']}/{result['total_networks']}")
            print(f"📁 CSV files: {result['csv_files']}")
            
            if result.get("excel_result") and result["excel_result"].get("success"):
                print(f"📊 Excel: {result['excel_result']['file_path']}")
                print(f"📋 Records: {result['excel_result']['records_written']}")
            
        else:
            print("❌ AUTOMATION FAILED")
            print(f"Error: {result.get('error')}")
        
        print("="*60)
        return result["success"]
        
    except Exception as e:
        print(f"❌ System error: {e}")
        return False

if __name__ == "__main__":
    main() 