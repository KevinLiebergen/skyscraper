import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger("skyscraper.browser")

class BrowserManager:
    def __init__(self, headless=False, proxy=None):
        self.driver = self._setup_driver(headless, proxy)
        self._setup_stealth()

    def _setup_driver(self, headless, proxy):
        logger.info(f"Initializing Selenium Driver (Headless: {headless})")
        
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Additional arguments to be less bot-like
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-infobars")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if proxy:
             options.add_argument(f'--proxy-server={proxy}')
             logger.info(f"Setting up browser with proxy: {proxy}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def _setup_stealth(self):
        # Apply stealth settings
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            logger.warning(f"Failed to apply stealth scripts: {e}")

    def get_driver(self):
        return self.driver
        
    def get_page(self):
        # Compatibility alias if needed, but prefer get_driver
        return self.driver

    def close(self):
        if self.driver:
            self.driver.quit()
        logger.info("Browser closed.")

    def random_sleep(self, min_seconds=2, max_seconds=5):
        """Simulate human wait time."""
        sleep_time = random.uniform(min_seconds, max_seconds)
        logger.info(f"Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    def navigate(self, url, retries=3):
        for attempt in range(retries):
            logger.info(f"Navigating to {url} (Attempt {attempt+1}/{retries})")
            try:
                self.driver.set_page_load_timeout(60)
                self.driver.get(url)
            except Exception as e:
                logger.warning(f"Navigation error: {e}")
                if attempt < retries - 1:
                    logger.info("Retrying navigation in 10s...")
                    time.sleep(10)
                    continue
                raise e

            # Check for ScraperAPI specific error content
            try:
                content = self.driver.page_source.lower()
                if "too many simultaneous requests" in content:
                    logger.warning("ScraperAPI Error: Too many simultaneous requests. Waiting 15s to drain connections...")
                    time.sleep(15)
                    continue # Retry loop
            except Exception as e:
                logger.warning(f"Error checking page content: {e}")

            self.random_sleep()
            return

        logger.error(f"Failed to navigate to {url} after {retries} attempts.")
