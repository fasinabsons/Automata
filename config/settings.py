import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# Updated directory structure as per user requirements
CSV_DIR = Path(r"C:\Users\Lenovo\Videos\Automata\EHC_Data")
MERGED_DIR = Path(r"C:\Users\Lenovo\Videos\Automata\EHC_Data_Merge")
REPORTS_DIR = Path(r"C:\Users\Lenovo\Videos\Automata\EHC_Data_Pdf")

# WiFi Management System Configuration
WIFI_CONFIG = {
    'target_url': 'https://51.38.163.73:8443/wsg/',  # Fixed with trailing slash
    'username': 'admin',
    'password': 'AdminFlower@123',
    'login_timeout': 30,
    'page_load_timeout': 60,
    'download_timeout': 120,
    'retry_attempts': 3,
    'retry_delay': 5,
    
    # Network extraction configuration - EXACT NAMES from screenshots
    'networks_to_extract': [
        {
            'name': 'EHC TV',
            'page': 1,
            'selector_type': 'table_row',
            'text': 'EHC TV',
            'clients_tab_required': True,
            'row_identifier': 'td',
            'column_index': 0  # Name column
        },
        {
            'name': 'EHC-15', 
            'page': 1,
            'selector_type': 'table_row',
            'text': 'EHC-15',
            'clients_tab_required': False,  # Download directly
            'row_identifier': 'td',
            'column_index': 0
        },
        {
            'name': 'Reception Hall-Mobile',
            'page': 2,
            'selector_type': 'table_row',
            'text': 'Reception Hall-Mobile',
            'clients_tab_required': True,
            'row_identifier': 'td',
            'column_index': 0
        },
        {
            'name': 'Reception Hall-TV',
            'page': 2,
            'selector_type': 'table_row',
            'text': 'Reception Hall-TV', 
            'clients_tab_required': False,  # Clients tab vanishes after page change
            'row_identifier': 'td',
            'column_index': 0
        }
    ],
    
    # Enhanced menu navigation selectors
    'wireless_menu_selectors': [
        "//div[contains(@class, 'x-tree-node-text') and normalize-space(text())='Wireless LANs']",
        "//span[normalize-space(text())='Wireless LANs']",
        "//a[normalize-space(text())='Wireless LANs']",
        "//*[normalize-space(text())='Wireless LANs']",
        "//div[contains(text(), 'Wireless LANs')]"
    ],
    
    # View Mode selectors (List/Group toggle from screenshots)
    'view_mode_selectors': [
        "//span[normalize-space(text())='List']",
        "//button[contains(@class, 'x-btn') and contains(text(), 'List')]",
        "//*[contains(@class, 'view-mode') and contains(text(), 'List')]",
        "//div[contains(@class, 'x-toolbar')]//span[text()='List']"
    ],
    
    # Page navigation selectors (numbered pagination from screenshots)
    'page_2_selectors': [
        "//span[normalize-space(text())='2' and contains(@class, 'x-btn-inner')]",
        "//button[normalize-space(text())='2']",
        "//a[normalize-space(text())='2']",
        "//*[contains(@class, 'x-toolbar-paging')]//span[text()='2']",
        "//div[contains(@class, 'x-toolbar')]//span[text()='2']"
    ],
    
    # Download button selectors (FontAwesome download icon from screenshots)
    'download_button_selectors': [
        "//span[contains(@class, 'fa-download')]",
        "//button[contains(@class, 'fa-download')]",
        "//*[contains(@class, 'x-btn-glyph') and contains(@style, 'FontAwesome')]",
        "//span[contains(@class, 'x-btn-icon') and contains(@class, 'fa-download')]",
        "//*[@title='Download' or @aria-label='Download']",
        "//button[contains(@class, 'download')]"
    ],
    
    # Clients tab selectors (from screenshots showing active tab)
    'clients_tab_selectors': [
        "//span[normalize-space(text())='Clients' and contains(@class, 'x-tab-inner')]",
        "//div[contains(@class, 'x-tab') and contains(text(), 'Clients')]",
        "//*[contains(@class, 'x-tab-strip')]//span[text()='Clients']",
        "//a[contains(@class, 'x-tab') and contains(text(), 'Clients')]"
    ],
    
    # Table row selectors for network selection
    'table_row_selectors': [
        "//table//tr[td[normalize-space(text())='{network_name}']]",
        "//tr[contains(@class, 'x-grid-row') and .//text()[normalize-space()='{network_name}']]",
        "//div[contains(@class, 'x-grid')]//tr[.//text()[contains(., '{network_name}')]]"
    ]
}

# VBS Application Configuration
VBS_CONFIG = {
    'primary_path': r'C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk',
    'fallback_path': r'\\192.168.10.16\e\ArabianLive\ArabianLive_MoonFlower\AbsonsItERP.exe',
    'username': 'Vj',
    'password': '',
    'default_date': '01/01/2023',
    'timeout': 60,
    'retry_attempts': 2
}

# Scheduling Configuration
SCHEDULE_CONFIG = {
    'slots': [
        {'time': '09:30', 'name': 'morning_slot'},
        {'time': '13:00', 'name': 'afternoon_slot'},
        {'time': '15:00', 'name': 'evening_slot'}
    ],
    'merge_delay_minutes': 5,  # Wait 5 minutes after last slot before merging
    'max_execution_time_minutes': 45,  # Maximum time per slot
    'inter_slot_delay_minutes': 2,  # Delay between processing different slots
}

