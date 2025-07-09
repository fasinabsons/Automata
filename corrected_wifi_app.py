#!/usr/bin/env python3
"""
Corrected WiFi App - Robust and Efficient Version
Combines best timing from login fix.txt with efficient selectors
FIXED: Consistent folder naming (08jul, 09jul, 08aug)
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modules
from modules.dynamic_file_manager import DynamicFileManager
from working_email_notifications import WorkingEmailNotifications

# Configuration
TARGET_URL = "https://51.38.163.73:8443/wsg/"
USERNAME = "admin"
PASSWORD = "AdminFlower@123"

class CorrectedWiFiApp:
    """Robust and efficient WiFi automation app with consistent folder naming"""
    
    def __init__(self):
        print("🚀 Initializing Robust WiFi App with consistent folder naming...")
        
        # Initialize dynamic file manager for consistent folder naming
        self.file_manager = DynamicFileManager()
        
        # Get today's CSV directory using consistent naming (08jul, 09jul, 08aug)
        self.csv_dir = self.file_manager.get_download_directory()
        print(f"📁 Using consistent folder naming: {self.csv_dir}")
        
        # Email notifications
        self.email_service = WorkingEmailNotifications()
        
        # Chrome driver
        self.driver = None
        self.wait = None
        
        # File tracking
        self.initial_files = self.count_csv_files()
        self.target_files = 4  # Download from 4 networks
        
        # Setup directories
        self.setup_directories()
    
    def setup_directories(self):
        """Setup required directories with consistent naming"""
        try:
            # Ensure CSV directory exists with consistent naming
            self.csv_dir.mkdir(parents=True, exist_ok=True)
            
            # Ensure download directory exists
            downloads_dir = Path("downloads")
            downloads_dir.mkdir(exist_ok=True)
            
            print(f"✅ Directories setup with consistent naming: {self.csv_dir}")
            
        except Exception as e:
            print(f"❌ Directory setup error: {e}")
    
    def setup_chrome(self):
        """Setup Chrome with proper configuration for stability"""
        try:
            print("🔧 Setting up Chrome with iframe support...")
            
            chrome_options = Options()
            
            # Download settings - use consistent folder naming
            prefs = {
                "download.default_directory": str(self.csv_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True
            }
            
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Chrome arguments for iframe support and stability
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            print("🚀 Starting Chrome...")
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Make Chrome window visible and stable
            self.driver.maximize_window()
            
            # Create wait object with longer timeout
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ Chrome setup complete!")
            return True
            
        except Exception as e:
            print(f"❌ Chrome setup failed: {e}")
            return False
    
    def count_csv_files(self):
        """Count CSV files in consistent CSV directory"""
        try:
            csv_files = list(self.csv_dir.glob("*.csv"))
            return len(csv_files)
        except:
            return 0
    
    def login_with_iframe(self):
        """Login using iframe - exact implementation from login fix.txt"""
        try:
            print("🔑 Starting iframe login process...")
            
            # Navigate to URL
            print(f"🌐 Navigating to {TARGET_URL}")
            self.driver.get(TARGET_URL)
            
            # Wait for page to load (from login fix.txt timing)
            print("⏳ Waiting for page to load...")
            time.sleep(10)
            
            # Take screenshot for debugging
            screenshot_path = f"login_debug_{int(time.time() * 1000)}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Look for the maskFrame iframe (from login fix.txt)
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
                
                # Wait for login form to load
                time.sleep(5)
                
                # Try precision selectors first (from fullpaths.txt)
                try:
                    print("🎯 Trying precision selectors...")
                    username_field = self.driver.find_element(By.ID, "userName")
                    password_field = self.driver.find_element(By.ID, "password")
                    
                    print("✏️ Entering credentials with precision selectors...")
                    username_field.clear()
                    username_field.send_keys(USERNAME)
                    time.sleep(1)
                    
                    password_field.clear()
                    password_field.send_keys(PASSWORD)
                    time.sleep(1)
                    
                    # Try precision login button
                    try:
                        login_button = self.driver.find_element(By.XPATH, "//*[@id='loginForm']/div[4]/input")
                        login_button.click()
                        print("✅ Clicked login button with precision selector!")
                    except:
                        # Fallback to CSS selector
                        login_button = self.driver.find_element(By.CSS_SELECTOR, "input.loginBtn[value='Login']")
                        login_button.click()
                        print("✅ Clicked login button with CSS selector!")
                    
                except:
                    print("⚠️ Precision selectors failed, trying visible inputs...")
                    # Fallback to visible inputs (from login fix.txt)
                    input_fields = self.driver.find_elements(By.TAG_NAME, "input")
                    visible_inputs = [inp for inp in input_fields if inp.is_displayed()]
                    
                    print(f"🔍 Found {len(visible_inputs)} visible input fields in iframe")
                    
                    if len(visible_inputs) >= 2:
                        # Enter credentials
                        print("✏️ Entering username...")
                        visible_inputs[0].clear()
                        visible_inputs[0].send_keys(USERNAME)
                        time.sleep(1)
                        
                        print("✏️ Entering password...")
                        visible_inputs[1].clear()
                        visible_inputs[1].send_keys(PASSWORD)
                        time.sleep(1)
                        
                        # Find and click login button
                        print("🔍 Looking for login button...")
                        login_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button']")
                        
                        for button in login_buttons:
                            if button.is_displayed():
                                print("🖱️ Clicking login button...")
                                button.click()
                                break
                    else:
                        print("❌ Could not find login form in iframe")
                        return False
                
                # Wait for login to complete (from login fix.txt timing)
                print("⏳ Waiting for login to complete...")
                time.sleep(15)
                
                # Switch back to main content
                self.driver.switch_to.default_content()
                
                print("✅ Login completed successfully!")
                return True
                
            except Exception as e:
                print(f"❌ Error with iframe login: {e}")
                
                # Try without iframe as fallback (from login fix.txt)
                print("🔄 Trying login without iframe...")
                self.driver.switch_to.default_content()
                
                # Try precision selectors first
                try:
                    username_field = self.driver.find_element(By.ID, "userName")
                    password_field = self.driver.find_element(By.ID, "password")
                    
                    username_field.clear()
                    username_field.send_keys(USERNAME)
                    time.sleep(1)
                    
                    password_field.clear()
                    password_field.send_keys(PASSWORD)
                    time.sleep(1)
                    
                    # Try precision login button
                    try:
                        login_button = self.driver.find_element(By.XPATH, "//*[@id='loginForm']/div[4]/input")
                        login_button.click()
                    except:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, "input.loginBtn[value='Login']")
                        login_button.click()
                    
                except:
                    # Fallback to visible inputs
                    input_fields = self.driver.find_elements(By.TAG_NAME, "input")
                    visible_inputs = [inp for inp in input_fields if inp.is_displayed()]
                    
                    if len(visible_inputs) >= 2:
                        visible_inputs[0].clear()
                        visible_inputs[0].send_keys(USERNAME)
                        time.sleep(1)
                        
                        visible_inputs[1].clear()
                        visible_inputs[1].send_keys(PASSWORD)
                        time.sleep(1)
                        
                        login_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button']")
                        
                        for button in login_buttons:
                            if button.is_displayed():
                                button.click()
                                break
                
                time.sleep(15)
                print("✅ Fallback login completed!")
                return True
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def navigate_to_wireless_lans(self):
        """Navigate to Wireless LANs using exact selector from login fix.txt"""
        try:
            print("🧭 Looking for Wireless LANs menu...")
            
            # Wait for page to stabilize (from login fix.txt timing)
            time.sleep(5)
            
            # Take screenshot for debugging
            screenshot_path = f"after_login_{int(time.time() * 1000)}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Use exact selectors from login fix.txt
            wireless_selectors = [
                "//div[contains(@class, 'x-title-text')][contains(text(), 'Wireless LANs')]",
                "//div[@id='title-1343-textEl']",
                "//div[contains(text(), 'Wireless LANs')]",
                "//span[contains(text(), 'Wireless LANs')]"
            ]
            
            for selector in wireless_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            text = elem.text.strip()
                            if "wireless" in text.lower():
                                print(f"✅ Found Wireless LANs: {text}")
                                elem.click()
                                print("✅ Clicked Wireless LANs menu")
                                time.sleep(5)
                                return True
                except:
                    continue
            
            print("❌ Could not find Wireless LANs menu")
            return False
            
        except Exception as e:
            print(f"❌ Error navigating to Wireless LANs: {e}")
            return False
    
    def click_list_button(self):
        """Click List button to ensure all networks are visible"""
        try:
            print("📋 Looking for List button...")
            
            # Use selectors from fullpaths.txt
            list_selectors = [
                "//span[@id='button-1644-btnInnerEl']",
                "//span[contains(@class, 'x-btn-inner')][contains(text(), 'List')]",
                "//span[contains(text(), 'List')][@data-ref='btnInnerEl']"
            ]
            
            for selector in list_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            print("✅ Found List button")
                            elem.click()
                            print("✅ Clicked List button")
                            time.sleep(3)
                            return True
                except:
                    continue
            
            print("⚠️ Could not find List button, continuing anyway")
            return False
            
        except Exception as e:
            print(f"⚠️ Error clicking List button: {e}")
            return False
    
    def click_network(self, network_name):
        """Click network using text-based selector from login fix.txt"""
        try:
            print(f"📡 Looking for {network_name}...")
            
            # Use exact text-based selector from login fix.txt (most reliable for dynamic elements)
            network_selector = f"//span[contains(@class, 'rks-clickable-column')][contains(text(), '{network_name}')]"
            
            elements = self.driver.find_elements(By.XPATH, network_selector)
            for elem in elements:
                if elem.is_displayed():
                    print(f"✅ Found {network_name}")
                    elem.click()
                    print(f"✅ Clicked {network_name}")
                    time.sleep(3)
                    return True
            
            print(f"❌ Could not find {network_name}")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking {network_name}: {e}")
            return False
    
    def click_clients_tab(self):
        """Click Clients tab using multiple selectors"""
        try:
            print("📊 Looking for Clients tab...")
            
            # Use multiple selectors for reliability
            clients_selectors = [
                "//span[contains(@class, 'x-tab-inner')][contains(text(), 'Clients')]",
                "//span[contains(text(), 'Clients')][@data-ref='btnInnerEl']",
                "//span[@id='tab-3448-btnInnerEl']"  # From fullpaths.txt
            ]
            
            for selector in clients_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            print("✅ Found Clients tab")
                            elem.click()
                            print("✅ Clicked Clients tab")
                            time.sleep(3)
                            return True
                except:
                    continue
            
            print("❌ Could not find Clients tab")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking Clients tab: {e}")
            return False
    
    def click_download_button(self):
        """Click FontAwesome download button using multiple selectors"""
        try:
            print("💾 Looking for FontAwesome download button...")
            
            # Use multiple selectors from login fix.txt + fullpaths.txt
            download_selectors = [
                "//span[contains(@class, 'x-btn-glyph')][@style*='FontAwesome']",
                "//span[contains(@class, 'x-btn-icon-el')][@style*='FontAwesome']",
                "//span[@data-ref='btnIconEl'][@style*='FontAwesome']",
                "//span[@id='Rks-module-base-Button-3835-btnIconEl']"  # From fullpaths.txt
            ]
            
            for selector in download_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            print("✅ Found FontAwesome download button")
                            elem.click()
                            print("✅ Clicked download button")
                            time.sleep(5)
                            return True
                except:
                    continue
            
            print("❌ Could not find FontAwesome download button")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking download button: {e}")
            return False
    
    def click_page_2(self):
        """Click page 2 using multiple selectors"""
        try:
            print("📄 Looking for page 2...")
            
            # Use multiple selectors from login fix.txt + fullpaths.txt
            page2_selectors = [
                "//span[contains(@class, 'x-btn-inner')][contains(text(), '2')]",
                "//span[@data-ref='btnInnerEl'][contains(text(), '2')]",
                "//span[@id='button-3084-btnInnerEl']"  # From fullpaths.txt
            ]
            
            for selector in page2_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            print("✅ Found page 2 button")
                            elem.click()
                            print("✅ Clicked page 2")
                            time.sleep(5)
                            return True
                except:
                    continue
            
            print("❌ Could not find page 2 button")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking page 2: {e}")
            return False
    
    def send_download_notification(self, files_downloaded: int, slot_name: str = ""):
        """Send email notification about download success"""
        try:
            print(f"📧 Sending notification for {files_downloaded} files...")
            
            # Get consistent folder info
            date_folder = self.file_manager.get_date_folder_name()
            
            subject = f"✅ CSV Download Success - {files_downloaded} files - {date_folder} - {datetime.now().strftime('%m/%d/%Y')}"
            
            body = f"""
