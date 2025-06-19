from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
import time
from datetime import datetime
import argparse
import os

def scrape_bitcoin_treasuries():
    """
    Scrapes Bitcoin Treasuries category data from bitbo.io/treasuries/
    Returns a list of category data
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Set binary location for GitHub Actions
    if os.path.exists('/usr/bin/chromium-browser'):
        chrome_options.binary_location = '/usr/bin/chromium-browser'
    elif os.path.exists('/usr/bin/chromium'):
        chrome_options.binary_location = '/usr/bin/chromium'

    # Initialize the driver with service
    service = Service()
    driver = webdriver.Chrome(options=chrome_options, service=service)
    
    try:
        # Navigate to the website
        driver.get('https://bitbo.io/treasuries/')
        
        # Wait for tables to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Get all tables
        tables = driver.find_elements(By.TAG_NAME, "table")
        
        # Get category totals (looking for table with "Category" in first column header)
        category_data = {}
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        category_data['timestamp'] = timestamp
        
        for table in tables:
            headers = table.find_elements(By.TAG_NAME, "th")
            if headers and "Category" in headers[0].text:
                category_rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
                for row in category_rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 3:  # Ensure we have enough columns
                        category = cols[0].text.strip()
                        if "/treasuries/" in category:  # Extract category name from link text
                            category = category.split("/treasuries/")[0].strip()
                        category = category.replace('[', '').replace(']', '')  # Remove [] from category names
                        # Only store BTC holdings, removing commas
                        btc_amount = cols[1].text.strip().replace(',', '')  # Remove commas from numbers
                        
                        # Clean up category name for column header
                        category_key = category.replace(' ', '_').lower()
                        category_data[category_key] = btc_amount
                
                break  # Found and processed the category table, exit loop
        
        return category_data
    
    finally:
        driver.quit()

def save_to_csv(data, filename='category_btc-treasuries.csv'):
    """
    Saves or appends the data to a CSV file with timestamp as first column
    and categories as subsequent columns
    """
    # Define the field order (timestamp first, then other fields alphabetically)
    fields = ['timestamp'] + sorted([field for field in data.keys() if field != 'timestamp'])
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        
        # Write headers only if file is new
        if not file_exists:
            writer.writeheader()
        
        # Write the data row
        writer.writerow(data)
    
    print(f"Data appended to {filename}")
    return fields

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape Bitcoin Treasuries category data')
    parser.add_argument('--output', '-o', 
                       default='category_btc-treasuries.csv',
                       help='Output CSV filename (default: category_btc-treasuries.csv)')
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        print("Scraping category data from bitbo.io/treasuries/...")
        category_data = scrape_bitcoin_treasuries()
        
        # Save category data
        fields = save_to_csv(category_data, args.output)
        print(f"Saved data with {len(fields)-1} categories")  # -1 to exclude timestamp
        
        # Display the current entry
        print("\nLatest entry:")
        for field in fields:
            print(f"{field}: {category_data.get(field, 'N/A')}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 