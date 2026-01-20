
import logging
from selenium.webdriver.common.by import By

logger = logging.getLogger("skyscraper.platforms.google.interactions")

class GoogleInteractions:
    """
    Handles interactions with the Google Flights page (navigation, clicking, etc.).
    """
    def __init__(self, browser):
        self.browser = browser
        self.driver = browser.driver

    def handle_cookie_consent(self):
        """
        Attempts to accept cookies if the banner appears.
        """
        try:
            accept_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Accept all')]")
            accept_button.click()
            logger.info("Clicked cookie consent.")
            self.browser.random_sleep(1, 2)
        except:
            pass 

    def construct_search_url(self, origin, destination, date, return_date=None):
        """
        Constructs the Google Flights search URL.
        """
        if return_date:
            query = f"{origin} to {destination} on {date} returning on {return_date}"
        else:
            query = f"{origin} to {destination} on {date} one way"
        
        return f"https://www.google.com/travel/flights?q={query.replace(' ', '+')}"

    def capture_flight_url(self, card, base_search_url):
        """
        Clicks on a flight card to capture its specific deep link.
        """
        try:
            card.click()
            self.browser.random_sleep(2, 3)
            
            flight_url = self.driver.current_url
            
            # Navigate back to list to reset state
            self.driver.get(base_search_url)
            self.browser.random_sleep(2, 3)
            
            return flight_url
        except Exception as e:
            logger.warning(f"Failed to capture flight URL: {e}")
            # Ensure return to base url
            if self.driver.current_url != base_search_url:
                 self.driver.get(base_search_url)
                 self.browser.random_sleep(2, 3)
            return base_search_url
