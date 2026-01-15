from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("skyscraper.platforms")

class FlightPlatform(ABC):
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.get_driver()

    @abstractmethod
    def search_flights(self, origin, destination, date):
        """
        Abstract method to search for flights.
        Should return a list of results or a formatted string.
        """
        pass
