
import argparse
from datetime import datetime

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: '{s}'. Expected format: YYYY-MM-DD")

def parse_arguments():
    """
    Parses command-line arguments for the Skyscraper application.
    """
    parser = argparse.ArgumentParser(description="Scrape flight prices and notify via Telegram.")
    parser.add_argument("--origin", required=True, help="Flight origin (e.g., LON)")
    parser.add_argument("--destination", required=True, help="Flight destination (e.g., NYC)")
    parser.add_argument("--date", required=True, type=valid_date, help="Flight date (YYYY-MM-DD)")
    parser.add_argument("--return-date", type=valid_date, help="Return flight date (YYYY-MM-DD). If omitted, searches one-way.")
    parser.add_argument("--max-price", type=float, help="Maximum price filter (e.g., 500)")
    parser.add_argument("--serpapi-key", required=True, help="SerpApi Key (Required)")
    parser.add_argument("--country", help="Country code(s) for search location (e.g., us, uk). Comma-separated.")
    
    return parser.parse_args()
