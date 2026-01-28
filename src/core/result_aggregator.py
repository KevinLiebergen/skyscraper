
import logging
from utils.parsing import parse_price

logger = logging.getLogger("skyscraper.core.aggregator")

class ResultAggregator:
    """
    Handles consolidation and deduplication of flight results from multiple sources.
    """
    def __init__(self):
        pass

    def consolidate_results(self, all_results):
        """
        Deduplicates results and selects the best price option for each unique flight.
        """
        if not all_results:
             return []

        # Key: Airline + Departure + Arrival (heuristic for same flight) + Flight Number isn't available, so we use times.
        best_flights = {}
        
        for flight in all_results:
            # Create a unique key for the flight option
            key = f"{flight.get('airline')}_{flight.get('departure_time')}_{flight.get('arrival_time')}"
            
            price = parse_price(flight.get('price'))
            
            # Store if it's the first time seeing this flight or if we found a cheaper price
            if key not in best_flights:
                best_flights[key] = (price, flight)
            else:
                existing_price, existing_flight = best_flights[key]
                new_source = flight.get('source')
                
                if price is not None:
                    # Case 1: Cheaper Price -> Replace completely
                    if existing_price is None or price < existing_price:
                        best_flights[key] = (price, flight)
                    # Case 2: Same Price -> Merge source info to show it's available elsewhere too
                    elif price == existing_price:
                        if new_source and new_source not in existing_flight.get('source', ''):
                            existing_flight['source'] = f"{existing_flight.get('source', '')}, {new_source}"
                            # Update the stored tuple with the modified flight object
                            best_flights[key] = (existing_price, existing_flight)

        final_results = [item[1] for item in best_flights.values()]
        logger.info(f"Consolidated {len(all_results)} raw results into {len(final_results)} unique options.")
        
        return final_results
