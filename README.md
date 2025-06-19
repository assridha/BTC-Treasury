# Bitcoin Treasury Scraper

This project automatically scrapes Bitcoin Treasury data from bitbo.io/treasuries/ on a daily basis. The data is stored in a CSV file and automatically updated through GitHub Actions.

## Data

The scraped data is stored in `category_btc-treasuries.csv` and is updated daily at 00:00 UTC.

## Automation

The scraping is automated using GitHub Actions, which:
1. Runs the script daily at 00:00 UTC
2. Uses Selenium with headless Chrome to scrape the data
3. Commits any changes back to the repository

## Local Development

To run the scraper locally:

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install selenium`
5. Run the scraper: `python treasury_scraper.py`

## Requirements

- Python 3.x
- Selenium
- Chrome/Chromium browser 