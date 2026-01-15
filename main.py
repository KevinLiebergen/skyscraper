import argparse
import logging
from config.settings import TELEGRAM_TOKEN
from logger.setup import setup_logger
from scraper.browser import BrowserManager
from scraper.platforms.google_flights import GoogleFlightsScraper
from notifications.telegram import TelegramNotifier

def main():
    # 1. Setup Logger
    logger = setup_logger()
    logger.info("Starting Skyscraper Flight Scraper")

    # 2. Parse Arguments
    parser = argparse.ArgumentParser(description="Scrape flight prices and notify via Telegram.")
    parser.add_argument("--origin", required=True, help="Flight origin (e.g., LON)")
    parser.add_argument("--destination", required=True, help="Flight destination (e.g., NYC)")
    parser.add_argument("--date", required=True, help="Flight date (YYYY-MM-DD)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    # 3. Setup Browser
    browser = BrowserManager(headless=args.headless)

    try:
        # 4. Initialize Platform
        # We could add a factory here if we had multiple platforms
        scraper = GoogleFlightsScraper(browser)

        # 5. Scrape
        results = scraper.search_flights(args.origin, args.destination, args.date)

        # 6. Notify
        if results:
            message = f"Flight Search Results ({args.origin} -> {args.destination}, {args.date}):\n"
            message += "\n".join(results)
            
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
