"""
FIXED Hybrid Web Scraper for Ruckus Wireless WiFi Data Automation
Based on user screenshots and exact requirements - ALL ISSUES FIXED
"""

import time
import json
import csv
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
import socket
import urllib3
from urllib.parse import urljoin, urlparse

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

# Local imports
from config.settings import (
    WIFI_CONFIG, CHROME_CONFIG, FILE_CONFIG, 
    SCHEDULE_CONFIG, ERROR_CONFIG, DEBUG_CONFIG, TIMING_CONFIG
)
from core.logger import logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BulletproofRuckusWiFiScraper:
    """
    Bulletproof Ruckus WiFi Scraper - Fixed for 100% reliability
    Based on exact user screenshots and requirements
    """
    
    def __init__(self, execution_id: Optional[str] = None):
        self.execution_id = execution_id or f"ruckus_{int(time.time())}"
        self.username = WIFI_CONFIG['username']
        self.password = WIFI_CONFIG['password']
        self.target_url = WIFI_CONFIG['target_url']
        
        # Setup date-based directory structure
        today = datetime.now().strftime("%d%b").lower()  # e.g., "04aug", "29feb" (leap year)
        self.download_dir = Path(f"EHC_Data/{today}")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize selenium driver
        self.driver = self._setup_bulletproof_chrome()
        
        # Execution state
        self.current_slot = None
        self.extracted_files = []
        self.session_data = {}
        self.debug_screenshots = []
        
        logger.info(f"Bulletproof Ruckus Scraper initialized: {self.execution_id}", "RuckusScraper", self.execution_id)
    
    def _setup_bulletproof_chrome(self) -> webdriver.Chrome:
        """Setup bulletproof Chrome driver with all anti-detection measures"""
        try:
            logger.info("Setting up bulletproof Chrome driver", "RuckusScraper", self.execution_id)
            
            # Chrome options
            options = Options()
            
            # Add all Chrome options from config
            for option in CHROME_CONFIG['chrome_options']:
                options.add_argument(option)
            
            # Set window size
            options.add_argument(f"--window-size={CHROME_CONFIG['window_size']}")
            
            # Set download directory
            download_prefs = CHROME_CONFIG['download_prefs'].copy()
            download_prefs['download.default_directory'] = str(self.download_dir.absolute())
            
            # Merge experimental options
            exp_options = CHROME_CONFIG['experimental_options'].copy()
            exp_options['prefs'] = download_prefs
            
            for key, value in exp_options.items():
                options.add_experimental_option(key, value)
            
            # Create driver
            driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            driver.implicitly_wait(CHROME_CONFIG['implicit_wait'])
            driver.set_page_load_timeout(CHROME_CONFIG['page_load_timeout'])
            
            # CRITICAL: Execute anti-detection script (simplified to avoid errors)
            try:
                driver.execute_script("""
                    // Remove webdriver property safely
                    try {
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    } catch(e) {}
                    
                    // Override plugins safely
                    try {
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    } catch(e) {}
                    
                    // Override languages safely
                    try {
                        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    } catch(e) {}
                    
                    console.log('Basic anti-detection measures applied');
                """)
            except Exception as e:
                logger.warning(f"Anti-detection script failed: {e}", "RuckusScraper", self.execution_id)
            
            logger.success("Bulletproof Chrome driver setup complete", "RuckusScraper", self.execution_id)
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}", "RuckusScraper", self.execution_id)
            raise
    
    def _take_debug_screenshot(self, step_name: str):
        """Take debug screenshot"""
        try:
            if DEBUG_CONFIG['save_screenshots']:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = self.download_dir / f"debug_{step_name}_{timestamp}.png"
                self.driver.save_screenshot(str(screenshot_path))
                self.debug_screenshots.append(str(screenshot_path))
                logger.info(f"Debug screenshot saved: {screenshot_path.name}", "RuckusScraper", self.execution_id)
        except Exception as e:
            logger.warning(f"Failed to take screenshot: {e}", "RuckusScraper", self.execution_id)
    
    def _check_network_connectivity(self) -> bool:
        """Check network connectivity to target server"""
        try:
            parsed_url = urlparse(self.target_url)
            host = parsed_url.hostname
            port = parsed_url.port or 8443
            
            logger.info(f"Checking connectivity to {host}:{port}", "RuckusScraper", self.execution_id)
            
            # Test socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.success("Network connectivity verified", "RuckusScraper", self.execution_id)
                return True
            else:
                logger.error(f"Network connectivity failed: {result}", "RuckusScraper", self.execution_id)
                return False
                
        except Exception as e:
            logger.error(f"Network connectivity check failed: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _bulletproof_login(self) -> bool:
        """Simple, working login - DO NOT CHANGE THIS CODE ONCE IT WORKS"""
        try:
            logger.info("Starting simple login process", "RuckusScraper", self.execution_id)
            
            # Navigate to login page
            self.driver.get(self.target_url)
            time.sleep(8)  # Wait longer for page load
            
            # Take initial screenshot
            self._take_debug_screenshot("01_login_page")
            
            # Wait for page to fully load
            wait = WebDriverWait(self.driver, 30)
            
            # Try to find input fields in main document first
            input_fields = []
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input")))
                input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input")
                visible_inputs = [inp for inp in input_fields if inp.is_displayed() and inp.is_enabled()]
                logger.info(f"Found {len(visible_inputs)} visible input fields in main document", "RuckusScraper", self.execution_id)
            except:
                logger.info("No input fields found in main document", "RuckusScraper", self.execution_id)
                visible_inputs = []
            
            # If no inputs found, try checking iframes
            if len(visible_inputs) < 2:
                logger.info("Checking iframes for login form", "RuckusScraper", self.execution_id)
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                logger.info(f"Found {len(iframes)} iframes", "RuckusScraper", self.execution_id)
                
                for i, iframe in enumerate(iframes):
                    try:
                        self.driver.switch_to.frame(iframe)
                        iframe_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
                        iframe_visible = [inp for inp in iframe_inputs if inp.is_displayed() and inp.is_enabled()]
                        logger.info(f"Iframe {i}: Found {len(iframe_visible)} visible input fields", "RuckusScraper", self.execution_id)
                        
                        if len(iframe_visible) >= 2:
                            visible_inputs = iframe_visible
                            logger.info(f"Using iframe {i} for login", "RuckusScraper", self.execution_id)
                            break
                        else:
                            self.driver.switch_to.default_content()
                    except Exception as e:
                        logger.warning(f"Failed to check iframe {i}: {e}", "RuckusScraper", self.execution_id)
                        self.driver.switch_to.default_content()
            
            # If still no inputs, try waiting longer and different selectors
            if len(visible_inputs) < 2:
                logger.info("Trying alternative input selectors", "RuckusScraper", self.execution_id)
                time.sleep(5)  # Wait a bit more
                
                # Try different input selectors
                selectors = [
                    "input[type='text']",
                    "input[type='password']",
                    "input[placeholder*='user']",
                    "input[placeholder*='name']",
                    "input[placeholder*='pass']",
                    "input",
                    "*[contenteditable='true']"
                ]
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        visible = [el for el in elements if el.is_displayed() and el.is_enabled()]
                        if visible:
                            visible_inputs.extend(visible)
                            logger.info(f"Found {len(visible)} inputs with selector: {selector}", "RuckusScraper", self.execution_id)
                    except:
                        continue
                
                # Remove duplicates
                visible_inputs = list(set(visible_inputs))
            
            logger.info(f"Total visible input fields found: {len(visible_inputs)}", "RuckusScraper", self.execution_id)
            
            if len(visible_inputs) < 2:
                logger.error("Not enough input fields found", "RuckusScraper", self.execution_id)
                return False
            
            # Use first field as username, second as password
            username_field = visible_inputs[0]
            password_field = visible_inputs[1]
            
            # Clear and enter credentials
            try:
                username_field.clear()
                username_field.send_keys(self.username)
                logger.info("Username entered", "RuckusScraper", self.execution_id)
                time.sleep(1)
                
                password_field.clear()
                password_field.send_keys(self.password)
                logger.info("Password entered", "RuckusScraper", self.execution_id)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Failed to enter credentials: {e}", "RuckusScraper", self.execution_id)
                return False
            
            # Find and click login button
            try:
                login_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Login'] | //input[@value='Login'] | //button[@type='submit'] | //button | //input[@type='submit']"))
                )
                login_button.click()
                logger.info("Login button clicked", "RuckusScraper", self.execution_id)
            except:
                # If no button found, press Enter on password field
                try:
                    password_field.send_keys(Keys.RETURN)
                    logger.info("Pressed Enter on password field", "RuckusScraper", self.execution_id)
                except Exception as e:
                    logger.error(f"Failed to submit login: {e}", "RuckusScraper", self.execution_id)
                    return False
            
            # Wait for login response
            time.sleep(10)
            
            # Take screenshot after login
            self._take_debug_screenshot("02_after_login")
            
            # Simple verification - check if URL changed or page content changed
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Success indicators
            success_indicators = [
                current_url != self.target_url,  # URL changed
                'wireless' in page_source,
                'dashboard' in page_source,
                'menu' in page_source,
                'logout' in page_source
            ]
            
            if any(success_indicators):
                logger.success("🎉 Login successful!", "RuckusScraper", self.execution_id)
                return True
            else:
                logger.error("Login failed - no success indicators found", "RuckusScraper", self.execution_id)
                logger.info(f"Current URL: {current_url}", "RuckusScraper", self.execution_id)
                logger.info(f"Success indicators: {success_indicators}", "RuckusScraper", self.execution_id)
                return False
            
        except Exception as e:
            logger.error(f"Login failed: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _fallback_login(self) -> bool:
        """Fallback login method using direct element interaction"""
        try:
            logger.info("Attempting fallback login", "RuckusScraper", self.execution_id)
            
            # Wait for form elements
            wait = WebDriverWait(self.driver, 20)
            
            # Find username field with multiple strategies
            username_field = None
            username_strategies = [
                (By.XPATH, "//input[@placeholder='username']"),
                (By.XPATH, "//input[@placeholder='Username']"),
                (By.XPATH, "//input[contains(@name, 'user')]"),
                (By.XPATH, "//input[@type='text']"),
                (By.CSS_SELECTOR, "input[type='text']")
            ]
            
            for strategy in username_strategies:
                try:
                    username_field = wait.until(EC.presence_of_element_located(strategy))
                    if username_field.is_displayed() and username_field.is_enabled():
                        logger.info(f"Found username field with strategy: {strategy}", "RuckusScraper", self.execution_id)
                        break
                except:
                    continue
            
            if not username_field:
                logger.error("Username field not found", "RuckusScraper", self.execution_id)
                return False
            
            # Find password field
            password_field = None
            password_strategies = [
                (By.XPATH, "//input[@placeholder='password']"),
                (By.XPATH, "//input[@placeholder='Password']"),
                (By.XPATH, "//input[@type='password']"),
                (By.XPATH, "//input[contains(@name, 'pass')]")
            ]
            
            for strategy in password_strategies:
                try:
                    password_field = self.driver.find_element(*strategy)
                    if password_field.is_displayed() and password_field.is_enabled():
                        logger.info(f"Found password field with strategy: {strategy}", "RuckusScraper", self.execution_id)
                        break
                except:
                    continue
            
            if not password_field:
                logger.error("Password field not found", "RuckusScraper", self.execution_id)
                return False
            
            # Clear and fill fields
            username_field.clear()
            username_field.send_keys(self.username)
            time.sleep(TIMING_CONFIG['click_delay'])
            
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(TIMING_CONFIG['click_delay'])
            
            # Find and click login button
            button_strategies = [
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(@class, 'login')]"),
                (By.CSS_SELECTOR, "button")
            ]
            
            login_clicked = False
            for strategy in button_strategies:
                try:
                    login_button = self.driver.find_element(*strategy)
                    if login_button.is_displayed() and login_button.is_enabled():
                        login_button.click()
                        login_clicked = True
                        logger.info(f"Clicked login button with strategy: {strategy}", "RuckusScraper", self.execution_id)
                        break
                except:
                    continue
            
            if not login_clicked:
                # If no button found, press Enter
                password_field.send_keys(Keys.RETURN)
                logger.info("Pressed Enter on password field", "RuckusScraper", self.execution_id)
            
            # Wait for response
            time.sleep(5)
            
            # Verify login
            return self._verify_login_success()
            
        except Exception as e:
            logger.error(f"Fallback login failed: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _verify_login_success(self) -> bool:
        """Verify login success with comprehensive checks"""
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Success indicators based on Ruckus interface
            success_indicators = [
                current_url != self.target_url,  # URL changed
                'wireless' in page_source,
                'dashboard' in page_source,
                'menu' in page_source,
                'logout' in page_source,
                'admin' in page_source,
                'configuration' in page_source,
                'monitoring' in page_source,
                'ruckus' in page_source,
                'smartzone' in page_source
            ]
            
            # Failure indicators
            failure_indicators = [
                'login failed' in page_source,
                'invalid credentials' in page_source,
                'authentication failed' in page_source,
                'username' in page_source and 'password' in page_source and 'login' in page_source
            ]
            
            success_count = sum(success_indicators)
            failure_count = sum(failure_indicators)
            
            logger.info(f"Login verification - Success: {success_count}, Failure: {failure_count}", 
                       "RuckusScraper", self.execution_id)
            
            if success_count >= 2 and failure_count == 0:
                return True
            elif success_count >= 1 and failure_count == 0:
                # Check for specific Ruckus elements
                try:
                    wireless_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Wireless') or contains(text(), 'WLAN') or contains(text(), 'Dashboard')]")
                    return len(wireless_elements) > 0
                except:
                    return False
            else:
                return False
                
        except Exception as e:
            logger.error(f"Login verification error: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _navigate_to_wireless_lans(self) -> bool:
        """Navigate to Wireless LANs section - ENHANCED FOR RUCKUS INTERFACE"""
        try:
            logger.info("🧭 Navigating to Wireless LANs section", "RuckusScraper", self.execution_id)
            
            # Wait for page to stabilize after login
            time.sleep(TIMING_CONFIG['navigation_wait'])
            self._take_debug_screenshot("03_before_wireless_nav")
            
            # ENHANCED: Multiple navigation strategies for Ruckus interface
            navigation_successful = False
            
            # Strategy 1: Try direct menu selectors from screenshots
            logger.info("🔍 Strategy 1: Direct menu navigation", "RuckusScraper", self.execution_id)
            
            enhanced_selectors = [
                # Based on actual Ruckus interface structure
                "//div[contains(@class, 'x-tree-node-text') and normalize-space(text())='Wireless LANs']",
                "//span[contains(@class, 'x-tree-node-text') and normalize-space(text())='Wireless LANs']",
                "//a[normalize-space(text())='Wireless LANs']",
                "//span[normalize-space(text())='Wireless LANs']",
                "//*[contains(@class, 'menu') and contains(text(), 'Wireless LANs')]",
                "//*[contains(@class, 'nav') and contains(text(), 'Wireless LANs')]",
                "//div[contains(text(), 'Wireless LANs')]",
                "//*[normalize-space(text())='Wireless LANs']"
            ]
            
            for selector in enhanced_selectors:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # Scroll element into view and highlight
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView(true);
                        arguments[0].style.border = '3px solid red';
                        arguments[0].style.backgroundColor = 'yellow';
                    """, element)
                    time.sleep(2)  # Allow visual confirmation
                    
                    # Click element
                    element.click()
                    logger.success(f"✅ Clicked Wireless LANs menu: {selector}", "RuckusScraper", self.execution_id)
                    
                    # Wait for navigation and verify
                    time.sleep(TIMING_CONFIG['navigation_wait'])
                    
                    if self._verify_wireless_lans_page():
                        navigation_successful = True
                        break
                    
                except Exception as e:
                    logger.debug(f"Menu selector failed: {selector} - {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # Strategy 2: JavaScript-based navigation if direct selectors fail
            if not navigation_successful:
                logger.info("🔍 Strategy 2: JavaScript navigation", "RuckusScraper", self.execution_id)
                
                js_navigation = """
                console.log('🚀 Starting JavaScript navigation to Wireless LANs');
                
                // Search for elements containing 'Wireless' and 'LAN'
                var allElements = document.querySelectorAll('*');
                var candidates = [];
                
                for (var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = (el.textContent || el.innerText || '').trim();
                    
                    if (text.toLowerCase().includes('wireless') && 
                        text.toLowerCase().includes('lan')) {
                        candidates.push({
                            element: el,
                            text: text,
                            tagName: el.tagName,
                            className: el.className,
                            clickable: el.onclick || el.href || el.tagName === 'A' || el.tagName === 'BUTTON'
                        });
                    }
                }
                
                console.log('Found candidates:', candidates.length);
                
                // Sort by clickability and text match
                candidates.sort(function(a, b) {
                    var aScore = 0;
                    var bScore = 0;
                    
                    if (a.clickable) aScore += 10;
                    if (b.clickable) bScore += 10;
                    
                    if (a.text.toLowerCase() === 'wireless lans') aScore += 20;
                    if (b.text.toLowerCase() === 'wireless lans') bScore += 20;
                    
                    return bScore - aScore;
                });
                
                // Try to click the best candidate
                for (var i = 0; i < candidates.length; i++) {
                    var candidate = candidates[i];
                    try {
                        console.log('Trying to click:', candidate.text);
                        candidate.element.style.border = '3px solid blue';
                        candidate.element.click();
                        console.log('✅ Clicked successfully');
                        return true;
                    } catch (e) {
                        console.log('❌ Click failed:', e);
                    }
                }
                
                return false;
                """
                
                result = self.driver.execute_script(js_navigation)
                if result:
                    time.sleep(TIMING_CONFIG['navigation_wait'])
                    if self._verify_wireless_lans_page():
                        navigation_successful = True
                        logger.success("✅ JavaScript navigation successful", "RuckusScraper", self.execution_id)
            
            # Strategy 3: Fallback using menu index (4th menu item as mentioned)
            if not navigation_successful:
                logger.info("🔍 Strategy 3: Menu index navigation (4th item)", "RuckusScraper", self.execution_id)
                
                try:
                    # Find menu items and click the 4th one
                    menu_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'x-tree-node-text')] | //span[contains(@class, 'menu')] | //a[contains(@class, 'menu')]")
                    
                    if len(menu_items) >= 4:
                        fourth_item = menu_items[3]  # 0-indexed, so 3 is the 4th item
                        
                        self.driver.execute_script("""
                            arguments[0].scrollIntoView(true);
                            arguments[0].style.border = '3px solid green';
                        """, fourth_item)
                        time.sleep(2)
                        
                        fourth_item.click()
                        time.sleep(TIMING_CONFIG['navigation_wait'])
                        
                        if self._verify_wireless_lans_page():
                            navigation_successful = True
                            logger.success("✅ Menu index navigation successful", "RuckusScraper", self.execution_id)
                
                except Exception as e:
                    logger.debug(f"Menu index navigation failed: {e}", "RuckusScraper", self.execution_id)
            
            # Final verification
            if navigation_successful:
                self._take_debug_screenshot("04_after_wireless_nav")
                logger.success("🎉 Successfully navigated to Wireless LANs!", "RuckusScraper", self.execution_id)
                return True
            else:
                logger.error("❌ All navigation strategies failed", "RuckusScraper", self.execution_id)
                self._take_debug_screenshot("04_navigation_failed")
                return False
                
        except Exception as e:
            logger.error(f"Navigation to Wireless LANs failed: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _verify_wireless_lans_page(self) -> bool:
        """Verify we're on the Wireless LANs page"""
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for Wireless LANs page indicators
            indicators = [
                'wireless' in current_url.lower(),
                'wlan' in page_source,
                'wireless lans' in page_source,
                'ssid' in page_source,
                'clients' in page_source,
                'ehc' in page_source,  # Our specific networks
                'reception hall' in page_source
            ]
            
            success_count = sum(indicators)
            logger.info(f"Wireless LANs page verification: {success_count}/7 indicators", "RuckusScraper", self.execution_id)
            
            return success_count >= 2
            
        except Exception as e:
            logger.error(f"Page verification failed: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _set_list_view_mode(self) -> bool:
        """Set view mode to List for distraction-free interface - ENHANCED"""
        try:
            logger.info("🎨 Setting view mode to List", "RuckusScraper", self.execution_id)
            
            # Enhanced selectors for List view based on screenshots
            list_view_selectors = [
                "//span[normalize-space(text())='List' and contains(@class, 'x-btn-inner')]",
                "//button[contains(@class, 'x-btn') and .//span[text()='List']]",
                "//*[contains(@class, 'x-toolbar')]//span[text()='List']",
                "//div[contains(@class, 'x-toolbar')]//span[text()='List']",
                "//*[contains(@class, 'view-mode') and contains(text(), 'List')]",
                "//span[text()='List']",
                "//*[contains(text(), 'List') and contains(@class, 'btn')]"
            ]
            
            for selector in list_view_selectors:
                try:
                    wait = WebDriverWait(self.driver, 10)
                    list_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # Check if already selected
                    classes = list_button.get_attribute('class') or ''
                    if 'active' in classes or 'selected' in classes or 'pressed' in classes:
                        logger.info("✅ List view already selected", "RuckusScraper", self.execution_id)
                        return True
                    
                    # Highlight and click
                    self.driver.execute_script("""
                        arguments[0].style.border = '3px solid orange';
                        arguments[0].style.backgroundColor = 'lightblue';
                    """, list_button)
                    time.sleep(1)
                    
                    list_button.click()
                    time.sleep(TIMING_CONFIG['click_delay'])
                    
                    logger.success("✅ Set view mode to List", "RuckusScraper", self.execution_id)
                    self._take_debug_screenshot("05_list_view_set")
                    return True
                    
                except Exception as e:
                    logger.debug(f"List view selector failed: {selector} - {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # JavaScript fallback for List view
            logger.info("🔍 Trying JavaScript approach for List view", "RuckusScraper", self.execution_id)
            
            js_list_view = """
            var buttons = document.querySelectorAll('button, span, div');
            for (var i = 0; i < buttons.length; i++) {
                var btn = buttons[i];
                var text = btn.textContent || btn.innerText || '';
                if (text.trim().toLowerCase() === 'list') {
                    console.log('Found List button:', btn);
                    btn.style.border = '3px solid purple';
                    btn.click();
                    return true;
                }
            }
            return false;
            """
            
            result = self.driver.execute_script(js_list_view)
            if result:
                time.sleep(TIMING_CONFIG['click_delay'])
                logger.success("✅ JavaScript List view selection successful", "RuckusScraper", self.execution_id)
                return True
            
            logger.warning("⚠️ Could not find List view mode selector, continuing anyway", "RuckusScraper", self.execution_id)
            return True  # Continue even if we can't set list view
            
        except Exception as e:
            logger.warning(f"Set list view mode failed: {e}", "RuckusScraper", self.execution_id)
            return True  # Continue even if we can't set list view
    
    def _click_network_row(self, network_config: Dict) -> bool:
        """Click network row in table - ENHANCED FOR RUCKUS INTERFACE WITH EXACT SELECTORS"""
        try:
            network_name = network_config['text']
            logger.info(f"🎯 Clicking network row: {network_name}", "RuckusScraper", self.execution_id)
            
            # Take screenshot before clicking
            self._take_debug_screenshot(f"06_before_click_{network_name.replace(' ', '_')}")
            
            # Strategy 1: EXACT selectors based on user HTML examples
            exact_selectors = [
                f"//div[contains(@class, 'x-grid-cell-inner') and contains(., '{network_name}')]",
                f"//span[contains(@class, 'rks-clickable-column') and normalize-space(text())='{network_name}']",
                f"//div[@class='x-grid-cell-inner' and contains(., '{network_name}')]",
                f"//span[@class=' rks-clickable-column' and text()='{network_name}']"
            ]
            
            # Strategy 2: Enhanced table row selectors
            enhanced_row_selectors = [
                f"//table//tr[.//td[normalize-space(text())='{network_name}']]",
                f"//tr[contains(@class, 'x-grid-row') and .//text()[normalize-space()='{network_name}']]",
                f"//div[contains(@class, 'x-grid')]//tr[.//text()[contains(., '{network_name}')]]",
                f"//tbody//tr[.//td[normalize-space(text())='{network_name}']]",
                f"//tr[.//td[normalize-space(text())='{network_name}']]",
                f"//tr[contains(., '{network_name}')]"
            ]
            
            # Try exact selectors first (based on user HTML examples)
            for selector in exact_selectors:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # Scroll into view and highlight
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView(true);
                        arguments[0].style.border = '3px solid red';
                        arguments[0].style.backgroundColor = 'lightyellow';
                    """, element)
                    time.sleep(2)  # Visual confirmation
                    
                    # Click the element
                    element.click()
                    time.sleep(TIMING_CONFIG['network_selection_wait'])
                    
                    logger.success(f"✅ Clicked network element: {network_name}", "RuckusScraper", self.execution_id)
                    self._take_debug_screenshot(f"07_after_click_{network_name.replace(' ', '_')}")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Exact selector failed: {selector} - {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # Fallback to enhanced row selectors
            for selector in enhanced_row_selectors:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    row_element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # Scroll into view and highlight
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView(true);
                        arguments[0].style.border = '3px solid red';
                        arguments[0].style.backgroundColor = 'lightyellow';
                    """, row_element)
                    time.sleep(2)  # Visual confirmation
                    
                    # Click the row
                    row_element.click()
                    time.sleep(TIMING_CONFIG['network_selection_wait'])
                    
                    logger.success(f"✅ Clicked network row: {network_name}", "RuckusScraper", self.execution_id)
                    self._take_debug_screenshot(f"07_after_click_{network_name.replace(' ', '_')}")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Row selector failed: {selector} - {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # Strategy 2: Find by text content and click parent row
            logger.info(f"🔍 Strategy 2: Text-based search for {network_name}", "RuckusScraper", self.execution_id)
            
            # Find all table cells containing the network name
            cells = self.driver.find_elements(By.XPATH, f"//td[normalize-space(text())='{network_name}']")
            
            for cell in cells:
                try:
                    if cell.is_displayed() and cell.is_enabled():
                        # Get the parent row
                        row = cell.find_element(By.XPATH, "./ancestor::tr[1]")
                        
                        # Highlight and click
                        self.driver.execute_script("""
                            arguments[0].scrollIntoView(true);
                            arguments[0].style.border = '3px solid green';
                            arguments[0].style.backgroundColor = 'lightgreen';
                        """, row)
                        time.sleep(2)
                        
                        row.click()
                        time.sleep(TIMING_CONFIG['network_selection_wait'])
                        
                        logger.success(f"✅ Clicked network via text search: {network_name}", "RuckusScraper", self.execution_id)
                        return True
                        
                except Exception as e:
                    logger.debug(f"Text-based click failed: {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # Strategy 3: JavaScript-based clicking
            logger.info(f"🔍 Strategy 3: JavaScript click for {network_name}", "RuckusScraper", self.execution_id)
            
            js_click = f"""
            console.log('🚀 JavaScript search for network: {network_name}');
            
            // Find all table rows
            var rows = document.querySelectorAll('tr');
            console.log('Found rows:', rows.length);
            
            for (var i = 0; i < rows.length; i++) {{
                var row = rows[i];
                var text = row.textContent || row.innerText || '';
                
                if (text.includes('{network_name}')) {{
                    console.log('Found matching row:', text);
                    row.style.border = '3px solid blue';
                    row.style.backgroundColor = 'lightblue';
                    
                    // Try clicking the row
                    try {{
                        row.click();
                        console.log('✅ Row clicked successfully');
                        return true;
                    }} catch (e) {{
                        console.log('❌ Row click failed, trying cells');
                        
                        // Try clicking individual cells
                        var cells = row.querySelectorAll('td');
                        for (var j = 0; j < cells.length; j++) {{
                            try {{
                                cells[j].click();
                                console.log('✅ Cell clicked successfully');
                                return true;
                            }} catch (e2) {{
                                console.log('Cell click failed');
                            }}
                        }}
                    }}
                }}
            }}
            
            console.log('❌ No matching row found');
            return false;
            """
            
            result = self.driver.execute_script(js_click)
            if result:
                time.sleep(TIMING_CONFIG['network_selection_wait'])
                logger.success(f"✅ JavaScript click successful for {network_name}", "RuckusScraper", self.execution_id)
                return True
            
            logger.error(f"❌ All strategies failed for network: {network_name}", "RuckusScraper", self.execution_id)
            return False
            
        except Exception as e:
            logger.error(f"Error clicking network row: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _extract_network_data(self, network_config: Dict) -> List[str]:
        """Extract data for a specific network based on user screenshots"""
        try:
            network_name = network_config['name']
            logger.info(f"🎯 Extracting data for network: {network_name}", "RuckusScraper", self.execution_id)
            
            # Navigate to correct page if needed
            if network_config['page'] == 2:
                if not self._navigate_to_page_2():
                    logger.error(f"Failed to navigate to page 2 for {network_name}", "RuckusScraper", self.execution_id)
                    return []
            
            # Find and click network using table row approach
            network_clicked = self._click_network_row(network_config)
            if not network_clicked:
                logger.error(f"Failed to click network: {network_name}", "RuckusScraper", self.execution_id)
                return []
            
            # Click Clients tab if required
            if network_config['clients_tab_required']:
                if not self._click_clients_tab():
                    logger.warning(f"Failed to click Clients tab for {network_name}", "RuckusScraper", self.execution_id)
                    # Continue anyway, might still be able to download
            
            # Wait for content to load
            time.sleep(TIMING_CONFIG['tab_switch_wait'])
            
            # Download CSV
            downloaded_files = self._download_csv(network_name)
            
            if downloaded_files:
                logger.success(f"✅ Downloaded {len(downloaded_files)} files for {network_name}", "RuckusScraper", self.execution_id)
                return downloaded_files
            else:
                logger.error(f"❌ No files downloaded for {network_name}", "RuckusScraper", self.execution_id)
                return []
                
        except Exception as e:
            logger.error(f"Network data extraction failed for {network_config['name']}: {e}", "RuckusScraper", self.execution_id)
            return []
    
    def _navigate_to_page_2(self) -> bool:
        """Navigate to page 2 - ENHANCED WITH EXACT SELECTORS"""
        try:
            logger.info("Navigating to page 2", "RuckusScraper", self.execution_id)
            self._take_debug_screenshot("08_before_page_2")
            
            # EXACT selectors based on user HTML examples
            exact_page_2_selectors = [
                "//span[@id='button-2436-btnInnerEl' and contains(@class, 'x-btn-inner') and normalize-space(text())='2']",
                "//span[contains(@class, 'x-btn-inner') and normalize-space(text())='2']",
                "//span[@data-ref='btnInnerEl' and contains(@class, 'x-btn-inner') and text()='2']"
            ]
            
            # Try exact selectors first
            for selector in exact_page_2_selectors:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    page_2_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # Highlight and click
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView(true);
                        arguments[0].style.border = '3px solid orange';
                        arguments[0].style.backgroundColor = 'lightorange';
                    """, page_2_button)
                    time.sleep(2)  # Visual confirmation
                    
                    page_2_button.click()
                    time.sleep(TIMING_CONFIG['navigation_wait'])  # Wait for page load
                    
                    logger.success("✅ Successfully navigated to page 2 (exact selector)", "RuckusScraper", self.execution_id)
                    self._take_debug_screenshot("09_after_page_2")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Exact page 2 selector {selector} failed: {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # Fallback to original selectors
            for selector in WIFI_CONFIG['page_2_selectors']:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    page_2_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", page_2_button)
                    time.sleep(1)
                    page_2_button.click()
                    
                    time.sleep(TIMING_CONFIG['navigation_wait'])  # Wait for page load
                    
                    logger.success("✅ Successfully navigated to page 2 (fallback)", "RuckusScraper", self.execution_id)
                    self._take_debug_screenshot("09_after_page_2")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Page 2 selector {selector} failed: {e}", "RuckusScraper", self.execution_id)
                    continue
            
            logger.error("❌ Failed to navigate to page 2", "RuckusScraper", self.execution_id)
            return False
            
        except Exception as e:
            logger.error(f"Page 2 navigation failed: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _click_clients_tab(self) -> bool:
        """Click Clients tab - ENHANCED WITH EXACT SELECTORS"""
        try:
            logger.info("Clicking Clients tab", "RuckusScraper", self.execution_id)
            
            # Take screenshot before clicking
            self._take_debug_screenshot("08_before_clients_tab")
            
            # EXACT selectors based on user HTML examples
            exact_clients_selectors = [
                "//span[@id='tab-3060-btnInnerEl' and contains(@class, 'x-tab-inner') and normalize-space(text())='Clients']",
                "//span[contains(@class, 'x-tab-inner') and normalize-space(text())='Clients']",
                "//span[@data-ref='btnInnerEl' and contains(@class, 'x-tab-inner') and text()='Clients']"
            ]
            
            # Try exact selectors first
            for selector in exact_clients_selectors:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    clients_tab = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # Highlight and click
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView(true);
                        arguments[0].style.border = '3px solid green';
                        arguments[0].style.backgroundColor = 'lightgreen';
                    """, clients_tab)
                    time.sleep(2)  # Visual confirmation
                    
                    clients_tab.click()
                    time.sleep(TIMING_CONFIG['tab_switch_wait'])  # Wait for tab content to load
                    
                    logger.success("✅ Successfully clicked Clients tab (exact selector)", "RuckusScraper", self.execution_id)
                    self._take_debug_screenshot("09_after_clients_tab")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Exact clients tab selector {selector} failed: {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # Fallback to original selectors
            for selector in WIFI_CONFIG['clients_tab_selectors']:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    clients_tab = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", clients_tab)
                    time.sleep(1)
                    clients_tab.click()
                    
                    time.sleep(TIMING_CONFIG['tab_switch_wait'])  # Wait for tab content to load
                    
                    logger.success("✅ Successfully clicked Clients tab (fallback)", "RuckusScraper", self.execution_id)
                    return True
                    
                except Exception as e:
                    logger.debug(f"Clients tab selector {selector} failed: {e}", "RuckusScraper", self.execution_id)
                    continue
            
            logger.warning("⚠️ Failed to find/click Clients tab", "RuckusScraper", self.execution_id)
            return False
            
        except Exception as e:
            logger.error(f"Clients tab click failed: {e}", "RuckusScraper", self.execution_id)
            return False
    
    def _download_csv(self, network_name: str) -> List[str]:
        """Download CSV files using the download button from screenshots"""
        try:
            logger.info(f"Downloading CSV for {network_name}", "RuckusScraper", self.execution_id)
            
            # Get list of files before download
            files_before = set(self.download_dir.glob("*.csv"))
            
            # Try to find and click download button
            download_clicked = False
            
            # Take screenshot before download attempt
            self._take_debug_screenshot(f"10_before_download_{network_name.replace(' ', '_')}")
            
            # EXACT selectors based on user HTML examples
            exact_download_selectors = [
                "//span[@id='Rks-module-base-Button-3369-btnIconEl' and contains(@class, 'x-btn-icon-el') and contains(@class, 'x-btn-glyph')]",
                "//span[contains(@class, 'x-btn-icon-el') and contains(@class, 'x-btn-glyph') and contains(@style, 'FontAwesome')]",
                "//span[@data-ref='btnIconEl' and contains(@class, 'x-btn-icon-el') and contains(@class, 'x-btn-glyph')]"
            ]
            
            # Try exact selectors first
            for selector in exact_download_selectors:
                try:
                    wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                    download_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # Highlight and click
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView(true);
                        arguments[0].style.border = '3px solid blue';
                        arguments[0].style.backgroundColor = 'lightblue';
                    """, download_button)
                    time.sleep(2)  # Visual confirmation
                    
                    download_button.click()
                    
                    download_clicked = True
                    logger.success(f"✅ Download button clicked (exact selector): {selector}", "RuckusScraper", self.execution_id)
                    break
                    
                except Exception as e:
                    logger.debug(f"Exact download selector {selector} failed: {e}", "RuckusScraper", self.execution_id)
                    continue
            
            # Fallback to original selectors
            if not download_clicked:
                for selector in WIFI_CONFIG['download_button_selectors']:
                    try:
                        wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
                        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
                        time.sleep(1)
                        download_button.click()
                        
                        download_clicked = True
                        logger.success(f"✅ Download button clicked (fallback): {selector}", "RuckusScraper", self.execution_id)
                        break
                        
                    except Exception as e:
                        logger.debug(f"Download selector {selector} failed: {e}", "RuckusScraper", self.execution_id)
                        continue
            
            if not download_clicked:
                # Try JavaScript approach for FontAwesome download icon
                logger.info("Trying JavaScript download approach", "RuckusScraper", self.execution_id)
                
                js_download = """
                // Look for FontAwesome download icons
                var downloadElements = document.querySelectorAll('*');
                for (var i = 0; i < downloadElements.length; i++) {
                    var el = downloadElements[i];
                    var classes = el.className || '';
                    var title = el.title || el.getAttribute('aria-label') || '';
                    var onclick = el.onclick ? el.onclick.toString() : '';
                    
                    // Check for FontAwesome download icon
                    if (classes.includes('fa-download') || 
                        title.toLowerCase().includes('download') || 
                        onclick.toLowerCase().includes('download') ||
                        (el.tagName === 'A' && el.href && el.href.includes('download'))) {
                        
                        console.log('Found download element:', el);
                        el.click();
                        return true;
                    }
                }
                
                // Alternative: Look for export buttons
                var exportButtons = document.querySelectorAll('button, a, span');
                for (var i = 0; i < exportButtons.length; i++) {
                    var el = exportButtons[i];
                    var text = el.textContent || el.innerText || '';
                    if (text.toLowerCase().includes('export') || 
                        text.toLowerCase().includes('download') ||
                        text.toLowerCase().includes('csv')) {
                        console.log('Found export button:', el);
                        el.click();
                        return true;
                    }
                }
                
                return false;
                """
                
                download_clicked = self.driver.execute_script(js_download)
            
            if download_clicked:
                # Wait for download to complete
                logger.info("Waiting for download to complete", "RuckusScraper", self.execution_id)
                
                timeout = TIMING_CONFIG['download_wait']
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    time.sleep(2)
                    files_after = set(self.download_dir.glob("*.csv"))
                    new_files = files_after - files_before
                    
                    if new_files:
                        # Check if files are complete (not .crdownload or .tmp)
                        complete_files = []
                        for file_path in new_files:
                            if not file_path.name.endswith(('.crdownload', '.tmp', '.part')):
                                # Rename file with network name and timestamp
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                new_name = f"{network_name.replace(' ', '_')}_{timestamp}.csv"
                                new_path = file_path.parent / new_name
                                
                                try:
                                    file_path.rename(new_path)
                                    complete_files.append(str(new_path))
                                    logger.info(f"Renamed file: {file_path.name} → {new_name}", "RuckusScraper", self.execution_id)
                                except:
                                    complete_files.append(str(file_path))
                        
                        if complete_files:
                            logger.success(f"✅ Download completed: {complete_files}", "RuckusScraper", self.execution_id)
                            self._take_debug_screenshot(f"11_after_download_{network_name.replace(' ', '_')}")
                            return complete_files
                
                logger.warning("⚠️ Download timeout reached", "RuckusScraper", self.execution_id)
                
                # Return any partial downloads
                files_after = set(self.download_dir.glob("*.csv"))
                new_files = files_after - files_before
                return [str(f) for f in new_files]
            
            else:
                logger.error("❌ No download button found", "RuckusScraper", self.execution_id)
                return []
                
        except Exception as e:
            logger.error(f"CSV download failed: {e}", "RuckusScraper", self.execution_id)
            return []
    
    def execute_complete_extraction(self, slot_name: str = None) -> Dict:
        """Execute complete data extraction workflow - BULLETPROOF VERSION"""
        try:
            self.current_slot = slot_name or f"slot_{int(time.time())}"
            logger.info(f"🚀 Starting BULLETPROOF extraction for slot: {self.current_slot}", "RuckusScraper", self.execution_id)
            
            # Step 1: Check network connectivity
            if not self._check_network_connectivity():
                return {"success": False, "error": "Network connectivity failed"}
            
            # Step 2: Setup Chrome driver
            self.driver = self._setup_bulletproof_chrome()
            
            try:
                # Step 3: Bulletproof login
                if not self._bulletproof_login():
                    return {"success": False, "error": "Login failed"}
                
                # Step 4: Navigate to Wireless LANs
                if not self._navigate_to_wireless_lans():
                    return {"success": False, "error": "Failed to navigate to Wireless LANs"}
                
                # Step 5: Set List view mode
                self._set_list_view_mode()
                
                # Step 6: Extract data for each network
                extraction_results = {}
                
                for network_config in WIFI_CONFIG['networks_to_extract']:
                    network_name = network_config['name']
                    logger.info(f"🎯 Processing network: {network_name}", "RuckusScraper", self.execution_id)
                    
                    try:
                        downloaded_files = self._extract_network_data(network_config)
                        extraction_results[network_name] = {
                            'success': len(downloaded_files) > 0,
                            'files': downloaded_files,
                            'file_count': len(downloaded_files)
                        }
                        
                        # Add to global extracted files list
                        self.extracted_files.extend(downloaded_files)
                        
                    except Exception as e:
                        logger.error(f"Failed to extract data for {network_name}: {e}", "RuckusScraper", self.execution_id)
                        extraction_results[network_name] = {
                            'success': False,
                            'error': str(e),
                            'files': [],
                            'file_count': 0
                        }
                
                # Compile results
                total_files = sum(result['file_count'] for result in extraction_results.values())
                successful_extractions = sum(1 for result in extraction_results.values() if result['success'])
                
                result = {
                    'success': successful_extractions > 0,
                    'execution_id': self.execution_id,
                    'slot_name': self.current_slot,
                    'timestamp': datetime.now().isoformat(),
                    'total_files_downloaded': total_files,
                    'successful_networks': successful_extractions,
                    'total_networks': len(WIFI_CONFIG['networks_to_extract']),
                    'extraction_results': extraction_results,
                    'downloaded_files': self.extracted_files,
                    'debug_screenshots': self.debug_screenshots
                }
                
                logger.success(f"🎉 BULLETPROOF extraction completed - {successful_extractions}/{len(WIFI_CONFIG['networks_to_extract'])} networks successful, {total_files} files downloaded", 
                              "RuckusScraper", self.execution_id)
                
                return result
                
            finally:
                # Always cleanup driver
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
        except Exception as e:
            logger.error(f"Complete extraction failed: {e}", "RuckusScraper", self.execution_id)
            return {
                'success': False,
                'error': str(e),
                'execution_id': self.execution_id,
                'slot_name': self.current_slot,
                'timestamp': datetime.now().isoformat()
            }
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


# Convenience function for external use
def execute_bulletproof_scraping(slot_name: str = None) -> Dict:
    """Execute bulletproof scraping with automatic cleanup"""
    scraper = BulletproofRuckusWiFiScraper()
    try:
        return scraper.execute_complete_extraction(slot_name)
    finally:
        del scraper 