import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

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

    # Fresh foods: 
    "fruits": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/fresh-fruit",
}

# Generalized CSS selector to find all product names
'''
product_name_CSS = '#list-content > li > div > div > div.styled__StyledTitleContainer-sc-t48uy4-1.hmpPZn > h3 > a > span'
last_page_CSS = '#asparagus-root > div > div.template-wrapper > main > div > div.Msjnn > div > div.J9cp1 > nav.styled__PaginationBarWrapper-sc-1yves1k-0.cjmjqn.BEmtj.ddsweb-pagination__container > div.styled__PaginationControls-sc-1o9kszc-2.erQXtp.WINOO > div > ul > li:nth-child(8) > a > span'
product_price_CSS = '#list-content > li > div > div > div.styled__StyledBuyBoxContainer-sc-t48uy4-3.jYiGsR > div > div > div.styled__StyledPriceContainer-sc-159tobh-5.kpODmQ > div > p.text__StyledText-sc-1jpzi8m-0.gyHOWz.ddsweb-text.styled__PriceText-sc-v0qv7n-1.cXlRF'
'''
# Generalized CSS selectors for product data
product_name_CSS = '#list-content li div[class*="StyledTitleContainer"] h3 a span'
next_button_CSS = 'nav[class*="PaginationBarWrapper"] div[class*="PaginationControls"] ul li:last-child a'

# Specific CSS selectors for prices
product_price_CSS = '#list-content li div[class*="StyledBuyBoxContainer"] div[class*="StyledPriceContainer"] p[class*="styled__PriceText-sc-v0qv7n-1"]'  # Adjust this if the class changes
product_price_per_unit_CSS = '#list-content li div[class*="StyledBuyBoxContainer"] div[class*="StyledPriceContainer"] p[class*="ddsweb-price__subtext"]'
product_clubcard_discount_CSS = '#list-content li div[class*="StyledPromotionsContainer"] div[class*="ContentContainer"] p[class*="ddsweb-value-bar__content-text"]'


# Create a list to hold all product data
all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")  # Get current date in YYYY-MM-DD format

# List to hold product data
all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")

for category, url in category_urls.items():
    driver.get(url)
    time.sleep(5)  # Wait for page load

    while True:
        # Extract product elements
        product_elements = driver.find_elements(By.CSS_SELECTOR, product_name_CSS)
        
        for product_index, product in enumerate(product_elements):
            # Check if the product is out of stock
            out_of_stock_selector = f'#list-content > li:nth-child({product_index + 1}) > div > div > div.styled__StyledMessagingContainer-sc-t48uy4-5.jHhxvV > div > div.styled__GlobalMessageContainer-sc-1s4u7b1-7.gaqrDw.ddsweb-status-messaging__message-container > div > div > span'
            out_of_stock_message = driver.find_elements(By.CSS_SELECTOR, out_of_stock_selector)

            if out_of_stock_message:
                # If the item is out of stock, assign None to price-related fields
                price = None
                price_per_unit = None
                clubcard_discount = None
            else:
                # Extract product prices only if the product is in stock
                price_elements = driver.find_elements(By.CSS_SELECTOR, product_price_CSS)
                prices = [price.text if price.is_displayed() else None for price in price_elements]
                price = prices[product_index] if product_index < len(prices) else None

                # Extract prices per unit
                price_per_unit_elements = driver.find_elements(By.CSS_SELECTOR, product_price_per_unit_CSS)
                prices_per_unit = [price_per_unit.text if price_per_unit.is_displayed() else None for price_per_unit in price_per_unit_elements]
                price_per_unit = prices_per_unit[product_index] if product_index < len(prices_per_unit) else None

                # Extract Clubcard discounts
                clubcard_discount_elements = driver.find_elements(By.CSS_SELECTOR, product_clubcard_discount_CSS)
                clubcard_discounts = [discount.text if discount.is_displayed() else None for discount in clubcard_discount_elements]
                clubcard_discount = clubcard_discounts[product_index] if product_index < len(clubcard_discounts) else None

            # Append the product data to the all_products list
            all_products.append({
                "Name": product.text, 
                "Price": price, 
                "Price per Unit": price_per_unit, 
                "Clubcard Discount": clubcard_discount, 
                "Category": category, 
                "Date": current_date
            })

        # Check if the Next button is disabled
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, next_button_CSS)
            aria_disabled = next_button.get_attribute("aria-disabled")

            if aria_disabled == "true":
                break  # Exit loop if the next button is disabled

            # Click the Next button to go to the next page
            next_button.click()
            time.sleep(5)  # Wait for page load

        except Exception as e:
            print(f"Error while checking next button: {e}")
            break  # Exit loop on any exception
        
# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

# Save DataFrame to CSV on desktop
desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")  # Get the path to the desktop
csv_file_path = os.path.join(desktop_path, "tesco_products.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")
