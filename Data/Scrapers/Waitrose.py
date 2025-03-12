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

    accept_cookies_button_CSS = '#content > div > div.overlay___EpSr5.bottom___qT4gz.spaceAroundLarge___HS0_z > div > div > section > div.cookiesCTA___REDdb > button.button___vXfOJ.primary___qJhSG.acceptAll___CHGcH'
    # Accept cookies pop-up once, if present
    driver.get("https://www.waitrose.com/")
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, accept_cookies_button_CSS))
        )
        accept_button.click()
        print("Cookies accepted.")
    except:
        print("No cookies pop-up detected.")

    return driver

# Initialize driver
driver = create_undetected_headless_driver()

category_urls = {
    "fresh_food": {
    'fruit': ['https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/fresh_fruit'],
    "vegetables": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/fresh_vegetables"],
    "fresh_food_vegan": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/vegan"],
    "milk_butter_eggs": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/milk_butter_and_eggs"],
    "cheese": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/cheese"],
    "yogurts": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/yogurts"],
    "meat_poultry": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/fresh_meat"],
    "seafood": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/chilled_fish_and_seafood"],
    "cooked_meat_antipasti_dips": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/cooked_meats_deli_and_dips"],
    "chilled_desserts": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/desserts"],
    "pizza_pasta_gbread": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/fresh_pizza_and_garlic_bread"],
    },
    "bakery": {
    "bakery": ["https://www.waitrose.com/ecom/shop/browse/groceries/bakery"],
    },

    "frozen":{ 
    "frozen_vegan": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_vegan"],
    "frozen_vegetarian":["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_vegetarian_food"],
    "frozen_vegtables": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_vegetables_herbs_and_rice"],
    "chips_related": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_chips_and_potatoes"],
    "frozen_meat_poultry": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_meat_and_poultry"],
    "frozen_seafood": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_fish_and_seafood"],
    "frozen_pizza": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_pizza"],
    "frozen_desserts": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_desserts"],
    "frozen_fruit_pastries": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/frozen_fruits_and_smoothie_mixes"],
    "icecreams": ["https://www.waitrose.com/ecom/shop/browse/groceries/frozen/ice_cream_frozen_yogurt_and_sorbets"],
    },
    "cupboard": {
    "treats_snacks": [
        "https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/crisps_snacks_and_nuts",
        'https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/chocolate_and_sweets'
    ],
    "seed_nuts": ["https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/crisps_snacks_and_nuts/nuts_seeds_and_dried_fruit"],
    "cereals": ["https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/breakfast_cereal"],
    "canned": ["https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/tins_cans_and_packets"],
    "carbs": ["https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/rice_pasta_and_pulses"],
    "sauce": [
        "https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/dried_herbs_oils_and_vinegar",
        'https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/condiments_dressings_and_marinades',
        ],
    "spread_jam": ["https://www.waitrose.com/ecom/shop/browse/groceries/food_cupboard/jam_honey_and_spreads"],
    },
    "drinks": {
    "soft_drink": ["https://www.waitrose.com/ecom/shop/browse/groceries/tea_coffee_and_soft_drinks/fizzy_drinks"],
    "water": ["https://www.waitrose.com/ecom/shop/browse/groceries/tea_coffee_and_soft_drinks/water"],
    "squash": ["https://www.waitrose.com/ecom/shop/browse/groceries/tea_coffee_and_soft_drinks/squash_and_cordials"],
    "milk": ["https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/milk_butter_and_eggs/milk"],
    "tea": ["https://www.waitrose.com/ecom/shop/browse/groceries/tea_coffee_and_soft_drinks/tea"],
    "coffee": ["https://www.waitrose.com/ecom/shop/browse/groceries/tea_coffee_and_soft_drinks/coffee"],
    "beer_cider": [
        "https://www.waitrose.com/ecom/shop/browse/groceries/beer_wine_and_spirits/beer",
        'https://www.waitrose.com/ecom/shop/browse/groceries/beer_wine_and_spirits/cider'
        ],
    "alc_free": ["https://www.waitrose.com/ecom/shop/browse/groceries/beer_wine_and_spirits/alcohol_free_and_low_alcohol_drinks"],
    "spirit": ["https://www.waitrose.com/ecom/shop/browse/groceries/beer_wine_and_spirits/spirits_and_liqueurs"],
    "wine": ["https://www.waitrose.com/ecom/shop/browse/groceries/beer_wine_and_spirits/wine"]

    }
}

product_box_CSS = 'div.content___yamWw'
product_name_CSS = 'div.content___yamWw > section.details___rYEWU > div.headerStarWrapper___W6G_c > header > a > h2 > span'
product_price_CSS = 'div.content___yamWw > section.trolleyChoices___TDa6D > div > div.prices___IA5LC > span.itemPrice___j1MYI > span:not(.priceEst___cK_H9):not(.priceInfo___ThE1M)'
product_price_per_unit_CSS = 'div.content___yamWw > section.trolleyChoices___TDa6D > div > div.prices___IA5LC > span.pricePerUnit___a1PxI'
next_button_CSS = 'div.loadMoreWrapper___pnUl7 > button'

all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")

# Loop through each category and URL in the category URLs dictionary
for main_category, subcategories in category_urls.items():
    for subcategory, urls in subcategories.items():
        for url in urls:
            driver.get(url)
            time.sleep(5)  # Initial wait for page load

            # Wait until all products are loaded
            while True:
                try:
                    # Check if the "Load More" button is clickable
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_CSS))
                    )
                    next_button.click()  # Click "Load More"
                    time.sleep(5)  # Wait for new products to load
                except:
                    print("No more products to load or the 'Load More' button is disabled.")
                    break  # Break the loop if the button is no longer clickable or doesn't exist

            # Now scrape all products after all pages have been loaded
            product_boxes = driver.find_elements(By.CSS_SELECTOR, product_box_CSS)

            for product in product_boxes:
                product_name = product.find_element(By.CSS_SELECTOR, product_name_CSS).text
                if not product_name:
                    print("No products found with the selector!")

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
                    "Category": main_category,  # Broad category
                    "Subcategory": subcategory,  # Subcategory 
                    "Date": current_date
                })

# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
csv_file_path = os.path.join(desktop_path, f"Waitrose_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")