# Skyscraper - Flight Scraper

Skyscraper is a modular, Python-based flight scraper designed to search for flight prices on platforms like Google Flights and notify users via Telegram. It emphasizes strict adherence to the Single Responsibility Principle (SRP) and Low Coupling.

## Features

- **Modular Design**: Separated concerns for Configuration, Logging, Notification, and Scraping.
- **Human Simulation**: Uses Selenium with realistic user-agent headers, screen resolution, and random sleeps to mimic human behavior.
- **Telegram Integration**: Sends text notifications directly to your device.
- **CLI Interface**: Easy-to-use command-line arguments for flexibility.

## Installation

### Prerequisites

- Python 3.10+
- [Conda](https://docs.conda.io/en/latest/) (Recommended)
- Google Chrome installed

### Setup

1. **Clone the repository** (if applicable) or navigate to the project folder.

2. **Create the Conda Environment**:

   ```bash
   conda create -n skyscraper python=3.10 -y
   conda activate skyscraper
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Environment Variables**:
   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`**:
   Open `.env` and add your Telegram Bot Token and Chat ID:
   ```ini
   TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   CHAT_ID=123456789
   ```

## Usage

Run the scraper using the `main.py` entry point. You must provide the origin, destination, and date.

```bash
python main.py --origin LON --destination NYC --date 2026-02-01
```

### Arguments

- `--origin`: 3-letter airport code (e.g., LON, NYC, PAR).
- `--destination`: 3-letter airport code.
- `--date`: Date of travel in YYYY-MM-DD format.
- `--headless`: (Optional) Run the browser in headless mode (no GUI).

### Example with Headless Mode

```bash
python main.py --origin LON --destination NYC --date 2026-02-01 --headless
```

## Project Structure

```
skyscraper/
├── config/             # Configuration loader
├── logger/             # Logging setup
├── notifications/      # Notification services (Telegram)
├── scraper/            # Scraper engine
│   ├── platforms/      # Flight platform implementations (Google Flights, etc.)
│   └── browser.py      # Browser automation manager
├── main.py             # CLI Entry point
├── requirements.txt    # Project dependencies
└── .env                # Secrets (GitIgnored)
```

## License

[MIT](LICENSE)
