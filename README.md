# Skyscraper - Flight Scraper

Skyscraper is a Python-based flight scraper designed to search for flight prices on platforms like Google Flights and notify users via Telegram.

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
   conda env create -f environment.yml
   ```

3. **Activate Environment**:
   ```bash
   conda activate skyscraper
   ```

## Configuration

1. **Environment Variables**:
   Create a `.env` file (see `.env.example` if available, or create one):

   ```bash
   touch .env
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
python main.py --origin London --destination "New York" --date 2026-02-01
```

### Arguments

- `--origin`: City name or 3-letter IATA code (e.g., "London", "LON").
- `--destination`: City name or 3-letter IATA code (e.g., "New York", "NYC").
- `--date`: Date of travel in YYYY-MM-DD format.
- `--return-date`: (Optional) Return date in YYYY-MM-DD format for round trips.
- `--headless`: (Optional) Run the browser in headless mode (no GUI).

### Example with Return Date and Headless Mode

```bash
python main.py --origin London --destination "New York" --date 2026-02-01 --return-date 2026-02-15 --headless
```

## Automation (Crontab)

To run the scraper automatically on a schedule (e.g., every 6 hours), you can use `cron`.

1.  Open your crontab editor:

    ```bash
    crontab -e
    ```

2.  Add a line to schedule the script. The following example runs every 6 hours and logs output to `cron.log`:

    ```bash
    # Run every 6 hours (00:00, 06:00, 12:00, 18:00)
    0 */6 * * * cd /home/kevinvanliebergen/git/skyscraper && /opt/conda/envs/skyscraper/bin/python main.py --origin London --destination "New York" --date 2026-02-01 --return-date 2026-02-15 --headless --max-price 600 >> cron.log 2>&1
    ```

    **Important Notes:**

    - **Absolute Paths**: Always use absolute paths for both `cd` and the `python` executable.
    - **Python Executable**: Use the python executable from your conda environment. You can find it by running `conda run -n skyscraper which python`.
    - **Display**: Since it runs headless, you generally don't need to set `DISPLAY`, but if you face issues, ensure `--headless` is used.

## Project Structure

```
skyscraper/
├── config/             # Configuration loader
├── logger/             # Logging setup
├── notifications/      # Notification services (Telegram)
│   ├── formatters.py   # Message formatting
│   └── telegram.py     # Telegram API integration
├── scraper/            # Scraper engine
│   ├── platforms/      # Flight platform implementations (Google Flights, etc.)
│   └── browser.py      # Browser automation manager
├── utils/              # Utility helper functions
│   └── locations.py    # City to IATA code conversion
├── main.py             # CLI Entry point
├── environment.yml     # Conda environment definition
└── .env                # Secrets (GitIgnored)
```

## License

[MIT](LICENSE)
