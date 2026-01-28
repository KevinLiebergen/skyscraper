import logging
from selenium.webdriver.common.by import By
from .flight_platform import FlightPlatform
from .google.interactions import GoogleInteractions
from .google.parser import GoogleParser

logger = logging.getLogger("skyscraper.platforms.google")

class GoogleFlightsScraper(FlightPlatform):
    def __init__(self, browser):
        super().__init__(browser)
        self.interactions = GoogleInteractions(browser)
        self.parser = GoogleParser()

    def search_flights(self, origin, destination, date, return_date=None):
        """
        Searches Google Flights using helper modules.
        """
        search_url = self.interactions.construct_search_url(origin, destination, date, return_date)
        
        # Navigate
        self.browser_manager.navigate(search_url)
        self.interactions.handle_cookie_consent()
        
        # Wait for results to load
        try:
            # Wait for either the results list or the "no flights found" message
            self.page.wait_for_selector(".pIav2d", timeout=30000)
        except:
             logger.warning("Timeout waiting for flight results.")
             return [], search_url

        # Check for results
        # Limit to 5 results as requested
        flight_cards = self.page.locator(".pIav2d").all()[:5]
        logger.info(f"Found {len(flight_cards)} potential flight cards (processing top 5).")

        results = []
        for index, card in enumerate(flight_cards):
             # Extract details using Parser (passing the locator)
             flight_data = self.parser.parse_flight_card(card)
             
             # Get Deep Link
             flight_url = self.interactions.capture_flight_url(index, search_url)
             flight_data['url'] = flight_url
             
             results.append(flight_data)
             
        return results, search_url
