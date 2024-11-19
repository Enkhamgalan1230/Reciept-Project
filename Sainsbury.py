import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

    driver.get("https://www.sainsburys.co.uk/gol-ui/groceries/fruit-and-vegetables/fresh-fruit/c:1020020")
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
    "fresh_food": {
    "fruits": ["https://www.sainsburys.co.uk/gol-ui/groceries/fruit-and-vegetables/fresh-fruit/c:1020020"],
    "vegetables": ["https://www.sainsburys.co.uk/gol-ui/groceries/fruit-and-vegetables/fresh-vegetables/c:1020057"],
    "fresh_food_vegan": ["https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/vegetarian-vegan-and-dairy-free/vegan/c:1019174"],
    "fresh_food_vegetarian": ['https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/vegetarian-vegan-and-dairy-free/vegetarian/c:1019175'],
    "milk_butter_eggs": ["https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/dairy-and-eggs/c:1019075"],
    "cheese": ["https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/dairy-and-eggs/cheese/all-cheese/c:1019035?tag=m52:position5:shop-cheese:non-value"],
    "yogurts": ["https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/dairy-and-eggs/yogurts/all-yogurts/c:1019062?tag=m52:position3:shop-yogurt:non-value"],
    "dairy_free": ['https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/dairy-and-chilled-essentials/dairy-free/c:1019053'],
    "meat_poultry": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/bacon-and-sausages/c:1020327',
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/beef/c:1020335',
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/chicken/c:1020345',
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/duck-game-and-venison/c:1020352',
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/lamb/c:1020376',
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/mince/c:1020379',
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/pork-and-gammon/c:1020384',
        'https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/turkey/c:1020386',
    ],
    "seafood": ["https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/fish-and-seafood/all-fish-and-seafood/c:1020353"],
    "cooked_meat_antipasti_dips": [
        "https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/ham-cooked-meats-and-pate/c:1020370",
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/olives-and-antipasti/c:1019514'
    ],
    "chilled_desserts": ["https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/desserts/all-desserts-and-cream/c:1019076"],
    "pizza_pasta_gbread": ["https://www.sainsburys.co.uk/gol-ui/groceries/dairy-eggs-and-chilled/pizza-pasta-and-garlic-bread/c:1019123"],
    },
    "bakery":{
    "bakery": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/birthday-and-party-cakes/c:1018773',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/bread/c:1018785',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/bread-rolls-and-bagels/c:1018791',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/cakes-and-tarts/c:1018800',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/croissants-and-breakfast-bakery/c:1018812',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/doughnuts-cookies-and-muffins/c:1018820',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/freefrom-bread-and-cakes/c:1018825',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/from-our-in-store-bakery/c:1018834',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/naans-and-meal-sides/c:1018841',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/scones-fruited-and-buns/c:1018850',
        'https://www.sainsburys.co.uk/gol-ui/groceries/bakery/wraps-thins-and-pittas/c:1018858'
    ],
    },

    "Frozen food": {
    "frozen_vegan": ["https://www.sainsburys.co.uk/gol-ui/groceries/frozen/vegan/c:1019988"],
    "frozen_vegetarian": ["https://www.sainsburys.co.uk/gol-ui/groceries/frozen/vegetarian-and-meat-free/c:1019999"],
    "frozen_vegtables": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/fruit-vegetables-and-herbs/broccoli-cauliflower-sprouts-and-carrots/c:1019926',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/fruit-vegetables-and-herbs/mixed-and-prepared-vegetables/c:1019928',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/fruit-vegetables-and-herbs/onions-peppers-and-herbs/c:1019929',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/fruit-vegetables-and-herbs/peas-beans-and-sweetcorn/c:1019930',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/fruit-vegetables-and-herbs/roast-potatoes-and-parsnips/c:1019932'
    ],
    "chips_related": [
        "https://www.sainsburys.co.uk/gol-ui/groceries/frozen/chips-potatoes-and-rice/chips-and-wedges/all-chips-and-wedges/c:1019884",
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/chips-potatoes-and-rice/onion-rings/c:1019890',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/chips-potatoes-and-rice/roast-potatoes/c:1019892',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/chips-potatoes-and-rice/sweet-potatoes/c:1019893',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/chips-potatoes-and-rice/waffles-hashbrowns-and-croquettes/c:1019894'
    ],
    "frozen_meat_poultry": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/meat-and-poultry/beef-pork-and-lamb/c:1019956',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/meat-and-poultry/burgers/c:1019957',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/meat-and-poultry/chicken-and-turkey/c:1019964',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/meat-and-poultry/sausages-and-bacon/c:1019965'
    ],
    "frozen_seafood": ["https://www.sainsburys.co.uk/gol-ui/groceries/frozen/fish-and-seafood/all/c:1019911"],
    "frozen_pizza": ["https://www.sainsburys.co.uk/gol-ui/groceries/frozen/pizza-and-garlic-bread/all-pizza-and-garlic-bread/c:1019967"],
    "frozen_desserts": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/desserts-and-pastry/cakes-and-cheesecakes/c:1019897',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/desserts-and-pastry/meringues-and-roulades/c:1019898',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/desserts-and-pastry/sponges-crumbles-and-tarts/c:1019901'
    ],
    "frozen_fruit_pastries": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/fruit-vegetables-and-herbs/fruit/c:1019927',
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/desserts-and-pastry/pies-and-pastry/c:1019899',
    ],
    "icecreams": ['https://www.sainsburys.co.uk/gol-ui/groceries/frozen/ice-cream-and-ice/all-ice-creams/c:1019935'],
    },
    "cupboard": {
    "treats_snacks": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/frozen/ice-cream-and-ice/all-ice-creams/c:1019935',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/biscuits-and-crackers/c:1019495',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/crisps-nuts-and-snacking-fruit/multipack-crisps/all/c:1019677',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/crisps-nuts-and-snacking-fruit/sharing-crisps/c:1019689',
    ],
    "seed_nuts": ['https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/crisps-nuts-and-snacking-fruit/snacking-fruit-and-seeds/c:1019690'],
    "cereals": ['https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/cereals/all-cereals/c:1019541'],
    "canned": [
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/baked-beans-and-canned-pasta/c:1019496',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/cold-meat/c:1019497',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/fish/all/c:1019498',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/fruit/c:1019511',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/hot-meat-and-meals/c:1019512',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/instant-snacks-and-meals/c:1019513',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/pulses-and-beans/c:1019516',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/soups/c:1019528',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/tomatoes/c:1019530',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/vegetables/c:1019538',
        'https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/canned-tinned-and-packaged-foods/vegetables/sweetcorn/c:1019537'
    ],
    "carbs": ['https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/rice-pasta-and-noodles/c:1019794'],
    "sauce": ["https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/cooking-ingredients-and-oils/c:1019630"],
    "spread_jam": ["https://www.sainsburys.co.uk/gol-ui/groceries/food-cupboard/jams-honey-and-spreads/c:1019754"],
    },
    "drinks": {
    "soft_drink": ["https://www.sainsburys.co.uk/gol-ui/groceries/drinks/fizzy-drinks/c:1019310"],
    "water": ['https://www.sainsburys.co.uk/gol-ui/groceries/drinks/water/c:1019437'],
    "squash": ["https://www.sainsburys.co.uk/gol-ui/groceries/drinks/squash-and-cordials/c:1019393"],
    "milk": ["https://www.sainsburys.co.uk/gol-ui/groceries/drinks/milk-and-milk-drinks/c:1019346"],
    "tea": ["https://www.sainsburys.co.uk/gol-ui/groceries/drinks/tea-coffee-and-hot-drinks/tea/c:1019427"],
    "coffee": ['https://www.sainsburys.co.uk/gol-ui/groceries/drinks/tea-coffee-and-hot-drinks/coffee/c:1019405'],
    "beer_cider": ['https://www.sainsburys.co.uk/gol-ui/groceries/drinks/beer-and-cider/c:1019285'],
    "alc_free": ['https://www.sainsburys.co.uk/gol-ui/groceries/drinks/low-and-no-alcohol/c:1019340'],
    "spirit": ['https://www.sainsburys.co.uk/gol-ui/groceries/drinks/spirits-and-liqueurs/c:1019377'],
    "wine": ['https://www.sainsburys.co.uk/gol-ui/groceries/drinks/wine/c:1019462']
    }
}


