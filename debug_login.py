#!/usr/bin/env python3
"""
Debug Login Script
Identifies exact issues with the WiFi login process
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

# Configuration
TARGET_URL = "https://51.38.163.73:8443/wsg/"
USERNAME = "admin"
PASSWORD = "AdminFlower@123"

class LoginDebugger:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_chrome(self):
        """Setup Chrome with debug configuration"""
        try:
            print("🔧 Setting up Chrome for debugging...")
            
            chrome_options = Options()
            
            # Debug settings
            prefs = {
                "download.default_directory": str(Path.cwd() / "debug_downloads"),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True
            }
            
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Chrome arguments
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            print("🚀 Starting Chrome...")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ Chrome setup complete!")
            return True
            
        except Exception as e:
            print(f"❌ Chrome setup failed: {e}")
            return False
    
    def analyze_page_structure(self):
        """Analyze the page structure to understand login elements"""
        try:
            print("🔍 Analyzing page structure...")
            
            # Get page source
            page_source = self.driver.page_source
            print(f"📄 Page source length: {len(page_source)} characters")
            
            # Check for common login indicators
            login_indicators = [
                "username", "password", "login", "signin", "sign-in",
                "email", "user", "pass", "auth", "credential"
            ]
            
            found_indicators = []
            for indicator in login_indicators:
                if indicator.lower() in page_source.lower():
                    found_indicators.append(indicator)
            
            print(f"🔍 Found login indicators: {found_indicators}")
            
            # Check for iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"🖼️ Found {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes):
                try:
                    iframe_id = iframe.get_attribute("id")
                    iframe_src = iframe.get_attribute("src")
                    print(f"   Iframe {i}: ID='{iframe_id}', SRC='{iframe_src}'")
                except:
                    print(f"   Iframe {i}: Could not get attributes")
            
            # Check for input fields
            input_fields = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"📝 Found {len(input_fields)} input fields")
            
            for i, field in enumerate(input_fields):
                try:
                    field_type = field.get_attribute("type")
                    field_name = field.get_attribute("name")
                    field_id = field.get_attribute("id")
                    field_placeholder = field.get_attribute("placeholder")
                    field_visible = field.is_displayed()
                    field_enabled = field.is_enabled()
                    
                    print(f"   Input {i}: type='{field_type}', name='{field_name}', id='{field_id}', placeholder='{field_placeholder}', visible={field_visible}, enabled={field_enabled}")
                except Exception as e:
                    print(f"   Input {i}: Error getting attributes: {e}")
            
            # Check for buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"🔘 Found {len(buttons)} buttons")
            
            for i, button in enumerate(buttons):
                try:
                    button_text = button.text
                    button_type = button.get_attribute("type")
                    button_visible = button.is_displayed()
                    button_enabled = button.is_enabled()
                    
                    print(f"   Button {i}: text='{button_text}', type='{button_type}', visible={button_visible}, enabled={button_enabled}")
                except Exception as e:
                    print(f"   Button {i}: Error getting attributes: {e}")
            
            # Check for forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"📋 Found {len(forms)} forms")
            
            # Save page source for analysis
            debug_file = f"debug_page_source_{int(time.time())}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"💾 Page source saved to: {debug_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Page analysis failed: {e}")
            return False
    
    def test_login_strategies(self):
        """Test different login strategies"""
        try:
            print("🧪 Testing login strategies...")
            
            # Strategy 1: Check for iframe login
            print("\n1️⃣ Testing iframe login...")
            try:
                iframe = self.driver.find_element(By.ID, "maskFrame")
                print("✅ Found maskFrame iframe")
                
                self.driver.switch_to.frame(iframe)
                time.sleep(3)
                
                # Analyze iframe content
                iframe_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                print(f"📝 Found {len(iframe_inputs)} input fields in iframe")
                
                visible_inputs = [inp for inp in iframe_inputs if inp.is_displayed()]
                print(f"👁️ Found {len(visible_inputs)} visible input fields in iframe")
                
                if len(visible_inputs) >= 2:
                    print("✅ Iframe has sufficient input fields for login")
                    
                    # Try to enter credentials
                    try:
                        visible_inputs[0].clear()
                        visible_inputs[0].send_keys(USERNAME)
                        print("✅ Entered username in iframe")
                        
                        visible_inputs[1].clear()
                        visible_inputs[1].send_keys(PASSWORD)
                        print("✅ Entered password in iframe")
                        
                        # Look for login button
                        iframe_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button']")
                        login_button_found = False
                        
                        for button in iframe_buttons:
                            if button.is_displayed():
                                button_text = button.text.lower()
                                button_value = button.get_attribute("value")
                                if button_value:
                                    button_value = button_value.lower()
                                
                                if any(word in button_text or (button_value and word in button_value) for word in ["login", "sign", "submit"]):
                                    print(f"🔘 Found login button: '{button.text}' / '{button_value}'")
                                    button.click()
                                    login_button_found = True
                                    break
                        
                        if not login_button_found:
                            print("⚠️ No login button found in iframe, trying Enter key")
                            visible_inputs[1].send_keys(Keys.RETURN)
                        
                        print("⏳ Waiting for iframe login response...")
                        time.sleep(10)
                        
                        # Check if login was successful
                        self.driver.switch_to.default_content()
                        current_url = self.driver.current_url
                        print(f"🌐 Current URL after iframe login: {current_url}")
                        
                        if current_url != TARGET_URL:
                            print("✅ Iframe login appears successful (URL changed)")
                            return True
                        else:
                            print("❌ Iframe login failed (URL unchanged)")
                            
                    except Exception as e:
                        print(f"❌ Error during iframe login: {e}")
                        self.driver.switch_to.default_content()
                else:
                    print("❌ Iframe doesn't have enough input fields")
                    self.driver.switch_to.default_content()
                    
            except Exception as e:
                print(f"❌ Iframe login failed: {e}")
                self.driver.switch_to.default_content()
            
            # Strategy 2: Direct login
            print("\n2️⃣ Testing direct login...")
            
            # Find username field
            username_field = None
            username_selectors = [
                "//input[@placeholder='username']",
                "//input[@placeholder='Username']", 
                "//input[@name='username']",
                "//input[@name='user']",
                "//input[@id='username']",
                "//input[@type='text']"
            ]
            
            for selector in username_selectors:
                try:
                    field = self.driver.find_element(By.XPATH, selector)
                    if field.is_displayed() and field.is_enabled():
                        username_field = field
                        print(f"✅ Found username field: {selector}")
                        break
                except:
                    continue
            
            # Find password field
            password_field = None
            password_selectors = [
                "//input[@placeholder='password']",
                "//input[@placeholder='Password']",
                "//input[@name='password']",
                "//input[@id='password']",
                "//input[@type='password']"
            ]
            
            for selector in password_selectors:
                try:
                    field = self.driver.find_element(By.XPATH, selector)
                    if field.is_displayed() and field.is_enabled():
                        password_field = field
                        print(f"✅ Found password field: {selector}")
                        break
                except:
                    continue
            
            # Fallback: use first two visible inputs
            if not username_field or not password_field:
                print("🔄 Using fallback field detection...")
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                visible_inputs = [inp for inp in all_inputs if inp.is_displayed() and inp.is_enabled()]
                
                if len(visible_inputs) >= 2:
                    if not username_field:
                        username_field = visible_inputs[0]
                        print("✅ Using first visible input as username")
                    if not password_field:
                        password_field = visible_inputs[1]
                        print("✅ Using second visible input as password")
            
            # Test direct login
            if username_field and password_field:
                try:
                    print("✏️ Entering credentials for direct login...")
                    username_field.clear()
                    username_field.send_keys(USERNAME)
                    print("✅ Username entered")
                    
                    password_field.clear()
                    password_field.send_keys(PASSWORD)
                    print("✅ Password entered")
                    
                    # Look for login button
                    login_selectors = [
                        "//button[contains(text(), 'Login')]",
                        "//button[contains(text(), 'Sign In')]",
                        "//input[@type='submit']",
                        "//button[@type='submit']"
                    ]
                    
                    login_clicked = False
                    for selector in login_selectors:
                        try:
                            button = self.driver.find_element(By.XPATH, selector)
                            if button.is_displayed() and button.is_enabled():
                                print(f"🔘 Clicking login button: {selector}")
                                button.click()
                                login_clicked = True
                                break
                        except:
                            continue
                    
                    if not login_clicked:
                        print("🔄 No login button found, pressing Enter")
                        password_field.send_keys(Keys.RETURN)
                    
                    print("⏳ Waiting for direct login response...")
                    time.sleep(10)
                    
                    # Check result
                    current_url = self.driver.current_url
                    print(f"🌐 Current URL after direct login: {current_url}")
                    
                    if current_url != TARGET_URL:
                        print("✅ Direct login appears successful (URL changed)")
                        return True
                    else:
                        print("❌ Direct login failed (URL unchanged)")
                        
                except Exception as e:
                    print(f"❌ Error during direct login: {e}")
            else:
                print("❌ Could not find username or password fields for direct login")
            
            return False
            
        except Exception as e:
            print(f"❌ Login strategy testing failed: {e}")
            return False
    
    def run_debug(self):
        """Run complete debug analysis"""
        try:
            print("🚀 Starting Login Debug Analysis")
            print("=" * 50)
            
            # Setup Chrome
            if not self.setup_chrome():
                return False
            
            # Navigate to target URL
            print(f"🌐 Navigating to: {TARGET_URL}")
            self.driver.get(TARGET_URL)
            
            # Wait for page to load
            print("⏳ Waiting for page to load...")
            time.sleep(10)
            
            # Take initial screenshot
            screenshot_path = f"debug_initial_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Initial screenshot saved: {screenshot_path}")
            
            # Analyze page structure
            self.analyze_page_structure()
            
            # Test login strategies
            login_success = self.test_login_strategies()
            
            # Final screenshot
            final_screenshot = f"debug_final_{int(time.time())}.png"
            self.driver.save_screenshot(final_screenshot)
            print(f"📸 Final screenshot saved: {final_screenshot}")
            
            # Summary
            print("\n" + "=" * 50)
            print("🎯 DEBUG SUMMARY")
            print("=" * 50)
            print(f"Login Success: {login_success}")
            print(f"Final URL: {self.driver.current_url}")
            
            return login_success
            
        except Exception as e:
            print(f"❌ Debug analysis failed: {e}")
            return False
        finally:
            if self.driver:
                input("Press Enter to close browser...")
                self.driver.quit()

def main():
    debugger = LoginDebugger()
    debugger.run_debug()

if __name__ == "__main__":
    main() 