import logging
import uuid
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

        # 1. SerpApi Path
        if args.serpapi_key:
            from scraper.platforms.serpapi_flights import SerpApiFlights
            
            # Handle multiple countries
            countries = self._get_countries(args)
            
            for country in countries:
                source_label = f"SerpApi ({country.upper()})"
                logger.debug(f"Creating SerpApi scraper for {country}")
                
                # Instance per country? actually SerpApiFlights is stateless regarding country 
                # except for the method call, but runner expects an object it can call.
                # However, SerpApiFlights.search_flights takes country_code.
                # To align with the Runner which just calls `search_flights(origin, dest, date, return_date)`,
                # we might need to wrap it or pre-configure it.
                # Current SerpApiFlights design requires country passed to search_flights.
                # We should update SerpApiFlights to accept country in __init__ or 
                # create a partial/wrapper here.
                
                # Let's create a wrapper/configured instance to satisfy a common interface if possible.
                # Or simply pass the country in the metadata and let Runner handle it?
                # BETTER: The Runner shouldn't know about "country" arg if possible. 
                # It should just call search().
                # Let's wrapping it in a simple adapter or use a lambda? 
                # Code consistency -> let's assume we modify SerpApiFlights or wrap it.
                
                # Let's start by modifying SerpApiFlights to optionally take country in constructor
                # Or just return a closure/bound method? 
                # Simpler: Return the scraper and a metadata dict with 'country_code'.
                # But Runner previously called `scraper.search_flights(..., country_code=country)`
                # We want Runner to just do `scraper.search_flights(...)`.
                
                # Let's use a ConfiguredSerpApi wrapper class here for cleanliness.
                scraper = ConfiguredSerpApi(args.serpapi_key, country)
                scrapers.append((scraper, {"source": source_label}))
                
            return scrapers

        # 2. Browser/Proxy Path (Google Flights)
        # Verify proxies
        proxies = self.proxy_manager.get_proxies(args)
        
        for i, proxy in enumerate(proxies):
            source_label = self.proxy_manager.get_source_label(proxy, args)
            logger.debug(f"Creating Browser scraper for {source_label}")
            
            # For browser, we need to create the browser manager.
            # IMPORTANT: BrowserManager opens a browser on __init__.
            # Creating all browsers upfront might crash system if list is long.
            # The previous runner created them sequentially inside the loop.
            # To preserve this, we should return a "Factory/Creator" or "Lazy" object?
            # OR we change ScraperRunner to handle the lifecycle.
            
            # SRP: Runner runs things. Factory prepares things.
            # If we pass a list of *initialized* browsers, we use too much RAM.
            # Solution: Return a LazyScraper that initializes on `search_flights`.
            
            scraper = LazyBrowserScraper(args.headless, proxy)
            scrapers.append((scraper, {"source": source_label}))

        return scrapers

    def _get_countries(self, args):
        if args.country:
            return [c.strip().lower() for c in args.country.split(',') if c.strip()]
        return ["us"]

class ConfiguredSerpApi:
    """Wrapper to pre-configure SerpApi with a country."""
    def __init__(self, key, country):
        from scraper.platforms.serpapi_flights import SerpApiFlights
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
