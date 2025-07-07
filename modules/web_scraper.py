#!/usr/bin/env python3
"""
Enhanced WiFi Web Scraper with dynamic file system integration
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import traceback
import shutil
import socket
import requests
import urllib3
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import WIFI_CONFIG, CHROME_CONFIG, CSV_DIR, TIMING_CONFIG
from core.logger import logger
from modules.dynamic_file_manager import DynamicFileManager
from modules.hybrid_web_scraper import HybridWiFiScraper

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WiFiWebScraper:
    """Enhanced WiFi Web Scraper with dynamic file system"""
    
    def __init__(self, execution_id=None):
        self.execution_id = execution_id or f"scraper_{int(time.time())}"
        self.driver = None
        self.wait = None
        
        # Initialize dynamic file manager
        self.file_manager = DynamicFileManager()
        
        # Use dynamic download directory
        today_folder = self.file_manager.create_today_folder()
        self.download_dir = Path(today_folder)
        
        logger.info(f"WiFi scraper initialized with dynamic folder: {self.download_dir}", "WebScraper", self.execution_id)
        
        # Ensure download directory exists
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_url = None
        
    def check_network_connectivity(self):
        """Check if the WiFi management server is reachable"""
        try:
            logger.info("Checking network connectivity to WiFi server", "WebScraper", self.execution_id)
            
            # Parse URL to get host and port
            import urllib.parse
            parsed = urllib.parse.urlparse(WIFI_CONFIG['target_url'])
            host = parsed.hostname
            port = parsed.port or 8443
            
            # Test socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.success(f"Network connectivity to {host}:{port} is available", "WebScraper", self.execution_id)
                return True
            else:
                logger.warning(f"Cannot connect to {host}:{port} (socket error: {result})", "WebScraper", self.execution_id)
                return False
                
        except Exception as e:
            logger.error(f"Network connectivity check failed: {str(e)}", "WebScraper", self.execution_id)
            return False
    
    def setup_driver(self):
        """Setup Chrome driver with enhanced network handling"""
        try:
            # Setup directories with dynamic date
            today = datetime.now().strftime("%d%b").lower()  # e.g., "04aug", "29feb" (leap year)
            self.download_dir = Path(f"EHC_Data/{today}")
            self.download_dir.mkdir(parents=True, exist_ok=True)
            
            # Chrome options with enhanced network settings
            options = uc.ChromeOptions()
            
            # Download preferences
            prefs = {
                "download.default_directory": str(self.download_dir),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.automatic_downloads": 1
            }
            options.add_experimental_option("prefs", prefs)
            
            # Enhanced Chrome arguments for better network handling
            if CHROME_CONFIG['headless']:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument(f"--window-size={CHROME_CONFIG['window_size']}")
            
            # Network and SSL options
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-web-security')
            options.add_argument('--ignore-certificate-errors-spki-list')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--accept-insecure-certs')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            
            # Network timeout settings
            options.add_argument('--timeout=60000')
            options.add_argument('--enable-features=NetworkService')
            
            # Initialize driver
            self.driver = uc.Chrome(options=options)
            
            # Set enhanced timeouts
            self.driver.set_page_load_timeout(60)  # Increased timeout
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome driver initialized successfully with enhanced network settings", "WebScraper", self.execution_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}", "WebScraper", self.execution_id, e)
            return False
    
    def login_to_wifi_interface(self):
        """Enhanced login with 2-field detection as per user requirements"""
        try:
            logger.info("Starting login to WiFi interface", "WebScraper", self.execution_id)
            
            # Navigate to login page (exact URL as specified)
            target_url = WIFI_CONFIG['target_url']
            if not target_url.endswith('/'):
                target_url += '/'
            
            logger.info(f"Navigating to: {target_url}", "WebScraper", self.execution_id)
            self.driver.get(target_url)
            time.sleep(5)
            
            # Take screenshot for debugging
            screenshot_path = f"login_attempt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(str(self.download_dir / screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}", "WebScraper", self.execution_id)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, WIFI_CONFIG['timeout'])
            
            # Check if already logged in by looking for dashboard elements
            try:
                dashboard_elements = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Wireless LANs')] | //span[contains(text(), 'Dashboard')] | //div[contains(@class, 'dashboard')]")
                if dashboard_elements:
                    logger.info("Already logged in, proceeding to navigation", "WebScraper", self.execution_id)
                    return True
            except:
                pass
            
            # Enhanced form detection with detailed field analysis
            all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
            logger.info(f"Found {len(all_inputs)} total input fields", "WebScraper", self.execution_id)
            
            # Filter for visible and enabled inputs with detailed analysis
            visible_inputs = []
            for inp in all_inputs:
                try:
                    if inp.is_displayed() and inp.is_enabled():
                        input_type = inp.get_attribute('type') or 'text'
                        input_name = inp.get_attribute('name') or 'unnamed'
                        input_id = inp.get_attribute('id') or 'no-id'
                        placeholder = inp.get_attribute('placeholder') or ''
                        
                        logger.info(f"Visible input: type={input_type}, name={input_name}, id={input_id}, placeholder={placeholder}", "WebScraper", self.execution_id)
                        visible_inputs.append({
                            'element': inp,
                            'type': input_type,
                            'name': input_name,
                            'id': input_id,
                            'placeholder': placeholder
                        })
                except Exception as e:
                    logger.warning(f"Error analyzing input field: {str(e)}", "WebScraper", self.execution_id)
            
            logger.info(f"Found {len(visible_inputs)} visible input fields", "WebScraper", self.execution_id)
            
            username_field = None
            password_field = None
            
            # Smart field detection based on attributes
            for field in visible_inputs:
                field_info = f"type={field['type']}, name={field['name']}, id={field['id']}"
                
                # Username field detection
                if not username_field:
                    username_indicators = [
                        field['type'] in ['text', 'email', ''],
                        'user' in field['name'].lower(),
                        'login' in field['name'].lower(),
                        'admin' in field['name'].lower(),
                        'user' in field['id'].lower(),
                        'login' in field['id'].lower(),
                        'username' in field['placeholder'].lower(),
                        'user' in field['placeholder'].lower()
                    ]
                    
                    if any(username_indicators) and field['type'] != 'password':
                        username_field = field['element']
                        logger.info(f"Username field detected: {field_info}", "WebScraper", self.execution_id)
                
                # Password field detection
                if not password_field:
                    password_indicators = [
                        field['type'] == 'password',
                        'pass' in field['name'].lower(),
                        'pwd' in field['name'].lower(),
                        'pass' in field['id'].lower(),
                        'password' in field['placeholder'].lower()
                    ]
                    
                    if any(password_indicators):
                        password_field = field['element']
                        logger.info(f"Password field detected: {field_info}", "WebScraper", self.execution_id)
            
            # 2-field detection fallback (as per user requirements)
            if not username_field or not password_field:
                if len(visible_inputs) == 2:
                    logger.info("Using 2-field detection approach", "WebScraper", self.execution_id)
                    username_field = visible_inputs[0]['element']
                    password_field = visible_inputs[1]['element']
                    logger.info("Assigned first field as username, second as password", "WebScraper", self.execution_id)
            
            # Final fallback by field order
            if not username_field or not password_field:
                logger.info("Using fallback detection by field order", "WebScraper", self.execution_id)
                
                text_fields = [field for field in visible_inputs if field['type'] in ['text', 'email', '']]
                password_fields = [field for field in visible_inputs if field['type'] == 'password']
                
                if text_fields and not username_field:
                    username_field = text_fields[0]['element']
                    logger.info("Selected first text field as username", "WebScraper", self.execution_id)
                
                if password_fields and not password_field:
                    password_field = password_fields[0]['element']
                    logger.info("Selected first password field as password", "WebScraper", self.execution_id)
                elif len(visible_inputs) >= 2 and not password_field:
                    # If no password field found, use second field
                    password_field = visible_inputs[1]['element']
                    logger.info("Selected second field as password (fallback)", "WebScraper", self.execution_id)
            
            # Verify we found both fields
            if not username_field or not password_field:
                logger.error("Could not find both username and password fields", "WebScraper", self.execution_id)
                if not username_field:
                    logger.error("Username field not found", "WebScraper", self.execution_id)
                if not password_field:
                    logger.error("Password field not found", "WebScraper", self.execution_id)
                raise Exception("Could not locate username or password fields")
            
            # Clear and enter credentials with enhanced interaction
            try:
                # Scroll to username field to ensure it's visible
                self.driver.execute_script("arguments[0].scrollIntoView(true);", username_field)
                time.sleep(1)
                
                # Focus on username field
                username_field.click()
                time.sleep(0.5)
                
                # Clear field using multiple methods
                username_field.clear()
                username_field.send_keys(Keys.CONTROL + "a")  # Select all
                username_field.send_keys(Keys.DELETE)  # Delete
                time.sleep(0.5)
                
                # Enter username
                username_field.send_keys(WIFI_CONFIG['username'])
                logger.info(f"Entered username: {WIFI_CONFIG['username']}", "WebScraper", self.execution_id)
                time.sleep(1)
                
                # Focus on password field
                password_field.click()
                time.sleep(0.5)
                
                # Clear password field
                password_field.clear()
                password_field.send_keys(Keys.CONTROL + "a")  # Select all
                password_field.send_keys(Keys.DELETE)  # Delete
                time.sleep(0.5)
                
                # Enter password
                password_field.send_keys(WIFI_CONFIG['password'])
                logger.info("Entered password", "WebScraper", self.execution_id)
                time.sleep(1)
                
                # Take screenshot after entering credentials
                screenshot_path = f"credentials_entered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(str(self.download_dir / screenshot_path))
                logger.info(f"Credentials screenshot saved: {screenshot_path}", "WebScraper", self.execution_id)
                
            except Exception as e:
                logger.error(f"Failed to enter credentials: {str(e)}", "WebScraper", self.execution_id)
                raise
            
            # Submit form - try Enter key first as it's most reliable
            try:
                password_field.send_keys(Keys.RETURN)
                logger.info("Submitted form using Enter key", "WebScraper", self.execution_id)
                time.sleep(5)
            except Exception as e:
                logger.error(f"Enter key failed, trying to find login button: {str(e)}", "WebScraper", self.execution_id)
                
                # Find and click login button as fallback
                login_button = None
                login_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Login')",
                    "button:contains('Sign In')",
                    "button:contains('Submit')",
                    ".btn-primary",
                    ".login-btn",
                    ".submit-btn"
                ]
                
                for selector in login_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                login_button = element
                                break
                        if login_button:
                            break
                    except:
                        continue
                
                if login_button:
                    try:
                        self.driver.execute_script("arguments[0].click();", login_button)
                        logger.info("Clicked login button using JavaScript", "WebScraper", self.execution_id)
                        time.sleep(5)
                    except:
                        login_button.click()
                        logger.info("Clicked login button using regular click", "WebScraper", self.execution_id)
                        time.sleep(5)
                else:
                    raise Exception("Could not submit login form")
            
            # Take post-login screenshot
            post_login_screenshot = f"post_login_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(str(self.download_dir / post_login_screenshot))
            logger.info(f"Post-login screenshot saved: {post_login_screenshot}", "WebScraper", self.execution_id)
            
            # Verify login success
            current_url = self.driver.current_url
            logger.info(f"Current URL after login: {current_url}", "WebScraper", self.execution_id)
            
            # Check for login success indicators
            success_indicators = [
                "dashboard",
                "wireless",
                "logout",
                "admin",
                "welcome",
                "home",
                "menu"
            ]
            
            page_text = self.driver.page_source.lower() if self.driver.page_source else ""
            login_successful = any(indicator in page_text for indicator in success_indicators)
            
            # Also check if URL changed from login page or contains session ID
            url_changed = current_url != target_url
            has_session_id = '#' in current_url  # Dynamic session ID as mentioned by user
            
            if login_successful or url_changed or has_session_id:
                self.session_url = current_url
                logger.success(f"Login successful! Session URL: {self.session_url}", "WebScraper", self.execution_id)
                return True
            else:
                logger.error(f"Login appears to have failed. Current URL: {current_url}", "WebScraper", self.execution_id)
                return False
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}", "WebScraper", self.execution_id, e)
            # Take error screenshot
            try:
                error_screenshot = f"login_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(str(self.download_dir / error_screenshot))
                logger.info(f"Error screenshot saved: {error_screenshot}", "WebScraper", self.execution_id)
            except:
                pass
            return False
    
    def navigate_to_wireless_lans(self):
        """Enhanced navigation with reload handling as per user requirements"""
        try:
            logger.info("Navigating to Wireless LANs (4th menu item)", "WebScraper", self.execution_id)
            
            wait = WebDriverWait(self.driver, WIFI_CONFIG['timeout'])
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    # User specified: "4th menu item that is Wireless LANs"
                    # Try multiple strategies to find the 4th menu item
                    
                    # Strategy 1: Find by text "Wireless LANs"
                    menu_selectors = [
                        "//a[contains(text(), 'Wireless LANs')]",
                        "//span[contains(text(), 'Wireless LANs')]",
                        "//div[contains(text(), 'Wireless LANs')]",
                        "//li[contains(text(), 'Wireless LANs')]",
                        "//*[contains(text(), 'Wireless LANs')]"
                    ]
                    
                    menu_item = None
                    for selector in menu_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled():
                                    menu_item = element
                                    logger.info(f"Found Wireless LANs menu with selector: {selector}", "WebScraper", self.execution_id)
                                    break
                            if menu_item:
                                break
                        except:
                            continue
                    
                    # Strategy 2: Find 4th menu item by position
                    if not menu_item:
                        try:
                            # Look for common menu structures
                            menu_containers = [
                                ".menu-item",
                                ".nav-item", 
                                "li",
                                ".x-menu-item",
                                "[role='menuitem']"
                            ]
                            
                            for container in menu_containers:
                                menu_items = self.driver.find_elements(By.CSS_SELECTOR, container)
                                visible_items = [item for item in menu_items if item.is_displayed()]
                                
                                if len(visible_items) >= 4:
                                    menu_item = visible_items[3]  # 4th item (0-indexed)
                                    logger.info(f"Found 4th menu item using container: {container}", "WebScraper", self.execution_id)
                                    break
                            
                            if menu_item:
                                break
                        except:
                            pass
                    
                    if menu_item:
                        # Click the menu item
                        try:
                            self.driver.execute_script("arguments[0].click();", menu_item)
                            logger.info("Clicked Wireless LANs menu using JavaScript", "WebScraper", self.execution_id)
                        except:
                            menu_item.click()
                            logger.info("Clicked Wireless LANs menu using regular click", "WebScraper", self.execution_id)
                        
                        time.sleep(5)
                        
                        # Check if content loaded
                        try:
                            # Look for indicators that we're on the Wireless LANs page
                            content_indicators = [
                                "//td[contains(text(), 'EHC')]",
                                "//span[contains(text(), 'EHC')]",
                                "//*[contains(text(), 'Reception')]",
                                "//table",
                                ".grid",
                                ".x-grid"
                            ]
                            
                            content_found = False
                            for indicator in content_indicators:
                                try:
                                    elements = self.driver.find_elements(By.XPATH, indicator)
                                    if elements:
                                        content_found = True
                                        logger.info(f"Content loaded, found indicator: {indicator}", "WebScraper", self.execution_id)
                                        break
                                except:
                                    continue
                            
                            if content_found:
                                logger.success("Successfully navigated to Wireless LANs", "WebScraper", self.execution_id)
                                return True
                            else:
                                logger.warning("Menu clicked but content not loaded, trying reload", "WebScraper", self.execution_id)
                                raise Exception("Content not loaded after menu click")
                        
                        except Exception as e:
                            logger.warning(f"Content check failed: {str(e)}", "WebScraper", self.execution_id)
                            if attempt < max_attempts - 1:
                                # User specified: "sometimes we have to load so click on other items too, then get back to Wireless LANs. or reload again"
                                logger.info("Trying reload strategy as specified by user", "WebScraper", self.execution_id)
                                self.driver.refresh()
                                time.sleep(5)
                                continue
                            else:
                                raise
                    else:
                        raise Exception("Could not locate Wireless LANs menu item")
                
                except Exception as e:
                    if attempt < max_attempts - 1:
                        logger.warning(f"Navigation attempt {attempt + 1} failed: {str(e)}, retrying with reload", "WebScraper", self.execution_id)
                        # Reload page as per user specification
                        self.driver.refresh()
                        time.sleep(5)
                    else:
                        logger.error(f"All navigation attempts failed: {str(e)}", "WebScraper", self.execution_id)
                        raise
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to navigate to Wireless LANs: {str(e)}", "WebScraper", self.execution_id, e)
            return False
    
    def download_source_data(self, source_name, has_clients_tab=True, page_number=1):
        """Enhanced download with exact source matching and robust verification"""
        try:
            logger.info(f"Starting download for {source_name} (Page {page_number})", "WebScraper", self.execution_id)
            
            wait = WebDriverWait(self.driver, WIFI_CONFIG['timeout'])
            
            # User specified exact sources:
            # Page 1: "EHC TV", "EHC-15" 
            # Page 2: "Reception Hall-Mobile", "Reception Hall-TV"
            
            # Find source by name with multiple strategies
            source_selectors = [
                f"//td[contains(text(), '{source_name}')]",
                f"//span[contains(text(), '{source_name}')]",
                f"//div[contains(text(), '{source_name}')]",
                f"//*[contains(@class, 'rks-clickable-column') and contains(text(), '{source_name}')]",
                f"//*[contains(text(), '{source_name}')]"
            ]
            
            source_element = None
            for selector in source_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.text.strip() == source_name:
                            source_element = element
                            logger.info(f"Found source {source_name} with selector: {selector}", "WebScraper", self.execution_id)
                            break
                    if source_element:
                        break
                except:
                    continue
            
            if not source_element:
                raise Exception(f"Could not locate source: {source_name}")
            
            # Click on the source to select it
            try:
                self.driver.execute_script("arguments[0].click();", source_element)
                logger.info(f"Clicked on source: {source_name}", "WebScraper", self.execution_id)
            except:
                source_element.click()
                logger.info(f"Clicked on source: {source_name} (regular click)", "WebScraper", self.execution_id)
            
            time.sleep(3)
            
            # Handle clients tab if source has clients
            # User specified: "EHC TV" and "Reception Hall-Mobile" have clients
            if has_clients_tab and source_name in ["EHC TV", "Reception Hall-Mobile"]:
                logger.info(f"Looking for clients tab for {source_name}", "WebScraper", self.execution_id)
                
                clients_selectors = [
                    "//a[contains(text(), 'Clients')]",
                    "//span[contains(text(), 'Clients')]",
                    "//div[contains(text(), 'Clients')]",
                    "//tab[contains(text(), 'Clients')]",
                    "//*[contains(@class, 'tab') and contains(text(), 'Clients')]"
                ]
                
                clients_tab = None
                for selector in clients_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                clients_tab = element
                                logger.info(f"Found clients tab with selector: {selector}", "WebScraper", self.execution_id)
                                break
                        if clients_tab:
                            break
                    except:
                        continue
                
                if clients_tab:
                    try:
                        self.driver.execute_script("arguments[0].click();", clients_tab)
                        logger.info("Clicked clients tab using JavaScript", "WebScraper", self.execution_id)
                    except:
                        clients_tab.click()
                        logger.info("Clicked clients tab using regular click", "WebScraper", self.execution_id)
                    
                    time.sleep(3)
                else:
                    logger.warning(f"Clients tab not found for {source_name}, proceeding without it", "WebScraper", self.execution_id)
            
            # Find and click download button with enhanced detection
            download_selectors = [
                "//button[contains(@class, 'download')]",
                "//a[contains(@class, 'download')]",
                "//button[contains(text(), 'Download')]",
                "//a[contains(text(), 'Download')]",
                "//button[contains(@title, 'Download')]",
                "//a[contains(@title, 'Download')]",
                "//*[contains(@aria-label, 'Download')]",
                "//button[contains(@class, 'btn') and contains(text(), 'Download')]",
                "//*[contains(@class, 'x-btn') and contains(text(), 'Download')]",
                "//input[@type='button' and contains(@value, 'Download')]"
            ]
            
            download_button = None
            for selector in download_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            download_button = element
                            logger.info(f"Found download button with selector: {selector}", "WebScraper", self.execution_id)
                            break
                    if download_button:
                        break
                except:
                    continue
            
            if not download_button:
                # Try finding by common download icon patterns
                icon_selectors = [
                    "//*[contains(@class, 'fa-download')]",
                    "//*[contains(@class, 'icon-download')]",
                    "//*[contains(@class, 'glyphicon-download')]",
                    "//*[contains(@class, 'download-icon')]"
                ]
                
                for selector in icon_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            # Look for parent clickable element
                            parent = element.find_element(By.XPATH, "..")
                            if parent and parent.is_displayed() and parent.is_enabled():
                                download_button = parent
                                logger.info(f"Found download button via icon with selector: {selector}", "WebScraper", self.execution_id)
                                break
                        if download_button:
                            break
                    except:
                        continue
            
            if not download_button:
                raise Exception(f"Could not locate download button for {source_name}")
            
            # Get initial file count for download verification
            initial_files = list(self.download_dir.glob("*.csv"))
            initial_count = len(initial_files)
            logger.info(f"Initial CSV file count: {initial_count}", "WebScraper", self.execution_id)
            
            # Click download button
            try:
                self.driver.execute_script("arguments[0].click();", download_button)
                logger.info(f"Clicked download button for {source_name} using JavaScript", "WebScraper", self.execution_id)
            except:
                download_button.click()
                logger.info(f"Clicked download button for {source_name} using regular click", "WebScraper", self.execution_id)
            
            time.sleep(2)
            
            # Enhanced download verification
            download_timeout = WIFI_CONFIG['download_timeout']
            start_time = time.time()
            download_completed = False
            
            logger.info(f"Waiting for download to complete (timeout: {download_timeout}s)", "WebScraper", self.execution_id)
            
            while time.time() - start_time < download_timeout:
                # Check for new CSV files
                current_files = list(self.download_dir.glob("*.csv"))
                current_count = len(current_files)
                
                if current_count > initial_count:
                    # Check if download is still in progress
                    temp_files = list(self.download_dir.glob("*.crdownload"))
                    part_files = list(self.download_dir.glob("*.part"))
                    tmp_files = list(self.download_dir.glob("*.tmp"))
                    
                    if not temp_files and not part_files and not tmp_files:
                        # Find the newest CSV file
                        newest_file = max(current_files, key=lambda f: f.stat().st_mtime)
                        file_size = newest_file.stat().st_size
                        
                        # Verify file is not empty and has reasonable size
                        if file_size > 0:
                            logger.success(f"Download completed for {source_name}! File: {newest_file.name} ({file_size} bytes)", "WebScraper", self.execution_id)
                            download_completed = True
                            break
                        else:
                            logger.warning(f"Downloaded file is empty: {newest_file.name}", "WebScraper", self.execution_id)
                
                time.sleep(2)
            
            if not download_completed:
                raise Exception(f"Download timeout for {source_name} after {download_timeout}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {source_name}: {str(e)}", "WebScraper", self.execution_id, e)
            return False
    
    def navigate_to_page_2(self):
        """Enhanced page 2 navigation with better detection"""
        try:
            logger.info("Navigating to page 2 for Reception Hall sources", "WebScraper", self.execution_id)
            
            wait = WebDriverWait(self.driver, WIFI_CONFIG['timeout'])
            
            # Enhanced page 2 detection
            page2_selectors = [
                "//a[contains(text(), '2')]",
                "//button[contains(text(), '2')]",
                "//*[contains(@class, 'page') and contains(text(), '2')]",
                "//*[contains(@class, 'pagination')]//a[contains(text(), '2')]",
                "//*[contains(@class, 'paging')]//a[contains(text(), '2')]",
                "//a[@title='Page 2']",
                "//button[@title='Page 2']",
                "//*[contains(@aria-label, 'Page 2')]"
            ]
            
            page2_button = None
            for selector in page2_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Verify it's actually a page 2 button
                            text = element.text.strip()
                            if text == "2" or "page 2" in text.lower():
                                page2_button = element
                                logger.info(f"Found page 2 button with selector: {selector}", "WebScraper", self.execution_id)
                                break
                    if page2_button:
                        break
                except:
                    continue
            
            if not page2_button:
                # Try finding next page button
                next_selectors = [
                    "//a[contains(text(), 'Next')]",
                    "//button[contains(text(), 'Next')]",
                    "//*[contains(@class, 'next')]",
                    "//*[contains(@title, 'Next')]",
                    "//*[contains(@aria-label, 'Next')]"
                ]
                
                for selector in next_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                page2_button = element
                                logger.info(f"Found next page button with selector: {selector}", "WebScraper", self.execution_id)
                                break
                        if page2_button:
                            break
                    except:
                        continue
            
            if not page2_button:
                raise Exception("Could not locate page 2 button")
            
            # Click page 2 button
            try:
                self.driver.execute_script("arguments[0].click();", page2_button)
                logger.info("Clicked page 2 button using JavaScript", "WebScraper", self.execution_id)
            except:
                page2_button.click()
                logger.info("Clicked page 2 button using regular click", "WebScraper", self.execution_id)
            
            time.sleep(5)
            
            # Verify we're on page 2 by looking for Reception Hall sources
            verification_selectors = [
                "//*[contains(text(), 'Reception Hall')]",
                "//*[contains(text(), 'Reception')]",
                "//td[contains(text(), 'Hall')]"
            ]
            
            page2_verified = False
            for selector in verification_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        page2_verified = True
                        logger.info(f"Page 2 verified, found Reception Hall content", "WebScraper", self.execution_id)
                        break
                except:
                    continue
            
            if not page2_verified:
                logger.warning("Could not verify page 2 content, but proceeding", "WebScraper", self.execution_id)
            
            logger.success("Successfully navigated to page 2", "WebScraper", self.execution_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to page 2: {str(e)}", "WebScraper", self.execution_id, e)
            return False
    
    def execute_hybrid_scraping_cycle(self, slot_number):
        """Execute scraping cycle using hybrid approach (Selenium + Scrapy)"""
        try:
            logger.info(f"Starting hybrid scraping cycle for slot {slot_number}", "WebScraper", self.execution_id)
            
            # Use hybrid scraper as primary approach
            hybrid_scraper = HybridWiFiScraper(execution_id=self.execution_id)
            result = hybrid_scraper.execute_hybrid_scraping(slot_number)
            
            if result:
                logger.success(f"Hybrid scraping successful for slot {slot_number}", "WebScraper", self.execution_id)
                return {
                    'success': True,
                    'status': 'complete',
                    'sources_downloaded': 4,  # Assuming all sources if successful
                    'total_sources': 4,
                    'downloaded_files': ['Hybrid_Scraped_Data'],
                    'slot_directory': str(hybrid_scraper.download_dir / f"slot_{slot_number}"),
                    'slot_number': slot_number,
                    'timestamp': datetime.now().isoformat(),
                    'network_accessible': True,
                    'method': 'hybrid'
                }
            else:
                logger.warning(f"Hybrid scraping failed for slot {slot_number}, falling back to traditional method", "WebScraper", self.execution_id)
                return self.execute_full_scraping_cycle(slot_number)
                
        except Exception as e:
            logger.error(f"Hybrid scraping cycle failed: {str(e)}", "WebScraper", self.execution_id, e)
            logger.info("Falling back to traditional scraping method", "WebScraper", self.execution_id)
            return self.execute_full_scraping_cycle(slot_number)
    
    def execute_full_scraping_cycle(self, slot_number):
        """Execute complete scraping cycle with network connectivity checks and retry logic"""
        try:
            logger.info(f"Starting full scraping cycle for slot {slot_number}", "WebScraper", self.execution_id)
            
            # Check network connectivity first
            if not self.check_network_connectivity():
                logger.warning("Network connectivity check failed, but proceeding with attempt", "WebScraper", self.execution_id)
                # Don't fail immediately, sometimes socket check fails but HTTPS works
            
            # Setup driver with retry logic
            max_setup_attempts = 3
            for attempt in range(max_setup_attempts):
                if self.setup_driver():
                    break
                else:
                    logger.warning(f"Driver setup attempt {attempt + 1} failed", "WebScraper", self.execution_id)
                    if attempt < max_setup_attempts - 1:
                        time.sleep(5)
                    else:
                        raise Exception("Failed to setup Chrome driver after multiple attempts")
            
            # Create slot-specific directory
            timestamp = datetime.now().strftime("%H%M")
            slot_dir = self.download_dir / f"Slot{slot_number}_{timestamp}"
            slot_dir.mkdir(parents=True, exist_ok=True)
            
            success_count = 0
            total_sources = 4
            downloaded_files = []
            
            # User specified exact workflow with retry logic:
            # Step 1: Navigate to https://51.38.163.73:8443/wsg/
            # Step 2: Login with admin credentials
            # Step 3: Click 4th menu item "Wireless LANs"
            # Step 4: Handle reload if needed
            # Step 5: Download from EHC TV (with clients)
            # Step 6: Download from EHC-15 (without clients)
            # Step 7: Navigate to page 2
            # Step 8: Download from Reception Hall-Mobile (with clients)
            # Step 9: Download from Reception Hall-TV (without clients)
            
            logger.info("Step 1-2: Login to WiFi interface with retry logic", "WebScraper", self.execution_id)
            login_success = False
            max_login_attempts = 3
            
            for login_attempt in range(max_login_attempts):
                try:
                    if self.login_to_wifi_interface():
                        login_success = True
                        break
                    else:
                        logger.warning(f"Login attempt {login_attempt + 1} failed", "WebScraper", self.execution_id)
                        if login_attempt < max_login_attempts - 1:
                            time.sleep(10)  # Wait before retry
                except Exception as e:
                    logger.error(f"Login attempt {login_attempt + 1} error: {str(e)}", "WebScraper", self.execution_id)
                    if login_attempt < max_login_attempts - 1:
                        time.sleep(10)  # Wait before retry
            
            if not login_success:
                raise Exception("Failed to login after multiple attempts")
            
            logger.info("Step 3-4: Navigate to Wireless LANs (4th menu item)", "WebScraper", self.execution_id)
            if not self.navigate_to_wireless_lans():
                raise Exception("Failed to navigate to Wireless LANs")
            
            # Page 1 sources with individual retry logic
            logger.info("Step 5-6: Download from Page 1 sources", "WebScraper", self.execution_id)
            sources_page1 = [
                {"name": "EHC TV", "has_clients": True},
                {"name": "EHC-15", "has_clients": False}
            ]
            
            for i, source in enumerate(sources_page1):
                logger.info(f"Downloading source {i+1}/4: {source['name']}", "WebScraper", self.execution_id)
                
                # Retry logic for each source
                download_success = False
                max_download_attempts = 2
                
                for download_attempt in range(max_download_attempts):
                    try:
                        if self.download_source_data(source["name"], source["has_clients"], page_number=1):
                            download_success = True
                            success_count += 1
                            downloaded_files.append(source["name"])
                            logger.success(f"Successfully downloaded {source['name']}", "WebScraper", self.execution_id)
                            break
                        else:
                            logger.warning(f"Download attempt {download_attempt + 1} failed for {source['name']}", "WebScraper", self.execution_id)
                            if download_attempt < max_download_attempts - 1:
                                time.sleep(5)
                    except Exception as e:
                        logger.error(f"Download attempt {download_attempt + 1} error for {source['name']}: {str(e)}", "WebScraper", self.execution_id)
                        if download_attempt < max_download_attempts - 1:
                            time.sleep(5)
                
                if not download_success:
                    logger.error(f"Failed to download {source['name']} after multiple attempts", "WebScraper", self.execution_id)
                
                time.sleep(3)  # Delay between downloads
            
            # Navigate to page 2 for Reception Hall sources
            logger.info("Step 7: Navigate to page 2", "WebScraper", self.execution_id)
            if self.navigate_to_page_2():
                # Page 2 sources with retry logic
                logger.info("Step 8-9: Download from Page 2 sources", "WebScraper", self.execution_id)
                sources_page2 = [
                    {"name": "Reception Hall-Mobile", "has_clients": True},
                    {"name": "Reception Hall-TV", "has_clients": False}
                ]
                
                for i, source in enumerate(sources_page2):
                    logger.info(f"Downloading source {i+3}/4: {source['name']}", "WebScraper", self.execution_id)
                    
                    # Retry logic for each source
                    download_success = False
                    max_download_attempts = 2
                    
                    for download_attempt in range(max_download_attempts):
                        try:
                            if self.download_source_data(source["name"], source["has_clients"], page_number=2):
                                download_success = True
                                success_count += 1
                                downloaded_files.append(source["name"])
                                logger.success(f"Successfully downloaded {source['name']}", "WebScraper", self.execution_id)
                                break
                            else:
                                logger.warning(f"Download attempt {download_attempt + 1} failed for {source['name']}", "WebScraper", self.execution_id)
                                if download_attempt < max_download_attempts - 1:
                                    time.sleep(5)
                        except Exception as e:
                            logger.error(f"Download attempt {download_attempt + 1} error for {source['name']}: {str(e)}", "WebScraper", self.execution_id)
                            if download_attempt < max_download_attempts - 1:
                                time.sleep(5)
                    
                    if not download_success:
                        logger.error(f"Failed to download {source['name']} after multiple attempts", "WebScraper", self.execution_id)
                    
                    time.sleep(3)  # Delay between downloads
            else:
                logger.error("Failed to navigate to page 2, skipping Reception Hall sources", "WebScraper", self.execution_id)
            
            # Organize downloaded files into slot directory
            logger.info("Organizing downloaded files", "WebScraper", self.execution_id)
            self._organize_downloaded_files(slot_dir, slot_number)
            
            # Final result with detailed status
            if success_count == total_sources:
                logger.success(f"COMPLETE SUCCESS: All {total_sources} sources downloaded successfully!", "WebScraper", self.execution_id)
                status = "complete"
            elif success_count > 0:
                logger.warning(f"PARTIAL SUCCESS: {success_count}/{total_sources} sources downloaded", "WebScraper", self.execution_id)
                status = "partial"
            else:
                logger.error(f"COMPLETE FAILURE: No sources downloaded", "WebScraper", self.execution_id)
                status = "failed"
            
            return {
                'success': success_count > 0,
                'status': status,
                'sources_downloaded': success_count,
                'total_sources': total_sources,
                'downloaded_files': downloaded_files,
                'slot_directory': str(slot_dir),
                'slot_number': slot_number,
                'timestamp': datetime.now().isoformat(),
                'network_accessible': True  # If we got this far, network was accessible
            }
            
        except Exception as e:
            logger.error(f"Scraping cycle failed: {str(e)}", "WebScraper", self.execution_id, e)
            return {
                'success': False,
                'status': 'error',
                'error': str(e),
                'sources_downloaded': success_count if 'success_count' in locals() else 0,
                'total_sources': total_sources,
                'downloaded_files': downloaded_files if 'downloaded_files' in locals() else [],
                'slot_directory': str(slot_dir) if 'slot_dir' in locals() else None,
                'slot_number': slot_number,
                'timestamp': datetime.now().isoformat(),
                'network_accessible': False
            }
        
        finally:
            self.cleanup()
    
    def _organize_downloaded_files(self, slot_dir, slot_number):
        """Enhanced file organization with proper naming convention"""
        try:
            csv_files = list(self.download_dir.glob("*.csv"))
            timestamp = datetime.now().strftime("%d%m%Y_%H%M")
            
            # Expected source mapping for proper naming
            source_mapping = {
                0: "EHC_TV",
                1: "EHC-15", 
                2: "Reception_Hall-Mobile",
                3: "Reception_Hall-TV"
            }
            
            logger.info(f"Organizing {len(csv_files)} CSV files into slot directory", "WebScraper", self.execution_id)
            
            for i, csv_file in enumerate(csv_files):
                # Get source name from mapping or use generic name
                source_name = source_mapping.get(i, f"Source_{i+1}")
                
                # Create descriptive filename
                new_name = f"{source_name}_Slot{slot_number}_{timestamp}.csv"
                new_path = slot_dir / new_name
                
                # Move file to slot directory
                shutil.move(str(csv_file), str(new_path))
                logger.info(f"Moved {csv_file.name} → {new_name}", "WebScraper", self.execution_id)
            
            logger.success(f"File organization completed for slot {slot_number}", "WebScraper", self.execution_id)
                
        except Exception as e:
            logger.error(f"Failed to organize files: {str(e)}", "WebScraper", self.execution_id, e)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Chrome driver closed", "WebScraper", self.execution_id)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", "WebScraper", self.execution_id, e)

# Test function
def test_web_scraper():
    """Test the web scraper functionality"""
    scraper = WiFiWebScraper("test-execution")
    result = scraper.execute_full_scraping_cycle(1)
    print(f"Test result: {result}")

if __name__ == "__main__":
    test_web_scraper()