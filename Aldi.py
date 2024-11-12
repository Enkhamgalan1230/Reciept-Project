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
    # Fresh food
    "fruits" : "https://groceries.aldi.co.uk/en-GB/fresh-food/fruit?origin=dropdown&c1=groceries&c2=fresh-food&c3=fresh-fruit&clickedon=fresh-fruit",
    "vegetables": "https://groceries.aldi.co.uk/en-GB/fresh-food/fresh-vegetables?origin=dropdown&c1=groceries&c2=fresh-food&c3=fresh-vegetables&clickedon=fresh-vegetables",
    "fresh_food_vegan": "https://groceries.aldi.co.uk/en-GB/fresh-food?&fn1=Lifestyle&fv1=Vegetarian%7CVegan",
    "milk_butter_eggs": "https://groceries.aldi.co.uk/en-GB/chilled-food?&fn1=CategoryLevel2_Facet&fv1=L2DA",
    "cheese": "https://groceries.aldi.co.uk/en-GB/chilled-food/cheese?origin=dropdown&c1=groceries&c2=chilled-food&c3=cheese&clickedon=cheese",
    "yogurts": "https://groceries.aldi.co.uk/en-GB/chilled-food/yogurts?origin=dropdown&c1=groceries&c2=chilled-food&c3=yogurts&clickedon=yogurts",
    "meat_poultry": "https://groceries.aldi.co.uk/en-GB/fresh-food/meat-poultry?origin=dropdown&c1=groceries&c2=fresh-food&c3=meat-poultry&clickedon=meat-poultry",
    "seafood": "https://groceries.aldi.co.uk/en-GB/fresh-food/fresh-fish-seafood?origin=dropdown&c1=groceries&c2=fresh-food&c3=fresh-fish-seafood&clickedon=fresh-fish-seafood",
    "party_food_salads_dips": "https://groceries.aldi.co.uk/en-GB/chilled-food?&fn1=CategoryLevel2_Facet&fv1=L2DJ",
    "chilled_desserts": "https://groceries.aldi.co.uk/en-GB/chilled-food?&fn1=CategoryLevel2_Facet&fv1=L2DD",
    "pizza_pasta_gbread": "https://groceries.aldi.co.uk/en-GB/chilled-food/pizza-pasta-garlic-bread?origin=dropdown&c1=groceries&c2=chilled-food&c3=pizza-pasta-garlic-bread&clickedon=pizza-pasta-garlic-bread",
    "chilled_meats": "https://groceries.aldi.co.uk/en-GB/chilled-food/chilled-meats?origin=dropdown&c1=groceries&c2=chilled-food&c3=chilled-meats&clickedon=chilled-meats",
    
    # Bakery:
    "bakery": "https://groceries.aldi.co.uk/en-GB/bakery?origin=dropdown&c1=groceries&c2=bakery&clickedon=bakery",

    # Frozen food: 
    "frozen_vegetarian": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GF",
    "frozen_vegtables": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GE",
    "chips_related": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GA",
    "frozen_meat_poultry": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GC",
    "frozen_seafood": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GB",
    "frozen_pizza": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GI",
    "frozen_desserts_icecream": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GG",
    "frozen_fruit": "https://groceries.aldi.co.uk/en-GB/frozen?&fn1=CategoryLevel2_Facet&fv1=L2GH",

    # Treats & cupboard
    "treats": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2EC",
    "snacks": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2ED",
    "seed_nuts": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2EE",
    "cereals": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2EB",
    "canned": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2EG",
    "carbs": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2EH",
    "sauce": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2EF",
    "spread_jam": "https://groceries.aldi.co.uk/en-GB/food-cupboard?&fn1=CategoryLevel2_Facet&fv1=L2EJ",

    #drinks
    "soft_drink": "https://groceries.aldi.co.uk/en-GB/drinks/soft-drinks-juices?origin=dropdown&c1=groceries&c2=drinks&c3=soft-drinks-juices&clickedon=soft-drinks-juices",
    "water": "https://groceries.aldi.co.uk/en-GB/drinks?&fn1=CategoryLevel2_Facet&fv1=L2FG",
    "milk": "https://groceries.aldi.co.uk/en-GB/chilled-food/milk-dairy-eggs?&fn1=CategoryLevel3_Facet&fv1=L3DAF",
    "tea": "https://groceries.aldi.co.uk/en-GB/drinks/tea?origin=dropdown&c1=groceries&c2=drinks&c3=tea&clickedon=tea",
    "coffee": "https://groceries.aldi.co.uk/en-GB/drinks?&fn1=CategoryLevel2_Facet&fv1=L2FB",
    "beer_cider": "https://groceries.aldi.co.uk/en-GB/drinks?&fn1=CategoryLevel2_Facet&fv1=L2FA",
    "spirit": "https://groceries.aldi.co.uk/en-GB/drinks?&fn1=CategoryLevel2_Facet&fv1=L2FE",
    "wine": "https://groceries.aldi.co.uk/en-GB/drinks?&fn1=CategoryLevel2_Facet&fv1=L2FF"
}

product_box_CSS = '#vueSearchResults > div > div'
product_name_CSS = 'div[class*="product-tile-text"][class*="text-center"][class*="px-3"][class*="mb-3"] > a'
product_price_CSS = 'div[class*="d-flex"][class*="flex-column"][class*="flex-grow-1"][class*="justify-content-end"][class*="px-3"] div[class*="product-tile-price"][class*="text-center"] > div > span > span'
product_price_per_unit_CSS = 'div[class*="d-flex"][class*="flex-column"][class*="flex-grow-1"][class*="justify-content-end"][class*="px-3"] div[class*="product-tile-price"][class*="text-center"] > div > div > p > small > span'
next_button_CSS = 'ul > li.page-item.next.ml-2'

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
            time.sleep(5)
            print("Clicked next button.")  # Wait for the next page to load

        except Exception as e:
            print(f"Error while checking or clicking next button: {e}")
            print(f"Error at page URL: {driver.current_url}")
            print(f"Error Details: {str(e)}")
            break  # Exit the loop on any exception

# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
csv_file_path = os.path.join(desktop_path, f"Aldi_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")