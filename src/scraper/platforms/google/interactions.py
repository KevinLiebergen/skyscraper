
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("skyscraper.platforms.google.interactions")

class GoogleInteractions:
    """
    Handles interactions with the Google Flights page (navigation, clicking, etc.).
    """
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.driver = browser_manager.get_driver()

    def handle_cookie_consent(self):
        """
        Attempts to accept cookies if the banner appears.
        """
        try:
            # Check for button with text "Accept all"
            # Using xpath to find by text as it's most robust for this specific case
            accept_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
            )
            accept_button.click()
            logger.info("Clicked cookie consent.")
            self.browser_manager.random_sleep(1, 2)
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

    def capture_flight_url(self, index, base_search_url):
        """
        Clicks on a flight card to capture its specific deep link.
        Refetch the element by index to avoid stale handles.
        """
        try:
            # Re-locate the card list and get the specific index
            # Selenium approach: Find all elements again
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".pIav2d")
            
            if index >= len(cards):
                return base_search_url
            
            card = cards[index]
            # Scroll into view if needed
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            time.sleep(1) # Small pause for scroll
            
            card.click()
            self.browser_manager.random_sleep(2, 3)
            
            # Wait for URL to change or just capture current
            flight_url = self.driver.current_url
            
            # Navigate back to list to reset state
            self.driver.get(base_search_url)
            self.browser_manager.random_sleep(2, 3)
            
            return flight_url
        except Exception as e:
            logger.warning(f"Failed to capture flight URL: {e}")
            # Ensure return to base url if we are lost
            if self.driver.current_url != base_search_url:
                 self.driver.get(base_search_url)
                 self.browser_manager.random_sleep(2, 3)
            return base_search_url
