def format_flight_results(results: list, origin: str, destination: str, date: str, return_date: str = None, search_url: str = None) -> str:
    """
    Formats flight search results into a rich Telegram message.
    """
    header = f"✈️ *Flight Search Results* ✈️\n"
    header += f"🌍 {origin.title()} ➡️ {destination.title()}\n"
    header += f"📅 {date}"
    if return_date:
        header += f" 🔄 {return_date}"
    header += "\n\n"
    
    body = ""
    for i, flight in enumerate(results, 1):
        price = flight.get('price', 'N/A')
        airline = flight.get('airline', 'Unknown')
        duration = flight.get('duration', 'N/A')
        departure = flight.get('departure_time', 'N/A')
        arrival = flight.get('arrival_time', 'N/A')
        stops = flight.get('stops', 'N/A')
        layover = flight.get('layover')
        
        body += f"🔹 *Option {i}*\n"
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
             body += f"   🔗 [Select Returning Flight]({flight_url})\n"
        
        body += "\n"

    return header + body
