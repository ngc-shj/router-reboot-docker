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
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(
            self.driver, 
            self.config['router']['connection']['timeout_seconds']
        )

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
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        # 基本的なオプション
        chrome_options.add_argument('--headless=new')  # 新しいヘッドレスモード
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # メモリ関連の設定
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # キャッシュとセッション関連
        chrome_options.add_argument(f'--user-data-dir=/tmp/chrome')
        chrome_options.add_argument('--disk-cache-dir=/selenium-cache')
        chrome_options.add_argument('--disable-extensions')
        
        # ネットワーク関連
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        # パフォーマンス設定
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # ログレベルの設定
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')

        try:
            service = Service(
                executable_path=os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
            )
            
            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            
            # ページロードのタイムアウト設定
            driver.set_page_load_timeout(
                self.config['router']['connection']['timeout_seconds']
            )
            
            # JavaScriptの実行を待機
            driver.implicitly_wait(10)
            
            # ウィンドウサイズを設定
            driver.set_window_size(1920, 1080)
            
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
        """Login to the router"""
        try:
            # ページロード前に少し待機
            time.sleep(2)
            
            # アクセス
            self.driver.get(self.config['router']['connection']['base_url'])
            
            # ページが完全にロードされるまで待機
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # さらに少し待機してJavaScriptの実行を確実に
            time.sleep(2)
            
            # ユーザー名とパスワードを入力
            if not self._safe_find_and_input(
                By.ID, 
                "form_USERNAME", 
                self.config['router']['auth']['username'],
                timeout=20  # タイムアウトを延長
            ):
                return False
                
            if not self._safe_find_and_input(
                By.ID, 
                "form_PASSWORD", 
                self.config['router']['auth']['password'],
                timeout=20
            ):
                return False

            # ログインボタンをクリック
            if not self._safe_find_and_click(By.CLASS_NAME, "button_login", timeout=20):
                return False

            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def reboot(self) -> bool:
        """Reboot the router
        
        Returns:
            bool: True if reboot successful, False otherwise
        """
        retry_count = self.config['router']['options']['retry_count']
        retry_interval = self.config['router']['options']['retry_interval_seconds']

        for attempt in range(retry_count):
            try:
                if not self.login():
                    raise Exception("Failed to login")

                # Access reboot page
                self.driver.get(
                    f"{self.config['router']['connection']['base_url']}/save_init.html"
                )

                # Find and click the reboot button
                reboot_button = self.wait.until(
                    EC.element_to_be_clickable((By.NAME, "reboot"))
                )
                reboot_button.click()

                # Wait for confirmation dialog
                time.sleep(2)

                logger.info("Router is rebooting...")
                time.sleep(120)  # Wait for router to restart

                logger.info("Reboot command sent successfully")
                return True

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{retry_count} failed: {e}")
                if attempt < retry_count - 1:
                    logger.info(f"Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                    continue
                return False

            finally:
                try:
                    self.driver.quit()
                except Exception:
                    pass

    def __enter__(self):
        """Context manager entry
        
        Returns:
            RouterReboot: self
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit
        
        Ensures proper cleanup of resources
        """
        try:
            self.driver.quit()
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
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)

