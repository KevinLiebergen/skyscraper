import argparse
import logging
from config.settings import TELEGRAM_TOKEN
from logger.setup import setup_logger
from scraper.browser import BrowserManager
from scraper.platforms.google_flights import GoogleFlightsScraper
from notifications.telegram import TelegramNotifier
from notifications.formatters import format_flight_results

def main():
    # 1. Setup Logger
    logger = setup_logger()
    logger.info("Starting Skyscraper Flight Scraper")

    # 2. Parse Arguments
    parser = argparse.ArgumentParser(description="Scrape flight prices and notify via Telegram.")
    parser.add_argument("--origin", required=True, help="Flight origin (e.g., LON)")
    parser.add_argument("--destination", required=True, help="Flight destination (e.g., NYC)")
    parser.add_argument("--date", required=True, help="Flight date (YYYY-MM-DD)")
    parser.add_argument("--return-date", help="Return flight date (YYYY-MM-DD). If omitted, searches one-way.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    # 3. Setup Browser
    browser = BrowserManager(headless=args.headless)
    
    # 4. Resolve Locations
    # Efficiently transform city names to IATA/City codes if needed
    from utils.locations import FlightLocationHandler
    loc_handler = FlightLocationHandler()
    
    origin_code = loc_handler.get_iata_code(args.origin)
    dest_code = loc_handler.get_iata_code(args.destination)
    
    logger.info(f"Resolved: {args.origin} -> {origin_code}, {args.destination} -> {dest_code}")

    try:
        # 5. Initialize Platform
        # We could add a factory here if we had multiple platforms
        scraper = GoogleFlightsScraper(browser)

        # 6. Scrape
        results = scraper.search_flights(origin_code, dest_code, args.date, args.return_date)

        # 7. Notify
        if results:
            message = format_flight_results(results, args.origin, args.destination, args.date, args.return_date)
            
            notifier = TelegramNotifier()
            notifier.send_message(message)
        else:
            logger.info("No results found or scraping failed.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # 7. Cleanup
        browser.close()
        logger.info("Finished.")

if __name__ == "__main__":
    main()
