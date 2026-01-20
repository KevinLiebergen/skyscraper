
import logging
from selenium.webdriver.common.by import By
from utils.parsing import convert_to_24h

logger = logging.getLogger("skyscraper.platforms.google.parser")

class GoogleParser:
    """
    Handles parsing of Google Flights HTML elements.
    """
    def parse_flight_card(self, card):
        """
        Extracts details from a flight card element.
        """
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
        
        # Departure and Arrival Times
        try:
            times_el = card.find_element(By.CSS_SELECTOR, ".YMlIz")
            times_text = times_el.text 
            
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
            stops_el = card.find_element(By.CSS_SELECTOR, ".EfT7Ae span")
            data['stops'] = stops_el.text
        except:
            data['stops'] = "N/A"
            
        # Layover
        try:
                layover_el = card.find_element(By.CSS_SELECTOR, ".BbR8Ec .sSHqwe")
                data['layover'] = layover_el.text
        except:
            data['layover'] = None

        return data
