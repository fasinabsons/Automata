#!/usr/bin/env python3
"""
Enhanced Web Scraper with Dynamic File Management
Fixes folder creation and file organization issues
"""

import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from core.logger import logger
from modules.dynamic_file_manager import DynamicFileManager
from config.settings import WIFI_CONFIG, CHROME_CONFIG, TIMING_CONFIG

class EnhancedWebScraper:
    """
    Enhanced web scraper with dynamic file management
    Automatically creates date-based folders and organizes files
    """
    
    def __init__(self, execution_id: Optional[str] = None):
        self.execution_id = execution_id or f"scraper_{int(time.time())}"
        self.driver = None
        self.wait = None
        
        # Initialize file manager
        self.file_manager = DynamicFileManager()
        
        # Setup directories for today
        self.directories = self.file_manager.create_date_directories()
        self.download_dir = self.directories['csv']
        
        # Create temporary download directory
        self.temp_download_dir = Path("downloads") / "temp"
        self.temp_download_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Enhanced Web Scraper initialized: {self.execution_id}", "WebScraper", self.execution_id)
        logger.info(f"Download directory: {self.download_dir}", "WebScraper", self.execution_id)
        logger.info(f"Temporary directory: {self.temp_download_dir}", "WebScraper", self.execution_id)
    
    def setup_chrome_driver(self) -> bool:
        """
        Setup Chrome driver with enhanced configuration
        Downloads to temporary directory first, then moves to date folder
        """
        try:
            logger.info("Setting up Chrome driver with enhanced configuration", "WebScraper", self.execution_id)
            
            options = Options()
            
            # Add Chrome options
            for option in CHROME_CONFIG['chrome_options']:
                options.add_argument(option)
            
            # Set window size
            options.add_argument(f"--window-size={CHROME_CONFIG['window_size']}")
            
            # Download preferences - Use temporary directory
            download_prefs = CHROME_CONFIG['download_prefs'].copy()
            download_prefs['download.default_directory'] = str(self.temp_download_dir.absolute())
            
            # Experimental options
            exp_options = CHROME_CONFIG['experimental_options'].copy()
            exp_options['prefs'] = download_prefs
            
            for key, value in exp_options.items():
                options.add_experimental_option(key, value)
            
            # Create driver
            self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            self.driver.implicitly_wait(CHROME_CONFIG['implicit_wait'])
            self.driver.set_page_load_timeout(CHROME_CONFIG['page_load_timeout'])
            
            # Create wait object
            self.wait = WebDriverWait(self.driver, TIMING_CONFIG['element_wait'])
            
            logger.success("Chrome driver setup completed successfully", "WebScraper", self.execution_id)
            return True
            
        except Exception as e:
            logger.error(f"Chrome driver setup failed: {e}", "WebScraper", self.execution_id)
            return False
    
    def login_to_wifi_interface(self) -> bool:
        """
        Login to WiFi interface with enhanced error handling
        """
        try:
            logger.info("Navigating to WiFi interface", "WebScraper", self.execution_id)
            
            # Navigate to login page
            self.driver.get(WIFI_CONFIG['target_url'])
            time.sleep(TIMING_CONFIG['page_load_wait'])
            
            # Find and fill username
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(WIFI_CONFIG['username'])
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(WIFI_CONFIG['password'])
            
            # Click login button
            login_button = self.driver.find_element(By.ID, "loginBtn")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(TIMING_CONFIG['page_load_wait'])
            
            # Verify login success
            if "dashboard" in self.driver.current_url.lower() or "main" in self.driver.current_url.lower():
                logger.success("Login successful", "WebScraper", self.execution_id)
                return True
            else:
                logger.error("Login failed - unexpected page", "WebScraper", self.execution_id)
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}", "WebScraper", self.execution_id)
            return False
    
    def navigate_to_wireless_lans(self) -> bool:
        """
        Navigate to Wireless LANs section
        """
        try:
            logger.info("Navigating to Wireless LANs", "WebScraper", self.execution_id)
            
            # Wait for page to load
            time.sleep(TIMING_CONFIG['navigation_wait'])
            
            # Find and click Wireless LANs menu item (4th item)
            wireless_selectors = [
                "//a[contains(text(), 'Wireless LANs')]",
                "//span[contains(text(), 'Wireless LANs')]",
                "//div[contains(text(), 'Wireless LANs')]",
                "//li[4]//a",  # 4th menu item
                "//nav//li[4]//a"
            ]
            
            for selector in wireless_selectors:
                try:
                    element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    logger.success(f"Clicked Wireless LANs with selector: {selector}", "WebScraper", self.execution_id)
                    break
                except:
                    continue
            else:
                raise Exception("Could not find Wireless LANs menu item")
            
            # Wait for page to load
            time.sleep(TIMING_CONFIG['page_load_wait'])
            
            logger.success("Successfully navigated to Wireless LANs", "WebScraper", self.execution_id)
            return True
            
        except Exception as e:
            logger.error(f"Navigation to Wireless LANs failed: {e}", "WebScraper", self.execution_id)
            return False
    
    def download_network_data(self, network_name: str, requires_clients: bool = False) -> bool:
        """
        Download data for a specific network
        
        Args:
            network_name: Name of the network to download
            requires_clients: Whether to click clients tab first
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            logger.info(f"Downloading data for network: {network_name}", "WebScraper", self.execution_id)
            
            # Find network row
            network_selectors = [
                f"//td[contains(text(), '{network_name}')]",
                f"//tr[contains(., '{network_name}')]//td[1]",
                f"//span[contains(text(), '{network_name}')]"
            ]
            
            network_row = None
            for selector in network_selectors:
                try:
                    network_row = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if not network_row:
                raise Exception(f"Could not find network: {network_name}")
            
            # Click on network row
            network_row.click()
            time.sleep(TIMING_CONFIG['click_delay'])
            
            # Click clients tab if required
            if requires_clients:
                clients_selectors = [
                    "//a[contains(text(), 'Clients')]",
                    "//span[contains(text(), 'Clients')]",
                    "//div[contains(text(), 'Clients')]"
                ]
                
                for selector in clients_selectors:
                    try:
                        clients_tab = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        clients_tab.click()
                        time.sleep(TIMING_CONFIG['tab_switch_wait'])
                        logger.info(f"Clicked clients tab for {network_name}", "WebScraper", self.execution_id)
                        break
                    except:
                        continue
            
            # Get files before download
            files_before = set(self.temp_download_dir.glob("*.csv"))
            
            # Find and click download button
            download_selectors = [
                "//span[contains(@class, 'fa-download')]",
                "//button[contains(@title, 'Download')]",
                "//a[contains(@href, 'download')]",
                "//span[contains(@class, 'x-btn-glyph')]"
            ]
            
            download_clicked = False
            for selector in download_selectors:
                try:
                    download_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    download_btn.click()
                    download_clicked = True
                    logger.info(f"Clicked download button for {network_name}", "WebScraper", self.execution_id)
                    break
                except:
                    continue
            
            if not download_clicked:
                raise Exception(f"Could not find download button for {network_name}")
            
            # Wait for download to complete
            timeout = time.time() + TIMING_CONFIG['download_wait']
            while time.time() < timeout:
                files_after = set(self.temp_download_dir.glob("*.csv"))
                new_files = files_after - files_before
                
                if new_files:
                    # Check if download is complete
                    complete_files = [f for f in new_files if not f.name.endswith(('.crdownload', '.tmp', '.part'))]
                    
                    if complete_files:
                        logger.success(f"Download completed for {network_name}: {len(complete_files)} files", "WebScraper", self.execution_id)
                        return True
                
                time.sleep(2)
            
            logger.warning(f"Download timeout for {network_name}", "WebScraper", self.execution_id)
            return False
            
        except Exception as e:
            logger.error(f"Download failed for {network_name}: {e}", "WebScraper", self.execution_id)
            return False
    
    def navigate_to_page_2(self) -> bool:
        """
        Navigate to page 2 for Reception Hall networks
        """
        try:
            logger.info("Navigating to page 2", "WebScraper", self.execution_id)
            
            # Find page 2 button
            page2_selectors = [
                "//a[contains(text(), '2')]",
                "//button[contains(text(), '2')]",
                "//span[contains(text(), '2')]",
                "//div[contains(@class, 'paging')]//a[contains(text(), '2')]"
            ]
            
            for selector in page2_selectors:
                try:
                    page2_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    page2_btn.click()
                    time.sleep(TIMING_CONFIG['page_load_wait'])
                    logger.success("Successfully navigated to page 2", "WebScraper", self.execution_id)
                    return True
                except:
                    continue
            
            logger.warning("Could not find page 2 button", "WebScraper", self.execution_id)
            return False
            
        except Exception as e:
            logger.error(f"Navigation to page 2 failed: {e}", "WebScraper", self.execution_id)
            return False
    
    def execute_full_download_cycle(self) -> Dict[str, Any]:
        """
        Execute complete download cycle for all networks
        """
        try:
            logger.info("Starting full download cycle", "WebScraper", self.execution_id)
            
            # Setup Chrome driver
            if not self.setup_chrome_driver():
                return {"success": False, "error": "Chrome driver setup failed"}
            
            # Login to WiFi interface
            if not self.login_to_wifi_interface():
                return {"success": False, "error": "Login failed"}
            
            # Navigate to Wireless LANs
            if not self.navigate_to_wireless_lans():
                return {"success": False, "error": "Navigation to Wireless LANs failed"}
            
            # Download from page 1 networks
            page1_networks = [
                {"name": "EHC TV", "requires_clients": True},
                {"name": "EHC-15", "requires_clients": False}
            ]
            
            success_count = 0
            total_networks = 4
            
            for network in page1_networks:
                if self.download_network_data(network["name"], network["requires_clients"]):
                    success_count += 1
                time.sleep(TIMING_CONFIG['network_selection_wait'])
            
            # Navigate to page 2
            if self.navigate_to_page_2():
                page2_networks = [
                    {"name": "Reception Hall-Mobile", "requires_clients": True},
                    {"name": "Reception Hall-TV", "requires_clients": False}
                ]
                
                for network in page2_networks:
                    if self.download_network_data(network["name"], network["requires_clients"]):
                        success_count += 1
                    time.sleep(TIMING_CONFIG['network_selection_wait'])
            
            # Organize downloaded files
            organization_result = self.file_manager.organize_downloaded_files(self.temp_download_dir)
            
            # Calculate results
            success_rate = (success_count / total_networks) * 100
            
            result = {
                "success": success_count > 0,
                "networks_downloaded": success_count,
                "total_networks": total_networks,
                "success_rate": success_rate,
                "download_directory": str(self.download_dir),
                "organization_result": organization_result,
                "execution_id": self.execution_id
            }
            
            if success_count == total_networks:
                logger.success(f"Complete success: All {total_networks} networks downloaded", "WebScraper", self.execution_id)
            elif success_count > 0:
                logger.warning(f"Partial success: {success_count}/{total_networks} networks downloaded", "WebScraper", self.execution_id)
            else:
                logger.error("Complete failure: No networks downloaded", "WebScraper", self.execution_id)
            
            return result
            
        except Exception as e:
            error_msg = f"Download cycle failed: {e}"
            logger.error(error_msg, "WebScraper", self.execution_id)
            return {"success": False, "error": error_msg}
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Cleanup resources
        """
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Chrome driver closed", "WebScraper", self.execution_id)
            
            # Clean up temporary directory if empty
            if self.temp_download_dir.exists():
                remaining_files = list(self.temp_download_dir.glob("*"))
                if not remaining_files:
                    try:
                        self.temp_download_dir.rmdir()
                        logger.info("Cleaned up temporary download directory", "WebScraper", self.execution_id)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Cleanup error: {e}", "WebScraper", self.execution_id)

# Convenience function for external use
def run_enhanced_scraping() -> Dict[str, Any]:
    """
    Run enhanced scraping with automatic file organization
    """
    scraper = EnhancedWebScraper()
    return scraper.execute_full_download_cycle()

if __name__ == "__main__":
    # Test the enhanced web scraper
    result = run_enhanced_scraping()
    print("Scraping result:", result) 