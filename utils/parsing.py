import re

def parse_price(price_str: str) -> float:
    """
    Parses a price string (e.g., "$1,234.50", "€ 400") into a float.
    Returns None if parsing fails.
    """
    if not price_str or price_str == "N/A":
        return None
        
    # Remove standard non-numeric chars except dot and comma
    # We assume standard western format usually.
    # Regex to find the first number.
    # Handles 1,234.56 or 1.234,56 logic roughly by being permissive
    # For now, simplistic extraction of digits and dots.
    
    # 1. Remove currency symbols and spaces
    clean_str = re.sub(r'[^\d.,]', '', price_str)
    
    # 2. Normalize decimal separator
    # If comma is used as decimal (e.g. 1.000,00), python float expects dot.
    # Heuristic: if comma is after dot, or only comma exists and it's near end
    
    if not clean_str:
        return None

    try:
        # Simple replace comma with nothing if it's thousands sep?
        # Robust way: ignore formatting, just find the number
        # If string is "1,234", float("1234") works. 
        # If "12.34", float("12.34").
        
        # Let's clean standard commas if they are thousands separators
        if "," in clean_str and "." in clean_str:
            if clean_str.find(",") < clean_str.find("."):
                 # 1,234.56
                 clean_str = clean_str.replace(",", "")
            else:
                 # 1.234,56 -> 1234.56
                 clean_str = clean_str.replace(".", "").replace(",", ".")
        elif "," in clean_str:
             # 123,45 or 1,234
             # If comma is 3 chars from end, maybe decimal? 
             # Usually prices have 2 decimals.
             # but "1,234" is integer 1234. 
             # Let's assume input from Google Flights is fairly standard.
             # usually it's local format.
             
             # Fallback to simple regex finding float
             pass 
             
        # Just use a simple regex to grab the number block
        # This handles "1234" "1234.56"
        # It fails on "1,234" unless we strip commas.
        
        # Simpler approach: Keep only digits and dots/commas
        # Then replace ',' with '.' if it acts as decimal?
        
        # Let's assume US/EU major formats. 
        # Remove all commas, they are usually thousands separators in English 
        # OR replace them if they are decimals.
        
        # Safest bet for scraping: remove all non-digits, divide by 100? No.
        
        # Final Strategy: 
        # Filter everything but numbers, commas, dots.
        # If ',' detected as thousands (followed by 3 digits), remove it.
        
        sanitized = clean_str.replace(',', '') # Assume comma is thousands sep for now or just ignore decimals if integer
        # If it was 12,50 it becomes 1250 which is wrong.
        
        # Better:
        # Google Flights usually outputs local currency format.
        # e.g., €483 -> 483
        
        # Let's try to just extract the first contiguous number.
        match = re.search(r"([\d\.,]+)", price_str)
        if match:
             num_str = match.group(1)
             # removing thousands separators. 
             # If we have 1,234.00 -> 1234.00
             # If we have 1.234,00 -> 1234.00
             
             if ',' in num_str and '.' in num_str:
                  if num_str.find(',') < num_str.find('.'):
                      num_str = num_str.replace(',', '') 
                  else:
                      num_str = num_str.replace('.', '').replace(',', '.')
             elif ',' in num_str:
                  # ambiguous: 1,000 (1k) or 10,50 (10.5)
                  # If 3 digits after comma, assume thousands
                  parts = num_str.split(',')
                  if len(parts[-1]) == 3:
                       num_str = num_str.replace(',', '')
                  else:
                       num_str = num_str.replace(',', '.')
             
             return float(num_str)
             
        return None
    except:
        return None
