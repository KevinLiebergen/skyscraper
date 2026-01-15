import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .flight_platform import FlightPlatform

logger = logging.getLogger("skyscraper.platforms.google")

class GoogleFlightsScraper(FlightPlatform):
    def search_flights(self, origin, destination, date, return_date=None):
        """
        Searches Google Flights.
        Note: Selectors are clear as of 2024 but subject to change.
        """
        url = "https://www.google.com/travel/flights"
        self.browser.get_page(url)
        
        try:
            # Handle potential cookie consent (common in EU)
            # Try to click 'Accept all' or similar if present
            try:
                accept_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Accept all')]")
                accept_button.click()
                logger.info("Clicked cookie consent.")
                self.browser.random_sleep(1, 2)
            except:
                pass # No cookie banner or different text

            # 1. Enter Origin
            # Google Flights usually pre-fills origin based on IP. We might need to clear it or add ours.
            # Finding inputs by aria-label or specific properties is safer.
            
            # This is a heuristic attempt. 
            # We look for the inputs.
            # Often there are multiple text inputs.
            
            # Clicking the "Where from?" box
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            if not inputs:
                 logger.error("Could not find input fields.")
                 return []
            
            # Attempting to interact with the first visible input for Origin
            # Note: This is highly specific to the rendered page and brittle.
            # A more robust way asks the user to provide specific selectors or we use visual AI.
            # For this task, we will try standard interaction.
            
            # Simplified interaction:
            # Just print what we would do if we had stable selectors.
            # Because fully automating Google Flights requires complex waiting and selector handling
            # which might fail in this headless/remote environment without visual feedback.
            
            # HOWEVER, I will try to implement a basic flow.
            
            # Wait, let's look for known placeholders or ARIA labels.
            # 'Where from?' box
            logger.info(f"Searching flights from {origin} to {destination} on {date} (Return: {return_date})")
            
            # This is a demonstration. Real scraping requires maintenance.
            logger.warning("Unstable selectors warning: interacting with Google Flights is complex.")
            
            # Let's fallback to constructing the URL directly, which is muc more robust!
            # URL pattern: https://www.google.com/travel/flights?tfs=...
            # But constructing the 'tfs' string is hard.
            # Simpler URL: https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date}
            # Or formatted: /flights?hl=en&gl=us&curr=USD
            
            # Let's try direct URL navigation which mimics "Search"
            # It's cleaner and "Low Cohesion" (Platform doesn't need to know how to click buttons if it can jump to state).
            # But the prompt said "enter to flight platforms, search with the parameters".
            
            # I'll stick to URL manipulation as it's the professional way to scrape if possible.
            # Correct URL construction
            query = f"Flights from {origin} to {destination} on {date}"
            if return_date:
                query += f" returning on {return_date}"
            
            search_url = f"https://www.google.com/travel/flights?q={query.replace(' ', '+')}"
            self.browser.get_page(search_url)
            
            # Wait for results to load
            logger.info("Waiting for results to load...")
            self.browser.random_sleep(3, 5)
            
            # Extract results
            # Selectors found:
            # Card: li.pIav2d
            # Price: .FpEdX span
            # Airline: .sSHqwe.tPgKwe.ogfYpf span (first one)
            # Duration: .gvkrdb
            # Stops: .EfT7Ae span
            # Layover: .BbR8Ec .sSHqwe

            flights_found = []
            flight_cards = self.driver.find_elements(By.CSS_SELECTOR, "li.pIav2d")
            
            # Limit to top 5 cheapest/best options to avoid spam
            for card in flight_cards[:5]:
                try:
                    data = {}
                    
                    # Price
                    try:
                        price_el = card.find_element(By.CSS_SELECTOR, ".FpEdX span")
                        data['price'] = price_el.text
                    except:
                        data['price'] = "N/A"
                        
                    # Airline
                    try:
                        airline_el = card.find_elements(By.CSS_SELECTOR, ".sSHqwe.tPgKwe.ogfYpf span")
                        if airline_el:
                            data['airline'] = airline_el[0].text
                        else:
                            data['airline'] = "Unknown Airline"
                    except:
                         data['airline'] = "Unknown Airline"

                    # Duration
                    try:
                        duration_el = card.find_element(By.CSS_SELECTOR, ".gvkrdb")
                        data['duration'] = duration_el.text
                    except:
                        data['duration'] = "N/A"
                        
                    # Stops
                    try:
                        stops_el = card.find_element(By.CSS_SELECTOR, ".EfT7Ae span")
                        data['stops'] = stops_el.text
                    except:
                        data['stops'] = "N/A"
                        
                    # Layover (if any)
                    try:
                         layover_el = card.find_element(By.CSS_SELECTOR, ".BbR8Ec .sSHqwe")
                         data['layover'] = layover_el.text
                    except:
                        data['layover'] = None

                    flights_found.append(data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse a flight card: {e}")
                    continue

            return flights_found
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []

