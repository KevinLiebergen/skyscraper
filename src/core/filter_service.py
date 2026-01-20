
import logging
from utils.parsing import parse_price

logger = logging.getLogger("skyscraper.core.filter")

class FilterService:
    """
    Handles filtering of flight results based on user criteria.
    """
    def filter_results(self, results, args):
        """
        Filters results based on arguments (e.g., max_price).
        Returns the filtered list of results.
        """
        if not results:
            return []

        if not args.max_price:
            return results

        filtered_results = []
        for flight in results:
            price_val = parse_price(flight.get('price'))
            if price_val is not None and price_val <= args.max_price:
                filtered_results.append(flight)
            else:
                logger.debug(f"Filtered out flight with price {flight.get('price')}")
        
        logger.info(f"Filtered results: {len(filtered_results)} of {len(results)} kept (Max Price: {args.max_price})")
        return filtered_results
