import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

def create_undetected_headless_driver():
    ''' 
    Set up options for Chrome Driver
    Disable image loading for faster page loading and reduced bandwidth
    Run Chrome in no-sandbox mode (helpful in Docker or restricted environments)
    Disable GPU usage (helpful when running in headless mode on systems without a GPU)
    Enable headless mode to run without a visible browser window
    Set the window size for headless mode to ensure all elements load as expected
    Set a custom user-agent to make the bot appear like a regular browser
    Disables "AutomationControlled" features, helping to avoid detection by anti-bot measures
    Prevents the need for shared memory, useful for restricted systems or environments
    Initialize the Chrome driver with the specified options
    Maximizes the browser window (can be helpful if using a visible browser, though not needed in headless mode)
    '''

    options = Options()
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
   # options.add_argument("--headless")
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

    # Fresh foods: 
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
    "pizza_pasta_gbread": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/fresh-pizza-pasta-and-garlic-bread",
    "chilled_desserts": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/chilled-desserts",

    # Bakery:
    "bakery": "https://www.tesco.com/groceries/en-GB/shop/bakery",

    # Frozen food: 
    "frozen_vegan": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/vegan",
    "frozen_vegetarian":"https://www.tesco.com/groceries/en-GB/shop/frozen-food/vegetarian",
    "frozen_vegtables": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/vegetables",
    "chips_related": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/chips-potatoes-and-sides",
    "frozen_meat_poultry": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/meat-and-poultry",
    "frozen_seafood": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/fish-and-seafood",
    "frozen_pizza": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/pizza",
    "frozen_desserts": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/desserts",
    "frozen_fruit_pastries": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/fruit-and-pastry",
    "icecreams": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/ice-cream-and-lollies",

    # Treats & cupboard
    "treats_snacks": "https://www.tesco.com/groceries/en-GB/shop/treats-and-snacks",
    "cupboard": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard",
    #drinks
    "drinks": "https://www.tesco.com/groceries/en-GB/shop/drinks",
    

}

# Generalized CSS selector to find all product names
product_name_CSS = '#list-content > li > div > div > div.styled__StyledTitleContainer-sc-t48uy4-1.hmpPZn > h3 > a > span'
last_page_CSS = '#asparagus-root > div > div.template-wrapper > main > div > div.Msjnn > div > div.J9cp1 > nav.styled__PaginationBarWrapper-sc-1yves1k-0.cjmjqn.BEmtj.ddsweb-pagination__container > div.styled__PaginationControls-sc-1o9kszc-2.erQXtp.WINOO > div > ul > li:nth-child(8) > a > span'
product_price_CSS = '#list-content > li > div > div > div.styled__StyledBuyBoxContainer-sc-t48uy4-3.jYiGsR > div > div > div.styled__StyledPriceContainer-sc-159tobh-5.kpODmQ > div > p.text__StyledText-sc-1jpzi8m-0.gyHOWz.ddsweb-text.styled__PriceText-sc-v0qv7n-1.cXlRF'


# List to hold product data
all_products = []
for category, url in category_urls.items():
    driver.get(url)
    time.sleep(5)  # Wait for page load

    # Determine the last page number for the category
    try:
        last_page_element = driver.find_element(By.CSS_SELECTOR, last_page_CSS)
        last_page_number = int(last_page_element.text)
    except Exception as e:
        print(f"Error finding last page for {category}: {e}")
        last_page_number = 1  # Default to one page if pagination is not found

    # Loop through all pages in the current category
    for page in range(1, last_page_number + 1):
        driver.get(f'{url}?page={page}')
        time.sleep(5)  # Wait for page load

        # Extract product names
        product_elements = driver.find_elements(By.CSS_SELECTOR, product_name_CSS)
        product_names = [product.text for product in product_elements if product.is_displayed()]

        # Add each product to all_products with category
        for product_name in product_names:
            all_products.append({"Name": product_name, "Category": category})


# Close the browser
driver.quit()

