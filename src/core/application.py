
import logging
import sys
import os

from logger.setup import setup_logger
from config.arguments import parse_arguments
from core.flight_controller import FlightController
from core.result_aggregator import ResultAggregator
from core.scraper_runner import ScraperRunner
from core.scraper_factory import ScraperFactory
from utils.locations import FlightLocationHandler
from notifications.telegram import TelegramNotifier

logger = logging.getLogger("skyscraper.core.app")

class SkyscraperApp:
    """
    Facade for the Skyscraper application.
    Orchestrates the entire scraping flow.
    """
    def __init__(self):
        self.logger = setup_logger()

    def run(self):
        self.logger.info("Starting Skyscraper Flight Scraper")
        try:
            # 1. Parse Arguments
            args = parse_arguments()

            # 2. Create Scrapers
            factory = ScraperFactory()
            scrapers = factory.create_scrapers(args)
            
            # 3. Resolve Locations
            loc_handler = FlightLocationHandler()
            origin_code = loc_handler.get_iata_code(args.origin)
            dest_code = loc_handler.get_iata_code(args.destination)
            
            self.logger.info(f"Resolved: {args.origin} -> {origin_code}, {args.destination} -> {dest_code}")

            # 4. Run Scrapers
            runner = ScraperRunner(headless=args.headless)
            all_results, last_search_url = runner.run_scrapers(scrapers, args, origin_code, dest_code)

            # 5. Process Results
            if not all_results:
                 self.logger.warning("No results found from any source.")
                 return

            result_aggregator = ResultAggregator()
            final_results = result_aggregator.consolidate_results(all_results)

            controller = FlightController()
            controller.process_results(final_results, args, last_search_url)

        except Exception as e:
            self._handle_error(e)
        finally:
            self.logger.info("Finished.")

    def _handle_error(self, e):
        error_msg = f"🚨 *Skyscraper Error* 🚨\n\nAn unexpected error occurred:\n`{str(e)}`"
        self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        try:
            notifier = TelegramNotifier()
            notifier.send_message(error_msg)
        except Exception as notification_error:
            self.logger.error(f"Failed to send error notification: {notification_error}")
