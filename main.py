import pandas as pd
import boto3
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime

from utils import create_dateframe

df = create_dateframe(n_years = 2, format = '%b %d, %Y')

os.makedirs("data", exist_ok=True)

for row in df.itertuples():
    effective_date = row[1]
    to_date = row[2]
 

    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Run Chrome in headless mode

    # Create the Chrome driver with the specified options
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the website
    driver.get("https://laatcabc.atc.la.gov/laatcprod/pub/Default.aspx?PossePresentation=LicenseSearch")

    # Find and set the value for the "Effective Date" field
    effective_date_input = driver.find_element(By.ID, "EffectiveDate_1535033_S0")
    effective_date_input.clear()
    effective_date_input.send_keys(f"{effective_date}")  # Update with the desired date format
    effective_date = datetime.strptime(effective_date_input.get_attribute("value"), "%b %d, %Y").strftime("%Y%m%d")  # Get the effective date value

    # Find and set the value for the "To" field
    to_input = driver.find_element(By.ID, "EffectiveDateTo_1535033_S0")
    to_input.clear()
    to_input.send_keys(f"{to_date}")  # Update with the desired date format
    to_date = datetime.strptime(to_input.get_attribute("value"), "%b %d, %Y").strftime("%Y%m%d")  # Get the to date value


    # Click the "Search" button
    search_button = driver.find_element(By.ID, "cphBottomFunctionBand_ctl03_PerformSearch")
    search_button.click()

    # Get the page source
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Create BeautifulSoup object for parsing the HTML
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all the table cells in the search results
    table_cells = soup.find_all("td")

    # Save the table cells as a text file
    table_cells_filename = "data/table_cells.txt"
    with open(table_cells_filename, "w") as file:
        for cell in table_cells:
            file.write(cell.text.strip() + "\n")

    print("Table cells saved as", table_cells_filename)

    # Open the file and read its contents as a string
    with open(table_cells_filename, "r") as file:
        file_content = file.read()

    # Split the data into individual records
    records = file_content.strip().split("\n\n\n")

    # Adjusted records
    adjusted_records = [i.strip().split("\n") for i in records]

    # Create a DataFrame from the adjusted records
    df = pd.DataFrame(adjusted_records)

    columns = ['License Number',
            'License Type',
            'Alcohol Content',
            'Licensee',
            'Street Address',
            'City State Zip',
            'License Status',
            'Effective Date',
            'Inactive Date',
            'Expiration Date']

    df.columns = columns

    df.dropna(inplace=True)

    # Save the DataFrame as a CSV file
    csv_filename = f"la_licenses_{effective_date}_{to_date}.parquet"
    df.to_parquet(csv_filename, index=False)

    # Upload the CSV file to Amazon S3
    s3_bucket_name = os.environ['S3_BUCKET_NAME']  # Replace with your S3 bucket name
    s3_folder_name = os.path.splitext(os.path.basename(__file__))[0]  # Use script name as folder name
    s3_key = f"alcohol_license_{s3_folder_name}/{csv_filename}"
    s3_client = boto3.client("s3")
    s3_client.upload_file(csv_filename, s3_bucket_name, s3_key)
