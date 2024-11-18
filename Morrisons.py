import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
from datetime import datetime
import random
from random import randint

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
    accept_cookies_button_CSS = '#onetrust-accept-btn-handler'

    driver.get("https://groceries.morrisons.com/")
    time.sleep(3)
    # Wait for and accept the cookies pop-up (if it appears)
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, accept_cookies_button_CSS))
        )
        accept_button.click()
        print("Cookies accepted.")
        time.sleep(2)  # Wait a bit after accepting cookies
    except Exception as e:
        print("No cookies on this page :) ")


    return driver

driver = create_undetected_headless_driver()

category_urls = {
    'fruit': ['https://groceries.morrisons.com/categories/fruit-veg/fruit/bc58fa02-e8fa-4ecb-a6fc-f273c3661239?source=navigation']
}

product_box_CSS = '#product-page > div._grid_vea1m_1._grid--flush_vea1m_24 > div._grid-item-12_tilop_45._grid-item-lg-10_tilop_273 > div > div.sc-6514kr-0.laInAo > div:not([class*="sc-6514kr-1"]):not([class*="sc-eDPEul"])'
product_name_CSS = 'div.footer-container > div[class*="sc-mmemlz"] > div.title-container > a > h3'
product_price_CSS = 'div.footer-container > div[class*="sc-mmemlz"] > div.price-pack-size-container > div > span[class*="_text"]'
product_price_per_unit_CSS = 'div.footer-container > div[class*="sc-mmemlz"] > div.sc-e95yj7-0.CvvRP > span[class*="_text"]:not([class*="asqfi"])'

all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")

def scroll_to_load(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

for category, urls in category_urls.items():
    for url in urls:
        driver.get(url)
        time.sleep(5)  # Wait for initial page load

        prev_product_count = 0
        last_page_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            try:
                product_boxes = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, product_box_CSS))
                )
            except Exception as e:
                print(f"Error waiting for product boxes: {e}")
                break

            if not product_boxes:
                print("No more product boxes found. End of page.")
                break

            for product in product_boxes:
                # Scrape product name, price, and price per unit
                product_name = product.find_element(By.CSS_SELECTOR, product_name_CSS).text if product.find_elements(By.CSS_SELECTOR, product_name_CSS) else 'null'
                price = product.find_element(By.CSS_SELECTOR, product_price_CSS).text if product.find_elements(By.CSS_SELECTOR, product_price_CSS) else 'null'
                price_per_unit = product.find_element(By.CSS_SELECTOR, product_price_per_unit_CSS).text if product.find_elements(By.CSS_SELECTOR, product_price_per_unit_CSS) else 'null'

                all_products.append({
                    "Name": product_name,
                    "Price": price,
                    "Price per Unit": price_per_unit,
                    "Category": category,
                    "Date": current_date
                })

            # Scroll the page or specific container
            new_page_height = driver.execute_script("return document.body.scrollHeight")
            if new_page_height == last_page_height:
                print("No new products loaded. Reached the end of the page.")
                break
            else:
                last_page_height = new_page_height

            # Scroll action (for entire page or specific container)
            try:
                driver.execute_script("window.scrollBy(0, 1000);")  # Scroll by fixed amount
                time.sleep(random.randint(3, 5))  # Random sleep to simulate human-like behavior
            except Exception as e:
                print(f"Error scrolling page: {e}")
                break
           

# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
csv_file_path = os.path.join(desktop_path, f"Morrisons_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")