product_box_CSS = '#main > ul > li > article > div.pt__content:not(.pt__content--with-header)'
product_name_CSS = 'article div.pt__content div.pt__wrapper-inner div.pt__wrapper__top div.product-description-box h2 a'
product_price_CSS = 'article div.pt__content div.pt__wrapper-inner div.pt__wrapper__bottom div.pt__cost span.pt__cost__retail-price'
product_price_per_unit_CSS = 'article div.pt__content div.pt__wrapper-inner div.pt__wrapper__bottom div.pt__cost span.pt__cost__unit-price-per-measure'
next_button_CSS = '#main > section > div > div > nav > ul > li[class*="ln-c-pagination__item"][class*="next"] > a'
nectar_CSS = '#main ul li article .pt__cost__contextual--wrapper > .pt__cost__contextual.pt__cost__contextual--with-nectar-not-associated > span'
# List to hold all product data
all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")

# Loop through each category and URL in the category URLs dictionary
for main_category, subcategories in category_urls.items():
    for subcategory, urls in subcategories.items():
        for url in urls:
            driver.get(url)
            time.sleep(5)  # Allow the page to load initially

            while True:
                # Extract product elements on the current page
                product_boxes = driver.find_elements(By.CSS_SELECTOR, product_box_CSS)

                for product in product_boxes:
                    try:
                        # Extract product name
                        product_name = product.find_element(By.CSS_SELECTOR, product_name_CSS).text

                        # Extract product price or assign 'null' if not found
                        price_elements = product.find_elements(By.CSS_SELECTOR, product_price_CSS)
                        price = price_elements[0].text if price_elements else 'null'

                        # Extract price per unit or assign 'null' if not found
                        price_per_unit_elements = product.find_elements(By.CSS_SELECTOR, product_price_per_unit_CSS)
                        price_per_unit = price_per_unit_elements[0].text if price_per_unit_elements else 'null'

                        # Check for Clubcard discount and assign 'null' if Clubcard discount elements are missing
                        nectar_discount_elements = product.find_elements(By.CSS_SELECTOR, nectar_CSS)
                        nectar_discount = nectar_discount_elements[0].text if nectar_discount_elements else 'null'

                        # Append the product data to the list
                        all_products.append({
                            "Name": product_name,
                            "Price": price,
                            "Price per Unit": price_per_unit,
                            "Nectar price": nectar_discount,
                            "Category": main_category,  # Broad category
                            "Subcategory": subcategory,  # Subcategory
                            "Date": current_date
                        })

                    except NoSuchElementException as e:
                        print(f"Element missing while extracting product data: {e}")
                    except Exception as e:
                        print(f"Error extracting product data: {e}")

                # Handle pagination: check for the "Next" button and navigate if enabled
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, next_button_CSS))
                    )

                    # Check if the button is disabled or not clickable
                    if "disabled" in next_button.get_attribute("class") or next_button.get_attribute("aria-disabled") == "true":
                        print(f"Last page reached for category: {main_category} - {subcategory}")
                        break  # Exit the loop if on the last page

                    # Click the "Next" button to navigate
                    next_button.click()
                    time.sleep(5)  # Allow time for the next page to load
                    print(f"Navigating to the next page for {main_category} - {subcategory}.")

                except TimeoutException:
                    print(f"Next button not found. Stopping pagination for: {main_category} - {subcategory}.")
                    break
                except Exception as e:
                    print(f"Error while handling the next button: {e}")
                    break

# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
csv_file_path = os.path.join(desktop_path, f"Sainsburys_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")