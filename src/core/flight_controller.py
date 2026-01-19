
import logging
from utils.parsing import parse_price
from database.storage import DatabaseManager
from notifications.formatters import format_flight_results
from notifications.telegram import TelegramNotifier

logger = logging.getLogger("skyscraper.core")

class FlightController:
    def __init__(self):
        self.db = DatabaseManager()
        self.notifier = TelegramNotifier()

    def process_results(self, results, args, search_url):
        """
        Filters, deduplicates, and notifies about flight results.
        """
        if not results:
            logger.info("No results found or scraping failed.")
            return

        # 1. Max Price Filtering
        if args.max_price:
            filtered_results = []
            for flight in results:
                price_val = parse_price(flight.get('price'))
                if price_val is not None and price_val <= args.max_price:
                    filtered_results.append(flight)
                else:
                    logger.debug(f"Filtered out flight with price {flight.get('price')}")
            
            logger.info(f"Filtered results: {len(filtered_results)} of {len(results)} kept (Max Price: {args.max_price})")
            results = filtered_results

        if not results:
            logger.info("No flights remain after filtering.")
            return

        # 2. Deduplication (Database Check)
        new_results = []
        for flight in results:
            if self.db.is_flight_new(flight, args.origin, args.destination, args.date, args.return_date):
                new_results.append(flight)
                # Save immediately to ensure persistence
                self.db.save_flight(flight, args.origin, args.destination, args.date, args.return_date)
        
        suppressed_count = len(results) - len(new_results)
        if suppressed_count > 0:
            logger.info(f"Suppressed {suppressed_count} duplicate or price-increased notifications.")

        # 3. Notify
        if new_results:
            message = format_flight_results(new_results, args.origin, args.destination, args.date, args.return_date, search_url)
            self.notifier.send_message(message)
            logger.info(f"Notification sent for {len(new_results)} flights.")
        else:
             logger.info("No new flights found (all duplicates or filtered).")
