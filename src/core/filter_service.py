
import logging
from utils.parsing import parse_price, parse_stops

logger = logging.getLogger("skyscraper.core.filter")

class FilterService:
    """
    Handles filtering of flight results based on user criteria.
    """
    def filter_results(self, results, args):
        """
        Filters results based on arguments (e.g., max_price, max_stops).
        Returns the filtered list of results.
        """
        if not results:
            return []

        filtered_results = results

        if args.max_price:
            filtered_results = self._filter_by_max_price(filtered_results, args.max_price)

        if args.max_stops is not None:
            filtered_results = self._filter_by_max_stops(filtered_results, args.max_stops)

        return filtered_results

    def _filter_by_max_price(self, results, max_price):
        filtered_results = []
        for flight in results:
            price_val = parse_price(flight.get('price'))
            if price_val is not None and price_val <= max_price:
                filtered_results.append(flight)
            else:
                logger.debug(f"Filtered out flight with price {flight.get('price')}")

        logger.info(f"Filtered results: {len(filtered_results)} of {len(results)} kept (Max Price: {max_price})")
        return filtered_results

    def _filter_by_max_stops(self, results, max_stops):
        filtered_results = []
        for flight in results:
            stops_val = parse_stops(flight.get('stops'))
            if stops_val is not None and stops_val <= max_stops:
                filtered_results.append(flight)
            else:
                logger.debug(f"Filtered out flight with stops {flight.get('stops')}")

        logger.info(f"Filtered results: {len(filtered_results)} of {len(results)} kept (Max Stops: {max_stops})")
        return filtered_results
