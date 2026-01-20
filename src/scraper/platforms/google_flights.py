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
        url = "https://www.google.com/travel/flights"
        self.browser.get_page(url)
        
        self.interactions.handle_cookie_consent()
        
        logger.info(f"Searching flights from {origin} to {destination} on {date} (Return: {return_date})")
        
        search_url = self.interactions.construct_search_url(origin, destination, date, return_date)
        self.browser.get_page(search_url)
        
        logger.info("Waiting for results to load...")
        self.browser.random_sleep(3, 5)
        
        flights_found = []
        
        try:
            base_search_url = self.driver.current_url
            num_cards = 5
            
            for i in range(num_cards):
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, "li.pIav2d")
                    if i >= len(cards):
                        break
                        
                    card = cards[i]
                    
                    # Parse data
                    data = self.parser.parse_flight_card(card)
                    
                    # Capture deep link
                    data['flight_url'] = self.interactions.capture_flight_url(card, base_search_url)

                    flights_found.append(data)
                    
                except Exception as e:
                    logger.warning(f"Failed to process flight card {i}: {e}")
                    # Try to reset state
                    try:
                        self.driver.get(base_search_url)
                        self.browser.random_sleep(2, 3)
                    except:
                        pass
                    continue
            
            return flights_found, base_search_url
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return [], None
