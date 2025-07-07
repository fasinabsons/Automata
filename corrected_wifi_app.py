#!/usr/bin/env python3
"""
Corrected WiFi App - Fast and Efficient Version
Fixed login delays and optimized for speed
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
    """Fast and efficient WiFi automation app"""
    
    def __init__(self):
        print("🚀 Initializing Fast WiFi App...")
        
        # Initialize dynamic file manager
        self.file_manager = DynamicFileManager()
        
        # Get today's CSV directory
        self.csv_dir = self.file_manager.get_download_directory()
        print(f"📁 Using dynamic folder: {self.csv_dir}")
        
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
        """Setup required directories"""
        try:
            # Ensure CSV directory exists
            self.csv_dir.mkdir(parents=True, exist_ok=True)
            
            # Ensure download directory exists
            downloads_dir = Path("downloads")
            downloads_dir.mkdir(exist_ok=True)
            
        except Exception as e:
            print(f"❌ Directory setup error: {e}")
    
    def setup_chrome(self):
        """Setup Chrome with proper configuration for stability"""
        try:
            print("🔧 Setting up Chrome with iframe support...")
            
            chrome_options = Options()
            
            # Download settings
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
        """Count CSV files in CSV directory"""
        try:
            csv_files = list(self.csv_dir.glob("*.csv"))
            return len(csv_files)
        except:
            return 0
    
    def fast_login(self):
        """Stable login using iframe - based on working login fix.txt"""
        try:
            print("🔑 Starting STABLE login process...")
            
            # Navigate to URL
            print(f"🌐 Navigating to {TARGET_URL}")
            self.driver.get(TARGET_URL)
            
            # Wait for page to load
            print("⏳ Waiting for page to load...")
            time.sleep(10)
            
            # Take screenshot for debugging
            screenshot_path = f"login_debug_{int(time.time() * 1000)}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Look for the maskFrame iframe
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
                
                # Find input fields in iframe
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
                    
                    print("✅ Entered username: admin")
                    print("✅ Entered password")
                    
                    # Find and click login button
                    print("🔍 Looking for login button...")
                    login_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button']")
                    
                    login_clicked = False
                    for button in login_buttons:
                        if button.is_displayed():
                            print("🖱️ Clicking login button...")
                            button.click()
                            login_clicked = True
                            break
                    
                    if login_clicked:
                        print("✅ Login button clicked!")
                        # Wait for login to complete - REDUCED TO 15 SECONDS
                        print("⏳ Waiting 15 seconds for login to complete...")
                        time.sleep(15)  # REDUCED: User requested 15 seconds
                        self.driver.switch_to.default_content()
                        print("✅ Iframe login completed!")
                        return True
                    else:
                        print("❌ Could not click login button")
                        return False
                else:
                    print("❌ Could not find login form in iframe")
                    return False
                    
            except Exception as e:
                print(f"❌ Error with iframe login: {e}")
                
                # Try without iframe as fallback
                print("🔄 Trying login without iframe...")
                self.driver.switch_to.default_content()
                
                input_fields = self.driver.find_elements(By.TAG_NAME, "input")
                visible_inputs = [inp for inp in input_fields if inp.is_displayed()]
                
                if len(visible_inputs) >= 2:
                    print("✏️ Entering credentials without iframe...")
                    visible_inputs[0].clear()
                    visible_inputs[0].send_keys(USERNAME)
                    time.sleep(1)
                    
                    visible_inputs[1].clear()
                    visible_inputs[1].send_keys(PASSWORD)
                    time.sleep(1)
                    
                    print("✅ Entered username: admin")
                    print("✅ Entered password")
                    
                    login_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button']")
                    
                    login_clicked = False
                    for button in login_buttons:
                        if button.is_displayed():
                            print("🖱️ Clicking login button...")
                            button.click()
                            login_clicked = True
                            break
                    
                    if login_clicked:
                        print("✅ Login button clicked!")
                        
                        # Wait for login completion - REDUCED TO 15 SECONDS
                        print("⏳ Waiting 15 seconds for login...")
                        time.sleep(15)  # REDUCED: User requested 15 seconds
                        
                        # Quick verification
                        print("✅ Fallback login completed!")
                        return True
                    else:
                        print("❌ Could not click login button in fallback")
                        return False
                else:
                    print("❌ Could not find login form in fallback")
                    return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def fast_navigate_to_wireless(self):
        """Navigate to Wireless LANs using stable method from login fix.txt"""
        try:
            print("🧭 Looking for Wireless LANs menu...")
            
            # Wait for page to stabilize after login
            print("⏳ Waiting for page to stabilize after login...")
            time.sleep(8)  # Wait for page to load after login
            
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
                except Exception as e:
                    print(f"❌ Selector failed: {e}")
                    continue
            
            print("❌ Could not find Wireless LANs menu")
            return False
            
        except Exception as e:
            print(f"❌ Error navigating to Wireless LANs: {e}")
            return False
    
    def click_network(self, network_name):
        """Click network using exact selector from login fix.txt"""
        try:
            print(f"📡 Looking for {network_name}...")
            
            # Use exact selector from login fix.txt:
            # <span class=" rks-clickable-column">EHC TV</span>
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
        """Click Clients tab using exact selector from login fix.txt"""
        try:
            print("📊 Looking for Clients tab...")
            
            # Use exact selector from login fix.txt:
            # <span id="tab-3060-btnInnerEl" data-ref="btnInnerEl" unselectable="on" class="x-tab-inner x-tab-inner-default">Clients</span>
            clients_selectors = [
                "//span[@id='tab-3060-btnInnerEl']",
                "//span[contains(@class, 'x-tab-inner')][contains(text(), 'Clients')]",
                "//span[contains(text(), 'Clients')][@data-ref='btnInnerEl']"
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
        """Click FontAwesome download button using exact selector from login fix.txt"""
        try:
            print("💾 Looking for FontAwesome download button...")
            
            # Use exact selector from login fix.txt:
            # <span id="Rks-module-base-Button-3369-btnIconEl" data-ref="btnIconEl" role="presentation" 
            #       unselectable="on" class="x-btn-icon-el x-btn-icon-el-default-toolbar-small  x-btn-glyph" 
            #       style="font-family:FontAwesome !important;"></span>
            download_selectors = [
                "//span[@id='Rks-module-base-Button-3369-btnIconEl']",
                "//span[contains(@class, 'x-btn-glyph')][@style*='FontAwesome']",
                "//span[contains(@class, 'x-btn-icon-el')][@style*='FontAwesome']",
                "//span[@data-ref='btnIconEl'][@style*='FontAwesome']"
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
        """Click page 2 using exact selector from login fix.txt"""
        try:
            print("📄 Looking for page 2...")
            
            # Use exact selector from login fix.txt:
            # <span id="button-2436-btnInnerEl" data-ref="btnInnerEl" unselectable="on" 
            #       class="x-btn-inner x-btn-inner-plain-toolbar-small">2</span>
            page2_selectors = [
                "//span[@id='button-2436-btnInnerEl']",
                "//span[contains(@class, 'x-btn-inner')][contains(text(), '2')]",
                "//span[@data-ref='btnInnerEl'][contains(text(), '2')]"
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
        """Send email notification"""
        try:
            if files_downloaded > 0:
                subject = f"✅ CSV Download Success - {slot_name} - {datetime.now().strftime('%m/%d/%Y')}"
                message = f"Successfully downloaded {files_downloaded} CSV files to {self.csv_dir}"
            else:
                subject = f"❌ CSV Download Failed - {slot_name} - {datetime.now().strftime('%m/%d/%Y')}"
                message = f"Failed to download CSV files to {self.csv_dir}"
            
            print(f"📧 Sending email: {subject}")
            self.email_service.send_email(subject, message)
            
        except Exception as e:
            print(f"❌ Email error: {e}")
    
    def fast_login_with_retry(self):
        """Login with retry and refresh logic - keep Chrome open"""
        max_attempts = 3  # Try up to 3 times with refresh
        
        for attempt in range(max_attempts):
            try:
                print(f"🔑 Login attempt {attempt + 1}/{max_attempts}...")
                
                if attempt > 0:
                    # Refresh the page instead of closing Chrome
                    print("🔄 Refreshing page for retry...")
                    self.driver.refresh()
                    time.sleep(10)  # Wait for refresh to complete
                
                # Try the stable login process
                if self.fast_login():
                    print(f"✅ Login successful on attempt {attempt + 1}!")
                    return True
                else:
                    print(f"❌ Login attempt {attempt + 1} failed")
                    if attempt < max_attempts - 1:
                        print("🔄 Will refresh and try again...")
                        
            except Exception as e:
                print(f"❌ Login attempt {attempt + 1} error: {e}")
                if attempt < max_attempts - 1:
                    print("🔄 Will refresh and try again...")
        
        print("❌ All login attempts failed")
        return False
    
    def download_with_persistence(self):
        """Download from all networks using exact pattern from login fix.txt"""
        print("🎯 Starting download from all networks...")
        
        success_count = 0
        
        # Page 1: EHC TV (with Clients tab) - EXACT PATTERN FROM OLD CODE
        print("\n🎯 Page 1: EHC TV (with Clients tab)")
        if self.click_network("EHC TV"):
            if self.click_clients_tab():
                if self.click_download_button():
                    success_count += 1
                    print(f"✅ Downloaded from EHC TV! ({success_count}/4)")
        
        # Page 1: EHC-15 (direct download) - EXACT PATTERN FROM OLD CODE
        print("\n🎯 Page 1: EHC-15 (direct download)")
        if self.click_network("EHC-15"):
            if self.click_download_button():
                success_count += 1
                print(f"✅ Downloaded from EHC-15! ({success_count}/4)")
        
        # Navigate to Page 2 - EXACT PATTERN FROM OLD CODE
        print("\n🎯 Navigating to Page 2...")
        if self.click_page_2():
            # Page 2: Reception Hall-Mobile (with Clients tab) - EXACT PATTERN FROM OLD CODE
            print("\n🎯 Page 2: Reception Hall-Mobile (with Clients tab)")
            if self.click_network("Reception Hall-Mobile"):
                if self.click_clients_tab():
                    if self.click_download_button():
                        success_count += 1
                        print(f"✅ Downloaded from Reception Hall-Mobile! ({success_count}/4)")
            
            # Page 2: Reception Hall-TV (Clients tab vanishes) - EXACT PATTERN FROM OLD CODE
            print("\n🎯 Page 2: Reception Hall-TV (Clients tab vanishes)")
            if self.click_network("Reception Hall-TV"):
                if self.click_download_button():
                    success_count += 1
                    print(f"✅ Downloaded from Reception Hall-TV! ({success_count}/4)")
        
        return success_count
    
    def run_robust_automation(self):
        """Run automation with robust retry and refresh logic"""
        try:
            print("=" * 60)
            print("🔥 ROBUST WIFI APP - WITH RETRY & REFRESH")
            print("=" * 60)
            
            # Setup Chrome once
            if not self.setup_chrome():
                return {"success": False, "error": "Chrome setup failed", "files_downloaded": 0}
            
            print("🔍 Chrome ready!")
            
            # Login with retry and refresh
            if not self.fast_login_with_retry():
                return {"success": False, "error": "Login failed after all retries", "files_downloaded": 0}
            
            # Navigate to Wireless LANs with retry
            navigation_success = False
            for nav_attempt in range(3):  # Try navigation 3 times
                print(f"🧭 Navigation attempt {nav_attempt + 1}/3...")
                
                if self.fast_navigate_to_wireless():
                    navigation_success = True
                    break
                else:
                    if nav_attempt < 2:
                        print("🔄 Navigation failed, refreshing and trying again...")
                        self.driver.refresh()
                        time.sleep(8)  # Wait for page to load after refresh
            
            if not navigation_success:
                return {"success": False, "error": "Navigation failed after all retries", "files_downloaded": 0}
            
            # Get initial file count
            initial_count = self.count_csv_files()
            
            # Download from all networks with persistence
            success_count = self.download_with_persistence()
            
            # Wait for downloads to complete
            print("\n⏳ Waiting for downloads to complete...")
            time.sleep(10)  # Wait for downloads
            
            # Check final results
            final_count = self.count_csv_files()
            new_files_downloaded = final_count - initial_count
            
            print(f"\n📊 Final Results:")
            print(f"🎯 Networks attempted: 4")
            print(f"📁 Initial files: {initial_count}")
            print(f"📂 Final files: {final_count}")
            print(f"🆕 New files downloaded: {new_files_downloaded}")
            print(f"✅ Successful networks: {success_count}/4")
            
            # Send notification
            if new_files_downloaded > 0 or success_count > 0:
                self.send_download_notification(new_files_downloaded, "Robust")
            
            # Keep Chrome open for inspection
            print("\n⏳ Keeping Chrome open for 15 seconds for inspection...")
            time.sleep(15)
            
            print("🔄 Closing Chrome...")
            self.driver.quit()
            
            return {
                "success": success_count > 0 or new_files_downloaded > 0,
                "files_downloaded": new_files_downloaded,
                "networks_processed": success_count,
                "target_networks": 4,
                "total_files": final_count
            }
            
        except Exception as e:
            print(f"❌ Automation error: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            return {"success": False, "error": str(e), "files_downloaded": 0}

def main():
    """Main function"""
    app = CorrectedWiFiApp()
    result = app.run_robust_automation()
    
    if result["success"]:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Fast app completed!")
        print("CSV files downloaded successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ App needs adjustment")
        print("Check output for details")
        print("=" * 60)
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main() 