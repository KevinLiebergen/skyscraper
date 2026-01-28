from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("skyscraper.platforms")

class FlightPlatform(ABC):
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        if browser_manager:
            self.page = browser_manager.get_page()
        else:
            self.page = None

    @abstractmethod
    def search_flights(self, origin, destination, date, return_date=None):
        """
        Abstract method to search for flights.
        Should return a list of results or a formatted string.
        """
        pass
