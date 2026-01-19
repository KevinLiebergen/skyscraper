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
from utils.locations import FlightLocationHandler
from notifications.telegram import TelegramNotifier

def main():
    # 1. Setup Logger
    logger = setup_logger()
    logger.info("Starting Skyscraper Flight Scraper")

    # 2. Parse Arguments
    args = parse_arguments()

    # 3. Setup Browser
    browser = BrowserManager(headless=args.headless)
    
    try:
        # 4. Resolve Locations
        loc_handler = FlightLocationHandler()
        origin_code = loc_handler.get_iata_code(args.origin)
        dest_code = loc_handler.get_iata_code(args.destination)
        
        logger.info(f"Resolved: {args.origin} -> {origin_code}, {args.destination} -> {dest_code}")

        # 5. Scrape
        scraper = GoogleFlightsScraper(browser)
        results, search_url = scraper.search_flights(origin_code, dest_code, args.date, args.return_date)

        # 6. Process Results
        controller = FlightController()
        controller.process_results(results, args, search_url)

    except Exception as e:
        error_msg = f"🚨 *Skyscraper Error* 🚨\n\nAn unexpected error occurred:\n`{str(e)}`"
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        try:
            notifier = TelegramNotifier()
            notifier.send_message(error_msg)
        except Exception as notification_error:
            logger.error(f"Failed to send error notification: {notification_error}")
    finally:
        # 7. Cleanup
        browser.close()
        logger.info("Finished.")

if __name__ == "__main__":
    main()
