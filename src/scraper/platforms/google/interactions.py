
import logging

logger = logging.getLogger("skyscraper.platforms.google.interactions")

class GoogleInteractions:
    """
    Handles interactions with the Google Flights page (navigation, clicking, etc.).
    """
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.page = browser_manager.get_page()

    def handle_cookie_consent(self):
        """
        Attempts to accept cookies if the banner appears.
        """
        try:
            # Check for button with text "Accept all"
            accept_button = self.page.get_by_role("button", name="Accept all")
            if accept_button.is_visible(timeout=3000):
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
            cards = self.page.locator(".pIav2d").all()
            if index >= len(cards):
                return base_search_url
            
            card = cards[index]
            card.click()
            self.browser_manager.random_sleep(2, 3)
            
            # Wait for URL to change or just capture current
            flight_url = self.page.url
            
            # Navigate back to list to reset state
            self.page.goto(base_search_url)
            self.browser_manager.random_sleep(2, 3)
            
            return flight_url
        except Exception as e:
            logger.warning(f"Failed to capture flight URL: {e}")
            # Ensure return to base url if we are lost
            if self.page.url != base_search_url:
                 self.page.goto(base_search_url)
                 self.browser_manager.random_sleep(2, 3)
            return base_search_url
