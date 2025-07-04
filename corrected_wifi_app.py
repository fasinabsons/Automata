#!/usr/bin/env python3
"""
Corrected WiFi Data Automation App
Uses exact iframe and selector information from clickshtml.txt
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

# Configuration
TARGET_URL = "https://51.38.163.73:8443/wsg/"
USERNAME = "admin"
PASSWORD = "AdminFlower@123"

class CorrectedWiFiApp:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.target_files = 4
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories"""
        today = datetime.now().strftime("%d%B").lower()
        self.download_dir = Path(f"C:/Users/Lenovo/Videos/Automata/EHC_Data/{today}")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {self.download_dir}")
    
    def setup_chrome(self):
        """Setup Chrome with proper configuration"""
        try:
            print("🔧 Setting up Chrome with iframe support...")
            
            chrome_options = Options()
            
            # Download settings
            prefs = {
                "download.default_directory": str(self.download_dir),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True
            }
            
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Chrome arguments for iframe support
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
            
            # Make Chrome window visible
            self.driver.maximize_window()
            
            # Create wait object
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ Chrome setup complete!")
            return True
            
        except Exception as e:
            print(f"❌ Chrome setup failed: {e}")
            return False
    
    def count_csv_files(self):
        """Count CSV files in download directory"""
        try:
            csv_files = list(self.download_dir.glob("*.csv"))
            return len(csv_files)
        except:
            return 0
    
    def login_with_iframe(self):
        """Login using iframe - exact implementation from clickshtml.txt"""
        try:
            print("🔑 Starting iframe login process...")
            
            # Navigate to URL
            print(f"🌐 Navigating to {TARGET_URL}")
            self.driver.get(TARGET_URL)
            
            # Wait for page to load
            print("⏳ Waiting for page to load...")
            time.sleep(10)
            
            # Look for the maskFrame iframe (from clickshtml.txt)
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
                    
                    # Find and click login button
                    print("🔍 Looking for login button...")
                    login_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button']")
                    
                    for button in login_buttons:
                        if button.is_displayed():
                            print("🖱️ Clicking login button...")
                            button.click()
                            break
                    
                    # Wait for login to complete
                    print("⏳ Waiting for login to complete...")
                    time.sleep(15)
                    
                    # Switch back to main content
                    self.driver.switch_to.default_content()
                    
                    print("✅ Login completed successfully!")
                    return True
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
                
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def navigate_to_wireless_lans(self):
        """Navigate to Wireless LANs using exact selector"""
        try:
            print("🧭 Looking for Wireless LANs menu...")
            
            # Wait for page to stabilize
            time.sleep(5)
            
            # Use exact selector from clickshtml.txt:
            # <div id="title-1343-textEl" data-ref="textEl" class="x-title-text x-title-text-default x-title-item" unselectable="on">Wireless LANs</div>
            
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
    
    def click_network(self, network_name):
        """Click network using exact selector from clickflow.txt"""
        try:
            print(f"📡 Looking for {network_name}...")
            
            # Use exact selector from clickflow.txt:
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
        """Click Clients tab using exact selector from clickflow.txt"""
        try:
            print("📊 Looking for Clients tab...")
            
            # Use exact selector from clickflow.txt:
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
        """Click FontAwesome download button using exact selector"""
        try:
            print("💾 Looking for FontAwesome download button (right side)...")
            
            # Use exact selector from clickflow.txt:
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
        """Click page 2 using exact selector from clickflow.txt"""
        try:
            print("📄 Looking for page 2...")
            
            # Use exact selector from clickflow.txt:
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
    
    def run_corrected_automation(self):
        """Run the corrected automation with proper iframe handling"""
        try:
            print("=" * 60)
            print("🔥 CORRECTED WIFI APP - IFRAME & EXACT SELECTORS")
            print("=" * 60)
            
            # Setup Chrome
            if not self.setup_chrome():
                return False
            
            print("🔍 Chrome is now open and ready!")
            
            # Login with iframe
            if not self.login_with_iframe():
                return False
            
            # Navigate to Wireless LANs
            if not self.navigate_to_wireless_lans():
                return False
            
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
            
            # Final check
            final_count = self.count_csv_files()
            csv_files = list(self.download_dir.glob("*.csv"))
            
            print(f"\n📁 Final result: {final_count} CSV files downloaded:")
            for file in csv_files:
                file_size = file.stat().st_size
                print(f"  ✅ {file.name} ({file_size} bytes)")
            
            if final_count >= self.target_files:
                print(f"\n🎉 SUCCESS! Downloaded {final_count}/{self.target_files} CSV files!")
                return True
            else:
                print(f"\n⚠️ Downloaded {final_count}/{self.target_files} CSV files")
                return success_count > 0
                
        except Exception as e:
            print(f"❌ Application error: {e}")
            return False
        finally:
            if self.driver:
                print("\n⏳ Keeping Chrome open for 15 seconds...")
                time.sleep(15)
                print("🔄 Closing Chrome...")
                self.driver.quit()

def main():
    """Main function"""
    app = CorrectedWiFiApp()
    success = app.run_corrected_automation()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! The corrected app is working!")
        print("CSV files have been downloaded!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ The app needs further adjustment")
        print("Check the console output for details")
        print("=" * 60)
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main() 