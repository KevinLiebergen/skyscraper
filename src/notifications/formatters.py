from datetime import datetime

def format_flight_results(results: list, origin: str, destination: str, date: str, return_date: str = None, search_url: str = None) -> str:
    """
    Formats flight search results into a rich Telegram message.
    """
    header = _format_header(origin, destination, date, return_date)
    
    body = ""
    for i, flight in enumerate(results, 1):
        body += _format_flight_option(i, flight, return_date)
        body += "\n"

    return header + body

def _format_date_with_day(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_str} ({dt.strftime('%A')})"
    except ValueError:
        return date_str

def _format_header(origin, destination, date, return_date):
    formatted_date = _format_date_with_day(date)
    
    header = f"✈️ *Flight Search Results* ✈️\n"
    header += f"🌍 {origin.title()} ➡️ {destination.title()}\n"
    header += f"📅 {formatted_date}"
    if return_date:
        formatted_return = _format_date_with_day(return_date)
        header += f" 🔄 {formatted_return}"
    header += "\n\n"
    return header

def _format_flight_option(index, flight, return_date):
    price = flight.get('price', 'N/A')
    airline = flight.get('airline', 'Unknown')
    duration = flight.get('duration', 'N/A')
    departure = flight.get('departure_time', 'N/A')
    arrival = flight.get('arrival_time', 'N/A')
    stops = flight.get('stops', 'N/A')
    layover = flight.get('layover')
    
    body = f"🔹 *Option {index}*\n"
    if return_date:
        body += f"   🛫 *Outbound Flight*\n"
    body += f"   💰 {'Total Price (Round Trip)' if return_date else 'Price'}: {price}\n"
    body += f"   🏢 Airline: {airline}\n"
    body += f"   🛫 Depart: {departure}\n"
    body += f"   🛬 Arrive: {arrival}\n"
    body += f"   ⏱️ Duration: {duration}\n"
    
    if stops and ("Nonstop" in stops or "0" in stops):
            body += f"   🚀 Stops: Nonstop\n"
    else:
            body += f"   🛑 Stops: {stops}\n"
            
    if layover:
        body += f"   ⏳ Layover: {layover}\n"
        
    flight_url = flight.get('flight_url')
    if flight_url:
            link_text = "Select Returning Flight" if return_date else "Select Flight"
            body += f"   🔗 [{link_text}]({flight_url})\n"
    
    source = flight.get('source')
    if source:
            body += f"   🌐 Found via: {source}\n"
            
    return body
