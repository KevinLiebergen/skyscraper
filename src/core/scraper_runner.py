
import logging
from scraper.browser import BrowserManager
from scraper.platforms.google_flights import GoogleFlightsScraper

logger = logging.getLogger("skyscraper.core.runner")

class ScraperRunner:
    """
    Orchestrates the scraping process across multiple proxies.
    """
    def __init__(self, headless=False):
        self.headless = headless

    def run_scrapers(self, proxies, args, origin_code, dest_code, proxy_manager):
        """
        Iterates through proxies and runs the scraper for each.
        Returns aggregated results and the last search URL.
        """
        all_results = []
        last_search_url = None

        for i, proxy in enumerate(proxies):
            source_label = proxy_manager.get_source_label(proxy, args)
            logger.info(f"--- Starting scrape with source: {source_label} ({i+1}/{len(proxies)}) ---")
            
            browser = None
            try:
                browser = BrowserManager(headless=self.headless, proxy=proxy)
                scraper = GoogleFlightsScraper(browser)
                results, search_url = scraper.search_flights(origin_code, dest_code, args.date, args.return_date)
                
                if search_url:
                    last_search_url = search_url
                
                # Tag results with source
                for res in results:
                    res['source'] = source_label
                    all_results.append(res)
                    
                logger.info(f"Found {len(results)} flights via {source_label}")

            except Exception as e:
                logger.error(f"Error scraping with proxy {source_label}: {e}")
            finally:
                if browser:
                    browser.close()
                    
        return all_results, last_search_url
