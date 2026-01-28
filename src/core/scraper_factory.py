import logging
from scraper.platforms.serpapi_flights import SerpApiFlights

logger = logging.getLogger("skyscraper.core.factory")

class ScraperFactory:
    """
    Factory for creating the appropriate scraper instances based on configuration.
    Returns a list of tuples: (scraper_instance, context_info_dict)
    """
    def __init__(self):
        pass

    def create_scrapers(self, args):
        """
        Creates a list of ready-to-use scraper instances.
        Each item is (scraper, metadata).
        Metadata contains 'source_label', 'country', etc.
        """
        scrapers = []

        # Enforce SerpApi Key
        if not args.serpapi_key:
            # Check environment variable potentially, but CLI arg is preferred
            # If mandatory, we should raise or return empty with warning
            logger.error("No SerpApi Key provided. Use --serpapi-key.")
            raise ValueError("SerpApi Key is required.")

        # Handle multiple countries
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
