import logging
from serpapi import GoogleSearch
from .flight_platform import FlightPlatform
from utils.parsing import parse_price, convert_to_24h

logger = logging.getLogger("skyscraper.platforms.serpapi")

class SerpApiFlights(FlightPlatform):
    """
    Uses SerpApi Google Flights Engine to retrieve flight data.
    """
    def __init__(self, api_key):
        # We don't need a browser for SerpApi
        super().__init__(None)
        self.api_key = api_key

    def search_flights(self, origin, destination, date, return_date=None, country_code="us"):
        """
        Executes search via SerpApi.
        """
        logger.info(f"Searching Flights via SerpApi: {origin} -> {destination} on {date} (Country: {country_code})")
        
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "currency": "EUR", 
            "hl": "en",
            "gl": country_code,
            "api_key": self.api_key,
            "deep_search": "true" 
        }
        
        if return_date:
            params["return_date"] = return_date
        else:
            # Type 2 = One Way (Required if no return_date)
            params["type"] = "2"
            
        # Mask API key for logging safety
        log_params = params.copy()
        log_params["api_key"] = "HIDDEN"
        logger.info(f"SerpApi Request Parameters: {log_params}")

        try:
            search = GoogleSearch(params)
            # We want to access the JSON results
            results = search.get_dict()
            
            # Check for error
            if "error" in results:
                logger.error(f"SerpApi Error: {results['error']}")
                return [], None

            flight_results = []
            
            # SerpApi returns "best_flights" and "other_flights"
            # We combine them or prioritize best
            
            raw_flights = results.get("best_flights", []) + results.get("other_flights", [])
            
            # Limit to top 5 as per user preference (though SerpApi is fast, limit helps processing)
            # Actually user asked to limit output, we can grab all and limit in controller or here.
            # Let's grab all valid ones first then slice.
            
            logger.info(f"SerpApi returned {len(raw_flights)} raw flight options.")
            
            for flight in raw_flights:
                parsed = self._parse_flight(flight)
                if parsed:
                    flight_results.append(parsed)
                    
            # Return limited results (e.g. top 5 or 10, user previously asked for 5)
            # But let's return all and let controller filter/deduplicate? 
            # The previous limit was for "deep linking" click overhead. Here overhead is low.
            # But let's stick to a reasonable number to avoid spam.
            return flight_results, results.get("search_metadata", {}).get("google_flights_url")

        except Exception as e:
            logger.error(f"SerpApi Execution Error: {e}")
            return [], None

    def _parse_flight(self, flight):
        try:
            # Extract main info
            # SerpApi structure varies, usually:
            # { "flights": [...segments...], "price": 123, "airline_logo": ..., "extensions": ... }
            
            # We need to flatten segments to get total duration, stops, airline of first segment
            segments = flight.get("flights_cluster", [flight])[0].get("flights", []) if "flights_cluster" in flight else flight.get("flights", [])
            
            if not segments:
                # Some structures are different
                return None
                
            first_leg = segments[0]
            last_leg = segments[-1]
            
            airline = first_leg.get("airline")
            departure_time = first_leg.get("departure_airport", {}).get("time")
            arrival_time = last_leg.get("arrival_airport", {}).get("time")
            
            # Duration (SerpApi often gives total_duration in minutes)
            total_duration_mins = flight.get("total_duration")
            duration_str = "N/A"
            if total_duration_mins:
                hours = total_duration_mins // 60
                mins = total_duration_mins % 60
                duration_str = f"{hours}h {mins}m"
            
            # Stops
            num_stops = len(segments) - 1
            stops_str = "Nonstop" if num_stops == 0 else f"{num_stops} Stop{'s' if num_stops > 1 else ''}"
            
            # Price (Force EUR formatting)
            price_val = flight.get("price")
            price_str = f"€{price_val}" if price_val else "N/A"
            
            # URL
            # SerpApi doesn't easily give deep links without share_token or detailed search
            # We will use the main Google Flights Results URL as a fallback so the user can click something.
            # This requires passing the search_url down or handling it in the runner?
            # Actually, formatters checks flight['flight_url'].
            # If we don't have a specific one, we can return None here, and the formatter
            # could optionally use the general search_url if passed?
            # But wait, formatters.py doesn't seem to use the 'search_url' arg for individual flight links!
            # It only uses flight.get('flight_url').
            # So we should try to put SOMETHING here.
            
            # Let's see if we can construct a deep link?
            # https://www.google.com/travel/flights?tfs=... is complex.
            # Best bet: check for 'share_token' or 'booking_token' usage?
            # For now, let's leave valid URL as None effectively distinct from N/A?
            # Or better: We can't easily get deep link.
            # But the user asked for URL.
            # Let's look for "google_flights_url" in the SEARCH METADATA (runner has it).
            # We can't access it here easily without refactoring.
            # TEMPORARY FIX: We will modify the runner to inject the main search URL into these results 
            # if specific URL is missing.
            
            return {
                "airline": airline,
                "departure_time": convert_to_24h(departure_time),
                "arrival_time": convert_to_24h(arrival_time),
                "duration": duration_str,
                "stops": stops_str,
                "price": price_str, 
                "price_numeric": price_val, # Helper for sorting if needed
                "flight_url": None # Will be populated by runner with main search URL
            }
        except Exception:
            return None
