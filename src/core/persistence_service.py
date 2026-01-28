
import logging
from database.storage import DatabaseManager

logger = logging.getLogger("skyscraper.core.persistence")

class PersistenceService:
    """
    Handles persistence of flight results and checks for new/unique flights.
    """
    def __init__(self):
        self.db = DatabaseManager()

    def filter_new_flights(self, results, args):
        """
        Checks results against the database and returns only new flights.
        Also saves the new flights to the database.
        """
        new_results = []
        for flight in results:
            logger.debug(f"Checking flight: {flight.get('airline')} {flight.get('departure_time')} {flight.get('price')}")
            if self.db.is_flight_new(flight, args.origin, args.destination, args.date, args.return_date):
                new_results.append(flight)
                # Save immediately to ensure persistence
                self.db.save_flight(flight, args.origin, args.destination, args.date, args.return_date)
        
        suppressed_count = len(results) - len(new_results)
        if suppressed_count > 0:
            logger.info(f"Suppressed {suppressed_count} duplicate or price-increased notifications.")
            
        return new_results
