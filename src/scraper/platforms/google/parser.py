
import logging
from selenium.webdriver.common.by import By
from utils.parsing import convert_to_24h

logger = logging.getLogger("skyscraper.platforms.google.parser")

class GoogleParser:
    """
    Handles parsing of Google Flights HTML elements.
    """
    def parse_flight_card(self, card_element):
        """
        Extracts details from a flight card element (Selenium WebElement).
        """
        data = {}
        
        # Price
        try:
            data['price'] = card_element.find_element(By.CSS_SELECTOR, ".FpEdX span").text
        except:
            data['price'] = "N/A"
            
        # Airline
        try:
            # text of the first matching span
            # Using find_elements to simulate .first and avoid error if not found immediately
            airlines = card_element.find_elements(By.CSS_SELECTOR, ".sSHqwe.tPgKwe.ogfYpf span")
            if airlines:
                data['airline'] = airlines[0].text
            else:
                data['airline'] = "Unknown Airline"
        except:
                data['airline'] = "Unknown Airline"

        # Duration
        try:
            data['duration'] = card_element.find_element(By.CSS_SELECTOR, ".gvkrdb").text
        except:
            data['duration'] = "N/A"
        
        # Departure and Arrival Times
        try:
            times_text = card_element.find_element(By.CSS_SELECTOR, ".YMlIz").text
            
            if "–" in times_text:
                dep, arr = times_text.split("–", 1)
                data['departure_time'] = convert_to_24h(dep)
                data['arrival_time'] = convert_to_24h(arr)
            else:
                data['departure_time'] = convert_to_24h(times_text)
                data['arrival_time'] = "?"
        except:
            data['departure_time'] = "N/A"
            data['arrival_time'] = "N/A"

        # Stops
        try:
            data['stops'] = card_element.find_element(By.CSS_SELECTOR, ".EfT7Ae span").text
        except:
            data['stops'] = "N/A"
            
        # Layover
        try:
            # Check if element exists
            layovers = card_element.find_elements(By.CSS_SELECTOR, ".BbR8Ec .sSHqwe")
            if layovers:
                 data['layover'] = layovers[0].text
            else:
                 data['layover'] = None
        except:
            data['layover'] = None

        return data
