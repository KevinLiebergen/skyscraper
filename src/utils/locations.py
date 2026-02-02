import airportsdata
import logging

logger = logging.getLogger("skyscraper.utils.locations")

class FlightLocationHandler:
    def __init__(self):
        self.airports = airportsdata.load('IATA')
        self._city_map = self._build_city_map()

    def _build_city_map(self):
        """
        Builds a mapping of City Name -> IATA Code.
        Prioritizes major airports or city codes if available.
        """
        city_map = {}
        for code, data in self.airports.items():
            city = data.get('city')
            if not city:
                continue
            
            city_lower = city.lower()
            
            # Simple heuristic: If multiple airports, usually one is the 'main' one or we store a list.
            # But the requirement is simple ID.
            # Ideally we want the "City Code" which airportsdata might not explicitly segregate for all.
            # For now, we map the city name to the airport code. 
            # If a city has multiple airports, the last one loaded overwrites (not ideal).
            
            # Improvement: Prefer airports with longer runways or simply store the first one found?
            # Or better: check if the IATA code matches the City name pattern?
            
            # Actually, `airportsdata` doesn't strictly have a "City IATA".
            # But mostly: London -> LHR, LGW. 
            # We want London -> LON.
            # Unfortunately, LON is a "Metro Code". 
            # Some airports have `iata` but the city code is different.

            # Heuristic: We map City -> [List of Codes].
            if city_lower not in city_map:
                city_map[city_lower] = []
            city_map[city_lower].append(code)
            
        return city_map

    def get_iata_code(self, city_name: str) -> str:
        """
        Returns the IATA code for a city.
        If multiple airports exist, returns the first one (or a Metro code if we could derive it).
        """
        if not city_name:
            return None
            
        # Check if input is already 3 letters uppercased - assume IATA
        if len(city_name) == 3 and city_name.isalpha():
            return city_name.upper()

        matches = self._city_map.get(city_name.lower())
        if matches:
            # If we have matches, which one to pick?
            # Example: London -> [LHR, LGW, LCY...]
            # Google Flights accepts 'LON' for 'all airports'.
            # We don't have 'LON' in our airport list usually (it's a pseudo-airport).
            
            # HARDCODED COMMON METRO CODES for better UX
            # If strict "Efficient way" is requested, a predefined map of top 50 cities is fastest.
            # But falling back to airport code is safe.
            
            # Hardcoded overrides for major multi-airport cities
            MAJOR_CITIES = {
                "london": "LON",
                "new york": "NYC",
                "paris": "PAR",
                "moscow": "MOW",
                "tokyo": "TYO",
                "rome": "ROM",
                "milan": "MIL",
                "buenos aires": "BUE",
                "sao paulo": "SAO",
                "rio de janeiro": "RIO",
                "washington": "WAS",
                "san francisco": "SFO", # SFO is often used for the area too
                "los angeles": "LAX", # LAX is often used
                "chicago": "CHI",
                "lima": "LIM",
            }
            
            if city_name.lower() in MAJOR_CITIES:
                return MAJOR_CITIES[city_name.lower()]

            return matches[0] # Return the first found airport
            
        logger.warning(f"Could not find IATA code for city: {city_name}")
        return city_name # Fallback to original name, Google Flights handles it.
