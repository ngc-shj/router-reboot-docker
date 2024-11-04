#!/usr/bin/env python3

import yaml
import logging
import time
import os
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RouterReboot:
    def __init__(self, config_path: str = '/app/config/config.yml'):
        """Initialize the RouterReboot class
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.driver = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file
        
        Args:
            config_path (str): Path to the configuration file
            
        Returns:
            Dict[str, Any]: Configuration dictionary
            
        Raises:
            Exception: If config file cannot be loaded
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver
            
        Raises:
            WebDriverException: If driver setup fails
        """
        chrome_options = Options()
        
        # Basic options for container environment
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Stability improvements
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--mute-audio')
        
        # Memory and performance settings
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-dev-tools')
        
        # Session handling
        chrome_options.add_argument('--disable-session-crashed-bubble')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Cache and data settings
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--deterministic-fetch')
        chrome_options.add_argument('--disk-cache-dir=/tmp/chrome/cache')
        chrome_options.add_argument('--user-data-dir=/tmp/chrome/user-data')
        
        try:
            service = Service(
                executable_path=os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
            )
            
            logger.info("Starting Chrome driver...")
            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            logger.info("Chrome driver started successfully")
            return driver
                
        except WebDriverException as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise

    def _safe_find_and_click(self, by: By, value: str, timeout: int = 10) -> bool:
        """Safely find and click an element
        
        Args:
            by (By): Selenium By locator
            value (str): Element identifier
            timeout (int): Wait timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return True
        except TimeoutException:
            logger.error(f"Element not found or not clickable: {value}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element {value}: {e}")
            return False

    def _safe_find_and_input(self, by: By, value: str, input_text: str, timeout: int = 10) -> bool:
        """Safely find and input text into an element
        
        Args:
            by (By): Selenium By locator
            value (str): Element identifier
            input_text (str): Text to input
            timeout (int): Wait timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            element = self.wait.until(
                EC.presence_of_element_located((by, value))
            )
            element.clear()
            element.send_keys(input_text)
            return True
        except TimeoutException:
            logger.error(f"Element not found: {value}")
            return False
        except Exception as e:
            logger.error(f"Error inputting text to {value}: {e}")
            return False

    def login(self) -> bool:
        """Attempt to login to the router with proper form handling
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Access login page
            self.driver.get(self.config['router']['connection']['base_url'])
            
            # Wait for page load
            wait = WebDriverWait(self.driver, 20)
            wait.until(
                EC.presence_of_element_located((By.NAME, "airstation_uname"))
            )
            
            # Input username
            username_field = self.driver.find_element(By.NAME, "airstation_uname")
            username_field.clear()
            username_field.send_keys(self.config['router']['auth']['username'])
            
            # Input password
            password_field = self.driver.find_element(By.NAME, "airstation_pass")
            password_field.clear()
            password_field.send_keys(self.config['router']['auth']['password'])
            
            # Click login button
            login_button = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "button_login"))
            )
            login_button.click()
            
            # Wait for login processing
            time.sleep(3)
            
            # Verify login success
            if "login.html" in self.driver.current_url:
                raise Exception("Login failed - still on login page")
            
            logger.info("Login successful")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def reboot(self) -> bool:
        """Attempt to reboot the router using direct form interaction
        
        Returns:
            bool: True if reboot successful, False otherwise
        """
        try:
            # Create initial driver
            self.driver = self._setup_driver()
            wait = WebDriverWait(self.driver, 20)
            
            # Initial login
            if not self.login():
                raise Exception("Failed to initial login")
            
            # Access reboot page directly using configured URL
            logger.info("Accessing reboot page...")
            self.driver.get(f"{self.config['router']['connection']['base_url']}/save_init.html")
            
            # Check if redirected to login
            if "login.html" in self.driver.current_url:
                logger.info("Re-authentication required, logging in again...")
                if not self.login():
                    raise Exception("Failed to re-login")
                
                # Try accessing reboot page again
                self.driver.get(f"{self.config['router']['connection']['base_url']}/save_init.html")
            
            # Find and click reboot button
            logger.info("Looking for reboot button...")
            reboot_button = wait.until(
                EC.element_to_be_clickable((By.NAME, "reboot"))
            )
            reboot_button.click()
            
            # Wait for confirmation dialog
            logger.info("Router is rebooting...")
            time.sleep(2)
            
            # Wait for reboot process
            time.sleep(120)
            
            logger.info("Reboot sequence completed")
            success = True
            
        except Exception as e:
            logger.error(f"Reboot attempt failed: {e}")
            success = False
        
        finally:
            # Clean up resources
            try:
                if self.driver:
                    self.driver.quit()
                    self.driver = None
            except Exception as e:
                logger.error(f"Error during driver cleanup: {e}")
        
        return success

    def __enter__(self):
        """Context manager entry method
        
        Returns:
            RouterReboot: self instance
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit method for cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception:
            pass

if __name__ == "__main__":
    try:
        with RouterReboot() as rebooter:
            success = rebooter.reboot()
            if not success:
                logger.error("Router reboot failed")
                exit(1)
            logger.info("Router reboot completed successfully")
            # Successfully completed, exit with status 0
            exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)

