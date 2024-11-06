import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

def create_undetected_headless_driver():
    options = Options()
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    #options.add_argument("--headless")
    options.add_argument("--window-size=1920,1200")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# Initialize driver
driver = create_undetected_headless_driver()

category_urls = {
    "fruits" : "https://groceries.aldi.co.uk/en-GB/fresh-food/fruit?origin=dropdown&c1=groceries&c2=fresh-food&c3=fresh-fruit&clickedon=fresh-fruit"

}

product_box_CSS = '#vueSearchResults > div > div'
product_name_CSS = 'div[class*="product-tile-text"][class*="text-center"][class*="px-3"][class*="mb-3"] > a'
product_price_CSS = 'div[class*="d-flex"][class*="flex-column"][class*="flex-grow-1"][class*="justify-content-end"][class*="px-3"] div[class*="product-tile-price"][class*="text-center"] > div > span > span'
product_price_per_unit_CSS = 'div[class*="d-flex"][class*="flex-column"][class*="flex-grow-1"][class*="justify-content-end"][class*="px-3"] div[class*="product-tile-price"][class*="text-center"] > div > div > p > small > span'
next_button_CSS = 'ul > li.page-item.next.ml-2'
total_pages_CSS = '#vueSearchResults > ul > li:nth-last-child(2) > span'

# List to hold all product data
all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")

# Loop through each category and URL in the category URLs dictionary
for category, url in category_urls.items():
    driver.get(url)
    time.sleep(5)  # Initial wait for page load

    while True:
        # Extract product elements on the current page
        product_boxes = driver.find_elements(By.CSS_SELECTOR, product_box_CSS)

        for product in product_boxes:
            # Extract product name
            product_name = product.find_element(By.CSS_SELECTOR, product_name_CSS).text

            # Check for product price and assign 'null' if price elements are missing
            price_elements = product.find_elements(By.CSS_SELECTOR, product_price_CSS)
            price = price_elements[0].text if price_elements else 'null'

            # Check for price per unit and assign 'null' if price per unit elements are missing
            price_per_unit_elements = product.find_elements(By.CSS_SELECTOR, product_price_per_unit_CSS)
            price_per_unit = price_per_unit_elements[0].text if price_per_unit_elements else 'null'

            # Append the product data to the all_products list
            all_products.append({
                "Name": product_name, 
                "Price": price, 
                "Price per Unit": price_per_unit,
                "Category": category, 
                "Date": current_date
            })

        # Check if there is a "Next" button available and whether it is enabled
        try:
            # Locate the next button using the generalized CSS selector
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, next_button_CSS))
            )
            
            # Check if the next button has the "disabled" class
            if "disabled" in next_button.get_attribute("class"):
                print("Last page reached for category:", category)
                break  # Exit the loop if the button is disabled

            # If not disabled, click the "Next" button to go to the next page
            next_button.click()
            time.sleep(5)  # Wait for the next page to load

        except Exception as e:
            print(f"Error while checking or clicking next button: {e}")
            break  # Exit the loop on any exception

# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
csv_file_path = os.path.join(desktop_path, f"Aldi_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")