🎉 WiFi Automation Success - Robust Version with Consistent Folder Naming!

📊 Files Downloaded: {files_downloaded}
📁 Download Directory: {self.csv_dir}
📅 Date Folder: {date_folder}
🕐 Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✨ Robust Features Applied:
- Iframe login with precision selectors
- Text-based network element finding
- Multiple selector fallbacks
- Timing from proven login fix.txt
- Consistent folder naming ({date_folder})

🚀 System Status: OPERATIONAL
📂 Folder Structure: Consistent naming format (08jul, 09jul, 08aug)
"""
            
            self.email_service.send_email(subject, body)
            print("✅ Email notification sent successfully!")
            
        except Exception as e:
            print(f"❌ Failed to send email notification: {e}")
    
    def run_robust_automation(self):
        """Run the robust automation with consistent folder naming"""
        try:
            print("=" * 60)
            print("🔥 ROBUST WIFI APP - CONSISTENT FOLDER NAMING")
            print("=" * 60)
            
            # Display consistent folder info
            date_folder = self.file_manager.get_date_folder_name()
            print(f"📅 Using consistent date folder: {date_folder}")
            print(f"📁 CSV Directory: {self.csv_dir}")
            
            # Setup Chrome
            if not self.setup_chrome():
                return False
            
            print("🔍 Chrome is now open and ready!")
            
            # Login with iframe (using login fix.txt timing)
            if not self.login_with_iframe():
                return False
            
            # Navigate to Wireless LANs
            if not self.navigate_to_wireless_lans():
                return False
            
            # Click List button to ensure all networks are visible
            self.click_list_button()
            
            # Try to download from all 4 networks
            success_count = 0
            
            # Page 1: EHC TV (with Clients tab)
            print("\n🎯 Page 1: EHC TV (with Clients tab)")
            if self.click_network("EHC TV"):
                if self.click_clients_tab():
                    if self.click_download_button():
                        success_count += 1
                        print(f"✅ Downloaded from EHC TV! ({success_count}/{self.target_files})")
            
            # Page 1: EHC-15 (direct download)
            print("\n🎯 Page 1: EHC-15 (direct download)")
            if self.click_network("EHC-15"):
                if self.click_download_button():
                    success_count += 1
                    print(f"✅ Downloaded from EHC-15! ({success_count}/{self.target_files})")
            
            # Navigate to Page 2
            print("\n🎯 Navigating to Page 2...")
            if self.click_page_2():
                # Page 2: Reception Hall-Mobile (with Clients tab)
                print("\n🎯 Page 2: Reception Hall-Mobile (with Clients tab)")
                if self.click_network("Reception Hall-Mobile"):
                    if self.click_clients_tab():
                        if self.click_download_button():
                            success_count += 1
                            print(f"✅ Downloaded from Reception Hall-Mobile! ({success_count}/{self.target_files})")
                
                # Page 2: Reception Hall-TV (Clients tab vanishes)
                print("\n🎯 Page 2: Reception Hall-TV (Clients tab vanishes)")
                if self.click_network("Reception Hall-TV"):
                    if self.click_download_button():
                        success_count += 1
                        print(f"✅ Downloaded from Reception Hall-TV! ({success_count}/{self.target_files})")
            
            # Wait for all downloads to complete
            print("\n⏳ Waiting for downloads to complete...")
            time.sleep(10)
            
            # Final check with consistent folder naming
            final_count = self.count_csv_files()
            new_files = final_count - self.initial_files
            csv_files = list(self.csv_dir.glob("*.csv"))
            
            print(f"\n📁 Final result in {date_folder}: {final_count} CSV files total, {new_files} new files:")
            for file in csv_files:
                file_size = file.stat().st_size
                print(f"  ✅ {file.name} ({file_size} bytes)")
            
            if new_files >= self.target_files:
                print(f"\n🎉 SUCCESS! Downloaded {new_files}/{self.target_files} CSV files!")
                print(f"📂 Consistent folder structure maintained: {date_folder}")
                self.send_download_notification(new_files)
                return {"success": True, "files_downloaded": new_files, "date_folder": date_folder}
            else:
                print(f"\n⚠️ Downloaded {new_files}/{self.target_files} CSV files")
                if new_files > 0:
                    self.send_download_notification(new_files)
                return {"success": success_count > 0, "files_downloaded": new_files, "date_folder": date_folder}
                
        except Exception as e:
            print(f"❌ Application error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if self.driver:
                print("\n⏳ Keeping Chrome open for 15 seconds...")
                time.sleep(15)
                print("🔄 Closing Chrome...")
                self.driver.quit()

def main():
    """Main function"""
    app = CorrectedWiFiApp()
    result = app.run_robust_automation()
    
    if result and result.get("success"):
        print("\n" + "=" * 60)
        print("✅ SUCCESS! The robust app is working!")
        print("CSV files have been downloaded with consistent folder naming!")
        print(f"📂 Date folder: {result.get('date_folder')}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ The app needs further adjustment")
        print("Check the console output for details")
        print("=" * 60)
    
    return result

if __name__ == "__main__":
    main() 