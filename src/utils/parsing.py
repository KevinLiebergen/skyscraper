from datetime import datetime
import re

def parse_price(price_str: str) -> float:
    """
    Parses a price string (e.g., "$1,234.50", "€ 400") into a float.
    Returns None if parsing fails.
    """
    if not price_str or price_str == "N/A":
        return None
        
    # Remove standard non-numeric chars except dot and comma
    clean_str = re.sub(r'[^\d.,]', '', price_str)
    
    if not clean_str:
        return None

    try:
        # Heuristic approach for parsing numbers with diverse separators
        match = re.search(r"([\d\.,]+)", price_str)
        if match:
             num_str = match.group(1)
             
             if ',' in num_str and '.' in num_str:
                  if num_str.find(',') < num_str.find('.'):
                      num_str = num_str.replace(',', '') 
                  else:
                      num_str = num_str.replace('.', '').replace(',', '.')
             elif ',' in num_str:
                  parts = num_str.split(',')
                  if len(parts[-1]) == 3:
                       num_str = num_str.replace(',', '')
                  else:
                       num_str = num_str.replace(',', '.')
             
             return float(num_str)
             
        return None
    except:
        return None

def parse_stops(stops_str: str) -> int:
    """
    Parses a stops string (e.g., "Nonstop", "1 Stop", "2 Stops") into an integer.
    Returns None if it can't be determined.
    """
    if not stops_str or stops_str == "N/A":
        return None

    if "Nonstop" in stops_str:
        return 0

    match = re.search(r'\d+', stops_str)
    if match:
        return int(match.group())

    return None

def convert_to_24h(time_str: str) -> str:
    """
    Converts 12-hour AM/PM time string to 24-hour format.
    Examples:
    "2:00 PM" -> "14:00"
    "10:00 AM" -> "10:00"
    "14:00" -> "14:00"
    """
    if not time_str or time_str == "N/A" or time_str == "?":
        return time_str

    time_str = time_str.strip()

    # Strip a leading "YYYY-MM-DD " date prefix (e.g. SerpApi's "2026-10-30 12:25")
    # since the date is already shown separately in the notification.
    time_str = re.sub(r'^\d{4}-\d{2}-\d{2}\s+', '', time_str).strip()

    # Check if already in 24h-like format (HH:MM without AM/PM)
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        return time_str

    try:
        # Try parsing standard formats
        # Using %I for 12-hour, %p for AM/PM
        # Note: Google Flights might output "2:00 pm" or "2:00 PM"
        # Or sometimes contains +1 (next day) e.g. "10:00 PM+1"
        
        # Strip potential +N day indicator for parsing
        clean_time = re.sub(r'\+\d+', '', time_str).strip()
        
        dt = datetime.strptime(clean_time, "%I:%M %p")
        formatted = dt.strftime("%H:%M")
        
        # Append back the +1 if it existed
        if "+" in time_str:
            formatted += time_str[time_str.find("+"):]
            
        return formatted
    except ValueError:
        # If standard parsing fails, might be just hour? "2 PM"
        try:
             clean_time = re.sub(r'\+\d+', '', time_str).strip()
             dt = datetime.strptime(clean_time, "%I %p")
             formatted = dt.strftime("%H:%M")
             if "+" in time_str:
                formatted += time_str[time_str.find("+"):]
             return formatted
        except:
             return time_str
