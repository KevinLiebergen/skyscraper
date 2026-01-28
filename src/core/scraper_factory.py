
import logging
from scraper.platforms.serpapi_flights import SerpApiFlights
from scraper.browser import BrowserManager
from scraper.platforms.google_flights import GoogleFlightsScraper
from core.proxy_manager import ProxyManager

logger = logging.getLogger("skyscraper.core.factory")

class ScraperFactory:
    """
    Factory for creating the appropriate scraper instances based on configuration.
    Returns a list of tuples: (scraper_instance, context_info_dict)
    """
    def __init__(self):
        self.proxy_manager = ProxyManager()

    def create_scrapers(self, args):
        """
        Creates a list of ready-to-use scraper instances.
        Each item is (scraper, metadata).
        Metadata contains 'source_label', 'country', etc.
        """
        scrapers = []

        # 1. SerpApi Path (Preferred)
        if args.serpapi_key:
            return self._create_serpapi_scrapers(args)

        # 2. Browser Path (Fallback)
        logger.info("No SerpApi key provided. Falling back to Browser Automation.")
        
        # Get proxies (or local direct)
        proxies = self.proxy_manager.get_proxies(args)
        
        for i, proxy in enumerate(proxies):
            source_label = self.proxy_manager.get_source_label(proxy, args)
            logger.debug(f"Creating Browser scraper for {source_label}")
            
            scraper = LazyBrowserScraper(args.headless, proxy)
            scrapers.append((scraper, {"source": source_label}))

        return scrapers

    def _create_serpapi_scrapers(self, args):
        scrapers = []
        countries = self._get_countries(args)
        for country in countries:
            source_label = f"SerpApi ({country.upper()})"
            logger.debug(f"Creating SerpApi scraper for {country}")
            scraper = ConfiguredSerpApi(args.serpapi_key, country)
            scrapers.append((scraper, {"source": source_label}))
        return scrapers

    def _get_countries(self, args):
        if args.country:
            return [c.strip().lower() for c in args.country.split(',') if c.strip()]
        return ["us"]

class ConfiguredSerpApi:
    """Wrapper to pre-configure SerpApi with a country."""
    def __init__(self, key, country):
        self.delegate = SerpApiFlights(key)
        self.country = country
        
    def search_flights(self, origin, destination, date, return_date):
        return self.delegate.search_flights(origin, destination, date, return_date, country_code=self.country)

class LazyBrowserScraper:
    """Delays browser creation until search is called."""
    def __init__(self, headless, proxy):
        self.headless = headless
        self.proxy = proxy
        self.browser_manager = None
        
    def search_flights(self, origin, destination, date, return_date):
        try:
            self.browser_manager = BrowserManager(headless=self.headless, proxy=self.proxy)
            scraper = GoogleFlightsScraper(self.browser_manager)
            return scraper.search_flights(origin, destination, date, return_date)
        finally:
            if self.browser_manager:
                self.browser_manager.close()
