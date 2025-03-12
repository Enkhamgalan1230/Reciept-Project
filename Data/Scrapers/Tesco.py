import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from undetected_chromedriver import Chrome

def create_undetected_headless_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    #options.add_argument("--headless")
    options.add_argument("--window-size=1920,1200")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")

    driver = Chrome(options=options)
    return driver

# Initialize driver
driver = create_undetected_headless_driver()

category_urls = {
    "fresh_food": {
    "fruits": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/fresh-fruit",
    "vegetables": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/fresh-vegetables-and-fresh-flowers",
    "fresh_food_vegan": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/chilled-vegetarian-and-vegan",
    "milk_butter_eggs": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/milk-butter-and-eggs",
    "cheese": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/cheese",
    "yogurts": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/yogurts",
    "dairy_free": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/dairy-free-and-dairy-alternatives",
    "meat_poultry": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/fresh-meat-and-poultry",
    "seafood": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/chilled-fish-and-seafood",
    "cooked_meat_antipasti_dips": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/cooked-meats-antipasti-and-dips",
    "chilled_desserts": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/chilled-desserts",
    "pizza_pasta_gbread": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/fresh-pizza-pasta-and-garlic-bread"
  },
  "bakery": {
    "bakery": "https://www.tesco.com/groceries/en-GB/shop/bakery"
  },
  "frozen": {
    "frozen_vegan": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/vegan",
    "frozen_vegetarian": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/vegetarian",
    "frozen_vegetables": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/vegetables",
    "chips_related": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/chips-potatoes-and-sides",
    "frozen_meat_poultry": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/meat-and-poultry",
    "frozen_seafood": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/fish-and-seafood",
    "frozen_pizza": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/pizza",
    "frozen_desserts": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/desserts",
    "frozen_fruit_pastries": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/fruit-and-pastry",
    "icecreams": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/ice-cream-and-lollies"
  },
  "cupboard": {
    "treats_snacks": "https://www.tesco.com/groceries/en-GB/shop/treats-and-snacks",
    "seed_nuts": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/dried-fruit-nuts-nutrient-powders-and-seeds",
    "cereals": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/cereals",
    "canned": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/tins-cans-and-packets",
    "carbs": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/dried-pasta-rice-noodles-and-cous-cous",
    "sauce": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/table-sauces-olives-pickles-and-chutney",
    "spread_jam": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/jams-sweet-and-savoury-spreads"
  },
  "drinks": {
    "soft_drink": "https://www.tesco.com/groceries/en-GB/shop/drinks/fizzy-and-soft-drinks",
    "water": "https://www.tesco.com/groceries/en-GB/shop/drinks/water",
    "squash": "https://www.tesco.com/groceries/en-GB/shop/drinks/squash-and-cordial",
    "milk": "https://www.tesco.com/groceries/en-GB/shop/drinks/milk-and-milkshakes",
    "tea": "https://www.tesco.com/groceries/en-GB/shop/drinks/tea",
    "coffee": "https://www.tesco.com/groceries/en-GB/shop/drinks/coffee",
    "beer_cider": "https://www.tesco.com/groceries/en-GB/shop/drinks/beer-and-cider",
    "alc_free": "https://www.tesco.com/groceries/en-GB/shop/drinks/alcohol-free-and-low-alcohol-drinks",
    "spirit": "https://www.tesco.com/groceries/en-GB/shop/drinks/spirits",
    "wine": "https://www.tesco.com/groceries/en-GB/shop/drinks/wine"
  }
}

# Generalized CSS selectors for product data
product_box_CSS = '#list-content > li'
product_name_CSS = 'div[class*="StyledTitleContainer"] h3 a span'
product_price_CSS = 'div[class*="StyledBuyBoxContainer"] div[class*="StyledPriceContainer"] p[class*="styled__PriceText-sc-v0qv7n-1"]'
product_price_per_unit_CSS = 'div[class*="StyledBuyBoxContainer"] div[class*="StyledPriceContainer"] p[class*="ddsweb-price__subtext"]'
product_clubcard_discount_CSS = 'div[class*="StyledPromotionsContainer"] div[class*="ContentContainer"] p[class*="ddsweb-value-bar__content-text"]'
next_button_CSS = 'nav[class*="PaginationBarWrapper"] div[class*="PaginationControls"] ul li:last-child a'
#next_button_CSS = "nav.styled__PaginationBarWrapper-sc-1yves1k-0 li:nth-child(9) > a"
# List to hold all product data
all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")

for main_category, subcategories in category_urls.items():
    for subcategory, url in subcategories.items():
        driver.get(url)
        time.sleep(5)  # Initial wait for page load

        print(f"Scraping category: {main_category} - {subcategory}")

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

                # Check for Clubcard discount and assign 'null' if Clubcard discount elements are missing
                clubcard_discount_elements = product.find_elements(By.CSS_SELECTOR, product_clubcard_discount_CSS)
                clubcard_discount = clubcard_discount_elements[0].text if clubcard_discount_elements else 'null'

                # Append the product data to the all_products list
                all_products.append({
                    "Name": product_name, 
                    "Price": price, 
                    "Price per Unit": price_per_unit, 
                    "Clubcard Discount": clubcard_discount, 
                    "Category": main_category,  # Broad category
                    "Subcategory": subcategory,  # Subcategory
                    "Date": current_date
                })

            # Check if there is a "Next" button available to go to the next page
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_CSS))
                )
                aria_disabled = next_button.get_attribute("aria-disabled")
                class_name = next_button.get_attribute
                # If the "Next" button is disabled, exit the loop
                if aria_disabled == "true":
                    print(f"Last page reached for category: {main_category} - {subcategory}")
                    break

                # Otherwise, click the "Next" button to continue to the next page
                next_button.click()
                time.sleep(5)  # Wait for the next page to load
                print("Clicked next button.")

            except Exception as e:
                print(f"Error while checking next button for {main_category} - {subcategory}: {e}")
                break  # Exit the loop on any exception


# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = os.path.join(desktop_path, f"Tesco_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")
