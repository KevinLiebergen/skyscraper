
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .flight_platform import FlightPlatform
from .google.interactions import GoogleInteractions
from .google.parser import GoogleParser

logger = logging.getLogger("skyscraper.platforms.google")

class GoogleFlightsScraper(FlightPlatform):
    def __init__(self, browser):
        super().__init__(browser)
        self.interactions = GoogleInteractions(browser)
        self.parser = GoogleParser()
        self.driver = browser.get_driver()

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
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pIav2d"))
            )
        except:
             logger.warning("Timeout waiting for flight results.")
             return [], search_url

        # Check for results
        # Limit to 5 results as requested
        flight_cards = self.driver.find_elements(By.CSS_SELECTOR, ".pIav2d")[:5]
        logger.info(f"Found {len(flight_cards)} potential flight cards (processing top 5).")

        results = []
        # Copy basic list first to avoid StaleElementReferenceException during iteration if page changes
        # But here we need to interact page to get deep links, so we have to be careful
        # The capture_flight_url method handles re-grabbing the list
        
        for index in range(len(flight_cards)):
             # Re-fetch the card to ensure freshness
             cards = self.driver.find_elements(By.CSS_SELECTOR, ".pIav2d")
             if index >= len(cards):
                 break
             
             card = cards[index]
             
             # Extract details using Parser (passing the web element)
             flight_data = self.parser.parse_flight_card(card)
             
             # Get Deep Link
             # This will navigate and come back, so 'card' will be stale afterwards
             flight_url = self.interactions.capture_flight_url(index, search_url)
             flight_data['url'] = flight_url
             
             results.append(flight_data)
             
        return results, search_url
