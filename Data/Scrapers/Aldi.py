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
    accept_cookies_button_CSS = '#onetrust-accept-btn-handler'

    driver.get("https://groceries.aldi.co.uk/en-GB/fresh-food")
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

# Initialize driver
driver = create_undetected_headless_driver()

category_urls = {
    
    "fresh_food": {
    "fruits" : "https://www.aldi.co.uk/products/fresh-food/fruit/k/1588161416978050001",
    "vegetables": "https://www.aldi.co.uk/products/fresh-food/vegetables/k/1588161416978050002",
    "fresh_food_vegan": "https://www.aldi.co.uk/products/vegetarian-plant-based/chilled-vegetarian/k/1588161421881163002",
    "fresh_food_vegan": "https://www.aldi.co.uk/products/vegetarian-plant-based/chilled-vegan/k/1588161421881163004",
    "milk_butter_eggs": "https://www.aldi.co.uk/products/chilled-food/milk/k/1588161416978051001",
    "milk_butter_eggs": "https://www.aldi.co.uk/products/chilled-food/eggs/k/1588161416978051003",
    "milk_butter_eggs": "https://www.aldi.co.uk/results?q=Butter",
    "cheese": "https://www.aldi.co.uk/products/chilled-food/cheese/k/1588161416978051004",
    "yogurts": "https://www.aldi.co.uk/results?q=Yogurt",
    "meat_poultry": "https://www.aldi.co.uk/results?q=Meat",

    "seafood": "https://www.aldi.co.uk/products/fresh-food/fish/k/1588161416978050011",
    "party_food_salads_dips": "https://www.aldi.co.uk/products/chilled-food/party-food-pies-salads/k/1588161416978051012",
    "chilled_desserts": "https://www.aldi.co.uk/products/chilled-food/chilled-desserts/k/1588161416978051006",
    "pizza_pasta_gbread": "https://www.aldi.co.uk/products/frozen-food/pizzas-garlic-bread/k/1588161416978056006",
    "chilled_meats": "https://www.aldi.co.uk/products/chilled-food/chilled-meats/k/1588161416978051011",
    },

    "bakery": {
    "bakery" : "https://www.aldi.co.uk/products/bakery/k/1588161416978049",
    },

    "frozen":{ 
    "frozen_vegetarian": "https://www.aldi.co.uk/products/vegetarian-plant-based/frozen-vegetarian/k/1588161421881163003",
    "frozen_vegtables": "https://www.aldi.co.uk/products/frozen-food/vegetables-sides/k/1588161416978056004",
    "chips_related": "https://www.aldi.co.uk/products/frozen-food/chips-potato/k/1588161416978056003",
    "frozen_meat_poultry": "https://www.aldi.co.uk/products/frozen-food/meat-poultry/k/1588161416978056001",
    "frozen_seafood": "https://www.aldi.co.uk/products/frozen-food/fish-seafood/k/1588161416978056002",
    "frozen_pizza": "https://www.aldi.co.uk/products/frozen-food/pizzas-garlic-bread/k/1588161416978056006",
    "frozen_desserts_icecream": "https://www.aldi.co.uk/products/frozen-food/ice-cream-desserts/k/1588161416978056009",
    "frozen_fruit": "https://www.aldi.co.uk/products/frozen-food/fruit-smoothies/k/1588161416978056008",
    },

    "cupboard": {
    "treats": "https://www.aldi.co.uk/products/food-cupboard/chocolate-sweets/k/1588161416978053003",
    "snacks": "https://www.aldi.co.uk/products/food-cupboard/crisps-snacks/k/1588161416978053004",
    "seed_nuts": "https://www.aldi.co.uk/products/food-cupboard/seeds-nuts-dried-fruits/k/1588161416978053009",
    "cereals": "https://www.aldi.co.uk/results?q=Cereal",
    "canned": "https://www.aldi.co.uk/results?q=Canned",
    "carbs": "https://www.aldi.co.uk/results?q=Rice",
    "carbs": "https://www.aldi.co.uk/results?q=Pasta",
    "sauce": "https://www.aldi.co.uk/results?q=Sauce",
    "spread_jam": "https://www.aldi.co.uk/products/food-cupboard/jams-spreads-syrups/k/1588161416978053006",
    },
    "drinks": {
    "soft_drink": "https://www.aldi.co.uk/products/drinks/soft-drinks-juices/k/1588161416978054004",
    "water": "https://www.aldi.co.uk/results?q=Water",
    "milk": "https://www.aldi.co.uk/results?q=Milk",
    "tea": "https://www.aldi.co.uk/results?q=Tea",
    "coffee": "https://www.aldi.co.uk/products/drinks/coffee/k/1588161416978054002",
    "beer_cider": "https://www.aldi.co.uk/products/alcohol/beers-ciders/k/1588161416978055001",
    "spirit": "https://www.aldi.co.uk/products/alcohol/spirits-liqueurs/k/1588161416978055002",
    "wine": "https://www.aldi.co.uk/results?q=Wine"
    }
}

product_box_CSS = 'div.product-listing-viewer__product-list-content [id^="product-tile-"]'
product_name_CSS = '[id^="product-tile-"] > div > a > div.product-tile__name > p'
product_price_CSS = '[id^="product-tile-"] > div > a > div.base-price.product-tile__price > div > span.base-price__regular > span'
product_price_per_unit_CSS = '[id^="product-tile-"] > div > a > div.base-price.product-tile__price > div > span.base-price__comparison-price'
next_button_CSS = 'a.base-pagination__arrow[aria-label="Next"]'

# List to hold all product data
all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")

# Loop through each category and URL in the category URLs dictionary
for main_category, subcategories in category_urls.items():
    for subcategory, url in subcategories.items():
        driver.get(url)
        time.sleep(5)  # Initial wait for page load

        while True:
            # Re-fetch product boxes each iteration to avoid stale elements
            product_boxes = driver.find_elements(By.CSS_SELECTOR, product_box_CSS)

            for product in product_boxes:
                try:
                    # Re-locate elements inside the loop to ensure they are fresh
                    product_name = product.find_element(By.CSS_SELECTOR, product_name_CSS).text

                    price_elements = product.find_elements(By.CSS_SELECTOR, product_price_CSS)
                    price = price_elements[0].text if price_elements else 'null'

                    price_per_unit_elements = product.find_elements(By.CSS_SELECTOR, product_price_per_unit_CSS)
                    price_per_unit = price_per_unit_elements[0].text if price_per_unit_elements else 'null'

                    all_products.append({
                        "Name": product_name,
                        "Price": price,
                        "Price per Unit": price_per_unit,
                        "Category": main_category,
                        "Subcategory": subcategory,
                        "Date": current_date
                    })

                except Exception as e:
                    print(f"Skipping product due to error: {e}")
                    continue  # Move to next product safely

            # Handle pagination safely
            try:
                # Check if the disabled 'Next' button span is present
                driver.find_element(By.CSS_SELECTOR, 'span.base-pagination__arrow[aria-label="Next"]')
                print(f"Last page reached for category: {main_category} - {subcategory}")
                break  # Exit while loop if next page is disabled

            except:
                try:
                    # Click active 'Next' pagination link
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.base-pagination__arrow[aria-label="Next"]'))
                    )
                    next_button.click()
                    time.sleep(5)  # Wait for the new products to load
                except Exception as e:
                    print(f"Error while clicking next button: {e}")
                    break

# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
csv_file_path = os.path.join(desktop_path, f"Aldi_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")