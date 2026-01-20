
import logging
from notifications.formatters import format_flight_results
from notifications.telegram import TelegramNotifier
from core.filter_service import FilterService
from core.persistence_service import PersistenceService

logger = logging.getLogger("skyscraper.core")

class FlightController:
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.filter_service = FilterService()
        self.persistence_service = PersistenceService()

    def process_results(self, results, args, search_url):
        """
        Filters, deduplicates, and notifies about flight results.
        """
        if not results:
            logger.info("No results found or scraping failed.")
            return

        # 1. Filter
        filtered_results = self.filter_service.filter_results(results, args)

        if not filtered_results:
            logger.info("No flights remain after filtering.")
            return

        # 2. Persistence & Deduplication
        new_results = self.persistence_service.filter_new_flights(filtered_results, args)

        # 3. Notify
        if new_results:
            message = format_flight_results(new_results, args.origin, args.destination, args.date, args.return_date, search_url)
            self.notifier.send_message(message)
            logger.info(f"Notification sent for {len(new_results)} flights.")
        else:
             logger.info("No new flights found (all duplicates or filtered).")
