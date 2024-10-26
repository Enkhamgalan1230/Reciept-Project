from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

all_product_names = []

# Set up options for ChromeDriver
options = Options()
options.headless = False  # Disable headless mode for debugging
options.add_argument("--window-size=1920,1200")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")


# Start ChromeDriver
driver = webdriver.Chrome(options=options)

# Navigate to the Tesco Fresh Food page
driver.get('https://www.tesco.com/groceries/en-GB/shop/fresh-food/')

# Pause to let the page load
time.sleep(5)

# Generalized CSS selector to find all product names
product_name_selector = '#list-content > li > div > div > div.styled__StyledTitleContainer-sc-t48uy4-1.hmpPZn > h3 > a > span'
last_page_selector = '#asparagus-root > div > div.template-wrapper > main > div > div.Msjnn > div > div.J9cp1 > nav.styled__PaginationBarWrapper-sc-1yves1k-0.cjmjqn.BEmtj.ddsweb-pagination__container > div.styled__PaginationControls-sc-1o9kszc-2.erQXtp.WINOO > div > ul > li:nth-child(8) > a > span'
last_page_element = driver.find_element(By.CSS_SELECTOR, last_page_selector)

# Extract the last page number from the element's text
last_page_number = int(last_page_element.text)  # Assuming the text of the element is the page number

for page in range(1, last_page_number + 1):
    # Navigate to the current page
    driver.get(f'https://www.tesco.com/groceries/en-GB/shop/fresh-food/?page={page}')
    time.sleep(5)  # Wait for the page to load

    # Find all elements matching the selector
    product_elements = driver.find_elements(By.CSS_SELECTOR, product_name_selector)

    # Filter for visible elements and add to the list
    product_names = [product.text for product in product_elements if product.is_displayed()]
    all_product_names.extend(product_names)  # Add names to the master list

# Print the list of all product names
print(all_product_names)

# Close the browser
driver.quit()

'''
Now the problem is this script takes everything including like sandwichs,
Do I really need that? Maybe now more specific categories and how to add categories with their product names etc. ? 
for now WE BALLLL
'''