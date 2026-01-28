import logging
import random
import time
from playwright.sync_api import sync_playwright

logger = logging.getLogger("skyscraper.browser")

class BrowserManager:
    def __init__(self, headless=False, proxy=None):
        self.playwright = sync_playwright().start()
        self.browser = self._setup_browser(headless, proxy)
        self.context = self._setup_context(proxy)
        self.page = self.context.new_page()
        self._setup_stealth(self.page)

    def _setup_browser(self, headless, proxy):
        logger.info(f"Initializing Playwright Browser (Headless: {headless})")
        # Proxy is set at context level usually, but can be set at launch if global
        # We will handle proxy in context for flexibility, or launch if needed for auth
        
        # Note: Playwright handles proxy auth in launch() or context()
        # For authenticated proxy, we pass it to launch or new_context
        
        launch_args = {
            "headless": headless,
            "args": [
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        }
        
        if proxy:
            # Parse proxy string to check for auth
            # Format: scheme://user:pass@host:port
            server = proxy
            username = None
            password = None
            
            if "@" in proxy:
                from urllib.parse import urlparse
                parsed = urlparse(proxy)
                username = parsed.username
                password = parsed.password
                # Reconstruct server without auth
                server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
                
                launch_args["proxy"] = {
                    "server": server,
                    "username": username,
                    "password": password
                }
                logger.info(f"Setting up browser with authenticated proxy: {server}")
            else:
                 launch_args["proxy"] = {"server": proxy}
                 logger.info(f"Setting up browser with proxy: {proxy}")

        return self.playwright.chromium.launch(**launch_args)

    def _setup_context(self, proxy):
        # Viewport null to use window size
        context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080}, 
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        
        # Bandwidth Optimization: Block heavy resources
        def route_handler(route):
            if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
                route.abort()
            else:
                route.continue_()
                
        context.route("**/*", route_handler)
        
        return context

    def _setup_stealth(self, page):
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

    def get_page(self):
        return self.page

    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
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
                # ScraperAPI can be slow, so we increase timeout to 60s
                self.page.goto(url, timeout=60000)
            except Exception as e:
                logger.warning(f"Navigation error: {e}")
                if attempt < retries - 1:
                    logger.info("Retrying navigation in 10s...")
                    time.sleep(10)
                    continue
                raise e

            # Check for ScraperAPI specific error content
            try:
                content = self.page.content().lower()
                if "too many simultaneous requests" in content:
                    logger.warning("ScraperAPI Error: Too many simultaneous requests. Waiting 15s to drain connections...")
                    time.sleep(15)
                    continue # Retry loop
            except Exception as e:
                logger.warning(f"Error checking page content: {e}")

            self.random_sleep()
            return

        logger.error(f"Failed to navigate to {url} after {retries} attempts.")
