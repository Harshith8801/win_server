import csv
import os
import time
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# Configure logging with more detailed log files
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
path = "C:/Users/yeera/OneDrive/Desktop/test/scraped_data.csv"

# Path to Firefox binary (install location on your machine)
# Path to Firefox binary (install location on your machine)
firefox_binary_path = r"C:/Program Files/Mozilla Firefox/firefox.exe"  # Update this if Firefox is installed in a different location
geckodriver_path = r"C:/Users/yeera/Downloads/geckodriver-v0.35.0-win64/geckodriver.exe"

# Configure Firefox options
firefox_options = Options()
firefox_options.add_argument("--headless")  # Optional: runs Firefox in headless mode (no GUI)
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--disable-dev-shm-usage")
firefox_options.binary_location = firefox_binary_path  # Set the binary location explicitly

# Check if geckodriver exists
if not os.path.exists(geckodriver_path):
    logger.error(f"Geckodriver not found at {geckodriver_path}. Please check the path.")

# Setup geckodriver and start the Firefox driver
service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=firefox_options)


if not os.path.exists(geckodriver_path):
    logger.error(f"Geckodriver not found at {geckodriver_path}. Please check the path.")

service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=firefox_options)

# Function to load existing CSV data
def load_existing_data(csv_path):
    try:
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                data = list(reader)
                logger.info(f"Loaded existing data from {csv_path}. Total rows: {len(data)}")
                return data
        else:
            logger.info(f"No existing CSV found at {csv_path}. Starting fresh.")
            return []
    except Exception as e:
        logger.error(f"Error loading existing data from {csv_path}: {e}")
        return []

# Function to save data to CSV
def save_to_csv(csv_path, data):
    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        logger.info(f"Data saved to {csv_path}. Total rows: {len(data)}")
    except Exception as e:
        logger.error(f"Error saving data to CSV: {e}")

# Function to add unique data with a limit and sorting
def add_unique_data_with_limit(existing_data, new_data, limit=2000):
    try:
        # Convert existing data to a set of tuples for fast lookup
        existing_set = {tuple(row) for row in existing_data}

        # Filter new data to include only unique rows
        unique_new_data = [row for row in new_data if tuple(row) not in existing_set]

        # Combine the existing data with unique new data
        combined_data = existing_data + unique_new_data

        # Sort the combined data by period in descending order
        sorted_data = sorted(combined_data, key=lambda x: int(x[0]), reverse=True)

        # Trim the data to the specified limit
        trimmed_data = sorted_data[:limit]

        logger.info(f"Data processed: {len(unique_new_data)} new rows added. Total rows after processing: {len(trimmed_data)}")
        return trimmed_data, len(unique_new_data)
    except Exception as e:
        logger.error(f"Error during data processing with limit: {e}")
        return existing_data, 0

# Function to handle the login and navigation process
def login_and_navigate():
    try:
        driver.get("https://okwin.work/#/login")  # Replace with your login URL
        time.sleep(2)

        phone_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Please enter the phone number"]')
        phone_input.send_keys("9684759448")  # Replace with actual phone number

        password_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Password"]')
        password_input.send_keys("numlookup9")  # Replace with actual password

        login_button = driver.find_element(By.CSS_SELECTOR, "button.active")
        login_button.click()
        logger.info("Login completed.")

        time.sleep(5)
        win1_button = driver.find_element(By.CSS_SELECTOR, ".van-button__text")
        win1_button.click()
        logger.info("Navigated to Wingo 1min.")

        try:
            time.sleep(5)
            win2_button = driver.find_element(By.CSS_SELECTOR, "div.close[data-v-9cd12fb2]")
            win2_button.click()
            logger.info("Cancelled pop-up.")
        except Exception as e:
            logger.warning("Pop-up cancellation failed or not found. Proceeding anyway.")

        time.sleep(5)
        element = driver.find_element(By.XPATH, "//div[@class='lotterySlotItem']")
        element.click()
        logger.info("Clicked the element.")

        time.sleep(5)
        win4_button = driver.find_element(By.CSS_SELECTOR, "div.GameList__C-item.active[data-v-17d56002]")
        win4_button.click()
        logger.info("Navigated to Wingo 1min.")

    except Exception as e:
        logger.error(f"Error during login/navigation: {e}")
        driver.quit()

# Function to scrape data and process it
def scrape_pages(csv_path=path, limit=2000):
    page_number = 1

    # Load existing data from the CSV if it exists
    existing_data = load_existing_data(csv_path)

    while True:
        try:
            # Wait for elements dynamically to be present on the page
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".van-col.van-col--9"))
            )

            period_elements = driver.find_elements(By.CSS_SELECTOR, ".van-col.van-col--9")
            outcome_elements = driver.find_elements(By.CSS_SELECTOR, ".van-col.van-col--5")

            filtered_period = [el.text.strip() for el in period_elements if el.text.strip().isdigit()]
            filtered_outcomes = [
                el.text.strip() for el in outcome_elements if re.match(r'(Small|Big)', el.text.strip())
            ]

            logger.info(f"Scraping page {page_number}...")
            logger.info(f"Found {len(filtered_period)} period elements.")
            logger.info(f"Found {len(filtered_outcomes)} outcome elements.")

            # Split outcomes like "Big Small" into separate rows
            new_data = []
            for period, outcome in zip(filtered_period, filtered_outcomes):
                if " " in outcome:  # If the outcome contains both "Big" and "Small"
                    outcomes = outcome.split()
                    for outcome in outcomes:
                        new_data.append([period, outcome])  # Add separate rows for each outcome
                else:
                    new_data.append([period, outcome])  # Normal single outcome row

            # Add only unique new data, maintain limit, and sort
            existing_data, new_rows_added = add_unique_data_with_limit(existing_data, new_data, limit)

            # Save the updated data to CSV
            save_to_csv(csv_path, existing_data)

            logger.info(f"Processed data written to {csv_path}. {new_rows_added} new rows added from page {page_number}.")

            # Navigate to the next page
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".GameRecord__C-foot-next"))
                )
                next_button.click()
                logger.info(f"Navigated to page {page_number + 1}.")
                page_number += 1
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error navigating to the next page: {e}")
                break

        except Exception as e:
            logger.error(f"Error during scraping process: {e}")
            break

    logger.info("Scraping process completed.")

# Main execution
if __name__ == "__main__":
    try:
        csv_path = "C:/Users/yeera/OneDrive/Desktop/test/scraped_data.csv"  # Define the path to your CSV file

        login_and_navigate()  # Login and navigate to the desired page
        scrape_pages(csv_path, limit=2000)  # Perform scraping with a 2000 record limit

    except Exception as e:
        logger.error(f"Unexpected error during execution: {e}")

    finally:
        # Close the driver
        driver.quit()
        logger.info("Script execution completed.")
