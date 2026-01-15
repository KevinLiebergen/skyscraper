import argparse
import logging
import sys
import os

# Add src/ directory to the path so modules can be found
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

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
    parser.add_argument("--max-price", type=float, help="Maximum price filter (e.g., 500)")
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

        # 7. Filter, Deduplicate & Notify
        if results:
            # A. Max Price Filtering
            if args.max_price:
                from utils.parsing import parse_price
                filtered_results = []
                for flight in results:
                    price_val = parse_price(flight.get('price'))
                    if price_val is not None and price_val <= args.max_price:
                        filtered_results.append(flight)
                    else:
                        logger.debug(f"Filtered out flight with price {flight.get('price')}")
                
                logger.info(f"Filtered results: {len(filtered_results)} of {len(results)} kept (Max Price: {args.max_price})")
                results = filtered_results

            # B. Deduplication (Database Check)
            from database.storage import DatabaseManager
            db = DatabaseManager()
            
            new_results = []
            for flight in results:
                if db.is_flight_new(flight, args.origin, args.destination, args.date, args.return_date):
                    new_results.append(flight)
                    # We save it immediately so next run knows about it.
                    # Or we could save batch after success. Saving here is safer against crashes.
                    db.save_flight(flight, args.origin, args.destination, args.date, args.return_date)
            
            if len(new_results) < len(results):
                logger.info(f"Suppressed {len(results) - len(new_results)} duplicate notifications.")

            # C. Notify
            if new_results:
                message = format_flight_results(new_results, args.origin, args.destination, args.date, args.return_date)
                
                notifier = TelegramNotifier()
                notifier.send_message(message)
            else:
                 logger.info("No new flights found (all duplicates or filtered).")
        else:
            logger.info("No results found or scraping failed.")

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
