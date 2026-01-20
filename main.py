import logging
import sys
import os

# Add src/ directory to the path so modules can be found
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from logger.setup import setup_logger
from config.arguments import parse_arguments
from core.flight_controller import FlightController
from core.proxy_manager import ProxyManager
from core.result_aggregator import ResultAggregator
from core.scraper_runner import ScraperRunner
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
        runner = ScraperRunner(headless=args.headless)
        all_results, last_search_url = runner.run_scrapers(proxies, args, origin_code, dest_code, proxy_manager)

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
