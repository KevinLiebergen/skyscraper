
import logging
from scraper.browser import BrowserManager
from scraper.platforms.google_flights import GoogleFlightsScraper

logger = logging.getLogger("skyscraper.core.runner")

class ScraperRunner:
    """
    Orchestrates the scraping process by executing a list of pre-configured scrapers.
    Follows SRP by only handling execution, not creation.
    """
    def __init__(self, headless=False):
        self.headless = headless

    def run_scrapers(self, scrapers, args, origin_code, dest_code):
        """
        Iterates through the provided list of scrapers and executes search.
        scrapers: List of (scraper_instance, metadata) tuples.
        """
        all_results = []
        last_search_url = None
        
        total = len(scrapers)

        for i, (scraper, metadata) in enumerate(scrapers):
            source_label = metadata.get("source", "Unknown")
            logger.info(f"--- Starting scrape with source: {source_label} ({i+1}/{total}) ---")
            
            try:
                # Common interface: search_flights(origin, dest, date, return_date)
                results, search_url = scraper.search_flights(origin_code, dest_code, args.date, args.return_date)
                
                if search_url:
                    last_search_url = search_url
                
                # Tag results
                for res in results:
                    res['source'] = source_label
                    # Inject fallback URL if needed (mainly for SerpApi)
                    if not res.get('flight_url') and search_url:
                        res['flight_url'] = search_url
                    all_results.append(res)
                    
                logger.info(f"Found {len(results)} flights via {source_label}")

            except Exception as e:
                logger.error(f"Error scraping with {source_label}: {e}")
                
        return all_results, last_search_url
