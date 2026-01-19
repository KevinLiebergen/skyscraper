
import argparse

def parse_arguments():
    """
    Parses command-line arguments for the Skyscraper application.
    """
    parser = argparse.ArgumentParser(description="Scrape flight prices and notify via Telegram.")
    parser.add_argument("--origin", required=True, help="Flight origin (e.g., LON)")
    parser.add_argument("--destination", required=True, help="Flight destination (e.g., NYC)")
    parser.add_argument("--date", required=True, help="Flight date (YYYY-MM-DD)")
    parser.add_argument("--return-date", help="Return flight date (YYYY-MM-DD). If omitted, searches one-way.")
    parser.add_argument("--max-price", type=float, help="Maximum price filter (e.g., 500)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    return parser.parse_args()
