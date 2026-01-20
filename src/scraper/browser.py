import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger("skyscraper.browser")

class BrowserManager:
    def __init__(self, headless=False, proxy=None):
        self.driver = self._setup_driver(headless, proxy)

    def _setup_driver(self, headless, proxy):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        # Human simulation: Screen size and Headers
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Anti-detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if proxy:
            logger.info(f"Setting up browser with proxy: {proxy}")
            options.add_argument(f'--proxy-server={proxy}')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        logger.info("Browser initialized successfully.")
        return driver

    def get_driver(self):
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

    def get_page(self, url):
        logger.info(f"Navigating to {url}")
        self.driver.get(url)
        self.random_sleep()