# Chrome Configuration with enhanced SSL and detection bypass
CHROME_CONFIG = {
    'headless': False,  # Set to True for background operation
    'window_size': '1920,1080',
    'download_timeout': 120,
    'page_load_timeout': 60,
    'implicit_wait': 10,
    
    # Enhanced Chrome options for Ruckus Wireless with anti-detection
    'chrome_options': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',  # Faster loading
        '--disable-javascript-harmony-shipping',
        
        # Enhanced SSL and security bypass for Ruckus
        '--ignore-certificate-errors',
        '--ignore-ssl-errors',
        '--ignore-certificate-errors-spki-list', 
        '--ignore-urlfetcher-cert-requests',
        '--allow-running-insecure-content',
        '--disable-web-security',
        '--accept-insecure-certs',
        '--allow-insecure-localhost',
        '--disable-features=VizDisplayCompositor',
        '--test-type',
        '--disable-extensions-file-access-check',
        '--disable-default-apps',
        
        # CRITICAL: Anti-detection measures for Ruckus
        '--disable-blink-features=AutomationControlled',
        '--disable-automation',
        '--disable-infobars',
        '--disable-browser-side-navigation',
        '--disable-renderer-backgrounding',
        '--disable-backgrounding-occluded-windows',
        '--disable-background-timer-throttling',
        '--disable-ipc-flooding-protection',
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-sync',
        '--force-fieldtrials=*BackgroundTracing/default/',
        
        # User agent to avoid detection
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # Performance optimization
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-popup-blocking',
        '--disable-translate',
        '--disable-background-networking',
        '--metrics-recording-only',
        '--no-report-upload'
    ],
    
    # Download preferences
    'download_prefs': {
        "download.default_directory": "",  # Will be set dynamically
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.content_settings.pattern_pairs.*,*.media-stream": {
            "video": 2,
            "audio": 2
        }
    },
    
    # Experimental options for anti-detection
    'experimental_options': {
        "excludeSwitches": ["enable-automation", "enable-logging"],
        "useAutomationExtension": False,
        "prefs": {}  # Will be merged with download_prefs
    }
}

# Timing Configuration for Ruckus Wireless
TIMING_CONFIG = {
    'page_load_wait': 5,        # Wait after page loads
    'element_wait': 10,         # Wait for elements to appear
    'click_delay': 2,           # Delay between clicks
    'download_wait': 30,        # Wait for downloads to complete
    'navigation_wait': 3,       # Wait after navigation
    'tab_switch_wait': 2,       # Wait after switching tabs
    'network_selection_wait': 1, # Wait after selecting network
    'retry_delay': 5,           # Delay between retries
    'screenshot_interval': 10   # Interval for debug screenshots
}

# File Processing Configuration
FILE_CONFIG = {
    # CSV headers from source files (Ruckus format)
    'source_csv_headers': [
        'Hostname',
        'IP Address', 
        'MAC Address',
        'WLAN (SSID)',
        'AP MAC',
        'Data Rate (up)',
        'Data Rate (down)'
    ],
    
    # Excel headers for output file
    'excel_headers': [
        'Hostname',      # A column
        'IP_Address',    # B column  
        'MAC_Address',   # C column
        'Package',       # D column (was WLAN SSID)
        'AP_MAC',        # E column
        'Upload',        # F column (was Data Rate up)
        'Download'       # G column (was Data Rate down)
    ],
    
    # Header mapping
    'header_mapping': {
        'Hostname': 'Hostname',
        'IP Address': 'IP_Address',
        'MAC Address': 'MAC_Address', 
        'WLAN (SSID)': 'Package',
        'AP MAC': 'AP_MAC',
        'Data Rate (up)': 'Upload',
        'Data Rate (down)': 'Download'
    },
    
    # File naming with timestamp
    'excel_filename_template': 'EHC_Upload_Mac_{date}.xlsx',  # {date} = DDMMYYYY
    'csv_filename_template': '{network}_{slot}_{timestamp}.csv',
    
    # Directory structure
    'csv_storage_path': 'EHC_Data/{date_folder}',  # e.g., EHC_Data/03july
    'excel_storage_path': 'EHC_Data_Merge/{date_folder}',  # e.g., EHC_Data_Merge/03july
    'date_folder_format': '%djuly',  # 03july, 04july, etc.
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': 'logs/wifi_automation.log',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'console_output': True
}

# Error Handling Configuration  
ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay_seconds': 5,
    'timeout_seconds': 120,
    'screenshot_on_error': True,
    'save_page_source_on_error': True,
    'continue_on_network_error': True,
    'email_alerts_on_failure': False,  # Can be enabled later
}

# Debug Configuration
DEBUG_CONFIG = {
    'save_screenshots': True,
    'screenshot_interval_seconds': 30,
    'verbose_logging': True,
    'save_page_source': True,
    'pause_on_error': False,  # Set to True for debugging
    'manual_intervention_timeout': 300,  # 5 minutes
    'capture_network_logs': True,
    'save_html_snapshots': True
}

# Create directories
for directory in [DATA_DIR, LOGS_DIR, DOWNLOADS_DIR, CSV_DIR, MERGED_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)