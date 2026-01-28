# Skyscraper - Flight Scraper

Skyscraper is a Python-based flight scraper designed to search for flight prices on Google Flights and notify users via Telegram. It supports both robust server-side scraping via **SerpApi** (recommended) and client-side browser automation.

## Features

- **Reliable Scraping**: Uses **SerpApi** to fetch data directly from Google Flights without browser overhead or stability issues.
- **Multi-Country Search**: Automatically checks flight prices from multiple regions (e.g., UK, US, ES) to find the best currency/regional deals.
- **Browser Fallback**: Intelligent fallback to local browser scraping if no API key is provided.
- **Source Deduplication**: Consolidates identical flights from different sources, showing all regions where the deal was found.
- **Rich Notifications**: Sends Telegram messages with Duration, Stops, Airline, Price (in Euros), and direct links to results.
- **Modular Architecture**: Built with a **Facade** entry point and **Factory Pattern** for easy extensibility.

## Installation

### Prerequisites

- Python 3.10+
- [Conda](https://docs.conda.io/en/latest/) (Recommended)
- Google Chrome (for browser mode)

### Setup

1. **Clone the repository** (if applicable) or navigate to the project folder.

2. **Create the Conda Environment**:

   ```bash
   conda env create -f environment.yml
   ```

3. **Activate Environment**:

   ```bash
   conda activate skyscraper
   ```

4. **Environment Variables**:
   Create a `.env` file with your Telegram credentials:
   ```ini
   TELEGRAM_TOKEN=123456:ABC-DEF...
   CHAT_ID=123456789
   ```

## Usage

Run the scraper using the `main.py` entry point.

### Recommended: SerpApi Mode

Run with your SerpApi key and a list of countries to check from:

```bash
python main.py --origin MAD --destination BRU --date 2026-03-28 --serpapi-key "YOUR_SERPAPI_KEY" --country uk,us,es
```

- `--serpapi-key`: Your SerpApi API Key (Required for this mode).
- `--country`: Comma-separated list of country codes (e.g., `uk,us`) to simulate searching from those locations.

### Fallback: Local Browser Mode

If you **do not provide** a `--serpapi-key`, the script will default to opening a local Google Chrome instance to scrape the data directly.

```bash
python main.py --origin MAD --destination BRU --date 2026-03-28 --headless
```

- `--headless`: Run browser in background (optional).

### Arguments

- `--origin`: City name or 3-letter IATA code (e.g., "London", "LON").
- `--destination`: City name or 3-letter IATA code (e.g., "New York", "NYC").
- `--date`: Date of travel in `YYYY-MM-DD` format.
- `--return-date`: (Optional) Return date in `YYYY-MM-DD` format.
- `--max-price`: (Optional) Filter results above this price.

## Booking Tips

💡 **Pro Tip**: If the scraper finds a cheaper price via a specific country source (e.g., `Found via: SerpApi (ES)`), you should **enable a VPN** set to that country (e.g., Spain) before visiting the airline's website or Google Flights. This ensures you can actually book the flight at the local price detected by the scraper.

## Project Structure

```
skyscraper/
├── config/             # Configuration loader
├── core/               # Core Application Logic
│   ├── application.py  # SkyscraperApp Facade
│   ├── scraper_factory.py # Factory for creating scrapers
│   ├── scraper_runner.py  # Execution engine (SRP compliant)
│   ├── flight_controller.py # Logic controller
│   └── result_aggregator.py # Deduplication logic
├── logger/             # Logging setup
├── notifications/      # Telegram integration
├── scraper/            # Scraper engine
│   ├── platforms/      # Implementations (SerpApi, Google Flights)
│   └── browser.py      # Browser automation
├── utils/              # Helpers (Locations, Parsing)
├── main.py             # Minimal entry point
├── environment.yml     # Dependencies
└── .env                # Secrets
```

## License

[MIT](LICENSE)
