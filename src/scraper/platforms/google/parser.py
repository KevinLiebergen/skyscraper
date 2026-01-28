
import logging
from utils.parsing import convert_to_24h

logger = logging.getLogger("skyscraper.platforms.google.parser")

class GoogleParser:
    """
    Handles parsing of Google Flights HTML elements.
    """
    def parse_flight_card(self, card_locator):
        """
        Extracts details from a flight card element (Playwright locator).
        """
        data = {}
        
        # Price
        try:
            data['price'] = card_locator.locator(".FpEdX span").inner_text()
        except:
            data['price'] = "N/A"
            
        # Airline
        try:
            # inner_text of the first matching span
            data['airline'] = card_locator.locator(".sSHqwe.tPgKwe.ogfYpf span").first.inner_text()
        except:
                data['airline'] = "Unknown Airline"

        # Duration
        try:
            data['duration'] = card_locator.locator(".gvkrdb").inner_text()
        except:
            data['duration'] = "N/A"
        
        # Departure and Arrival Times
        try:
            times_text = card_locator.locator(".YMlIz").inner_text()
            
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
            data['stops'] = card_locator.locator(".EfT7Ae span").inner_text()
        except:
            data['stops'] = "N/A"
            
        # Layover
        try:
            # Check if element exists before getting text to avoid error on cleaner flow
            layover_loc = card_locator.locator(".BbR8Ec .sSHqwe")
            if layover_loc.count() > 0:
                 data['layover'] = layover_loc.inner_text()
            else:
                 data['layover'] = None
        except:
            data['layover'] = None

        return data
