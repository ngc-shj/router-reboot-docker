import yaml
import logging
import time
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RouterReboot:
    def __init__(self, config_path: str = '/app/config/config.yml'):
        self.config = self._load_config(config_path)
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, self.config['router']['connection']['timeout_seconds'])

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _setup_driver(self) -> webdriver.Chrome:
        """Chromeドライバーの設定とセットアップ"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # ヘッドレスモード
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')  # SSL証明書エラーを無視

        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.config['router']['connection']['timeout_seconds'])
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise

    def _safe_find_and_click(self, by: By, value: str, timeout: int = 10) -> bool:
        """要素を安全に見つけてクリック"""
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
        """要素を安全に見つけて入力"""
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
        """ルーターにログイン"""
        try:
            # ログインページにアクセス
            self.driver.get(self.config['router']['connection']['base_url'])
            
            # ユーザー名とパスワードを入力
            if not self._safe_find_and_input(By.ID, "form_USERNAME", 
                                           self.config['router']['auth']['username']):
                return False
                
            if not self._safe_find_and_input(By.ID, "form_PASSWORD", 
                                           self.config['router']['auth']['password']):
                return False

            # ログインボタンをクリック
            if not self._safe_find_and_click(By.CLASS_NAME, "button_login"):
                return False

            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def reboot(self) -> bool:
        """ルーターを再起動"""
        retry_count = self.config['router']['options']['retry_count']
        retry_interval = self.config['router']['options']['retry_interval_seconds']

        for attempt in range(retry_count):
            try:
                if not self.login():
                    raise Exception("Failed to login")

                # 再起動ページにアクセス
                self.driver.get(f"{self.config['router']['connection']['base_url']}/save_init.html")

                # 再起動ボタンを見つけてクリック
                reboot_button = self.wait.until(
                    EC.element_to_be_clickable((By.NAME, "reboot"))
                )
                reboot_button.click()

                # 再起動確認を待つ
                time.sleep(2)

                # ルーターの再起動を待機
                logger.info("Router is rebooting...")
                time.sleep(120)  # 2分待機

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

if __name__ == "__main__":
    try:
        rebooter = RouterReboot()
        rebooter.reboot()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)

