import logging
import sys
import os

# Add src/ directory to the path so modules can be found
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from logger.setup import setup_logger
from scraper.browser import BrowserManager
from scraper.platforms.google_flights import GoogleFlightsScraper
from config.arguments import parse_arguments
from core.flight_controller import FlightController
from core.proxy_manager import ProxyManager
from core.result_aggregator import ResultAggregator
from utils.locations import FlightLocationHandler
from notifications.telegram import TelegramNotifier

def main():
    # 1. Setup Logger
    logger = setup_logger()
    logger.info("Starting Skyscraper Flight Scraper")

    # 2. Parse Arguments
    args = parse_arguments()

    # 3. Load Proxies
    proxy_manager = ProxyManager()
    proxies = proxy_manager.get_proxies(args)
    
    try:
        # 4. Resolve Locations
        loc_handler = FlightLocationHandler()
        origin_code = loc_handler.get_iata_code(args.origin)
        dest_code = loc_handler.get_iata_code(args.destination)
        
        logger.info(f"Resolved: {args.origin} -> {origin_code}, {args.destination} -> {dest_code}")

        all_results = []
        last_search_url = None

        # 5. Scrape with Proxies
        for i, proxy in enumerate(proxies):
            source_label = proxy_manager.get_source_label(proxy, args)
            logger.info(f"--- Starting scrape with source: {source_label} ({i+1}/{len(proxies)}) ---")
            
            browser = None
            try:
                browser = BrowserManager(headless=args.headless, proxy=proxy)
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

        # 6. Process Results (Best Price Logic)
        if not all_results:
             logger.warning("No results found from any source.")
             return

        result_aggregator = ResultAggregator()
        final_results = result_aggregator.consolidate_results(all_results)

        # 7. Process Final Results
        controller = FlightController()
        controller.process_results(final_results, args, last_search_url)

    except Exception as e:
        error_msg = f"🚨 *Skyscraper Error* 🚨\n\nAn unexpected error occurred:\n`{str(e)}`"
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        try:
            notifier = TelegramNotifier()
            notifier.send_message(error_msg)
        except Exception as notification_error:
            logger.error(f"Failed to send error notification: {notification_error}")
    finally:
        logger.info("Finished.")

if __name__ == "__main__":
    main()
