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
    # Accept cookies pop-up once, if present
    driver.get("https://groceries.asda.com/")
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
    "fruits": ["https://groceries.asda.com/aisle/fruit-veg-flowers/fruit/view-all-fruit/1215686352935-910000975210-1215666947025"],
    "vegetables": ["https://groceries.asda.com/aisle/fruit-veg-flowers/vegetables-potatoes/view-all-vegetables-potatoes/1215686352935-1215665891579-1215686354635"],
    "fresh_food_vegan": ["https://groceries.asda.com/aisle/meat-poultry-fish/vegan-vegetarian/vegan-chilled-meat-alternatives/1215135760597-1215686355777-1215685771335"],
    "fresh_food_vegetarian": ["https://groceries.asda.com/aisle/meat-poultry-fish/vegan-vegetarian/vegetarian-chilled-food/1215135760597-1215686355777-1215686355778"],

    "milk_butter_eggs": ["https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/fresh-milk/1215660378320-1215339432024-1215339434886",
                         "https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/butter-spreads/1215660378320-1215339432024-1215339437646",
                         "https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/eggs/1215660378320-1215339432024-910000975407"], 
    
    "dairy_free": ["https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/dairy-free-or-lactose-free-drinks/1215660378320-1215339432024-1215339434995"],
    "cheese":  ["https://groceries.asda.com/aisle/chilled-food/cheese/cheddar-regional-cheese/1215660378320-1215341805721-1215341805765",
                "https://groceries.asda.com/aisle/chilled-food/cheese/cheeseboard-speciality-cheese/1215660378320-1215341805721-1215686355503",
                "https://groceries.asda.com/aisle/chilled-food/cheese/grated-sliced-cheese/1215660378320-1215341805721-1215341805815",
                "https://groceries.asda.com/aisle/chilled-food/cheese/soft-cottage-cheese/1215660378320-1215341805721-1215341805865"],

    "yogurts": ["https://groceries.asda.com/aisle/chilled-food/yogurts-desserts/yogurts-fromage-frais/1215660378320-1215341888021-910000975580"],

    "meat_poultry":["https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/chicken-turkey/1215135760597-910000975206-910000975462",
                    "https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/beef/1215135760597-910000975206-910000975528",
                    "https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/bacon-sausages-gammon/1215135760597-910000975206-910000975529",
                    "https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/pork/1215135760597-910000975206-910000975676",
                    "https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/lamb/1215135760597-910000975206-910000975607"],
    "seafood": ["https://groceries.asda.com/aisle/meat-poultry-fish/fish-seafood/view-all-fish/1215135760597-1215337195095-1215685901166"],

    "cooked_meat_antipasti_dips":["https://groceries.asda.com/aisle/meat-poultry-fish/cooked-meat/sliced-cooked-meats/1215135760597-1215661243132-1215663266417",
                                "https://groceries.asda.com/aisle/meat-poultry-fish/cooked-meat/chicken-turkey-pieces/1215135760597-1215661243132-1215663266326"],
    
    "chilled_desserts": ["https://groceries.asda.com/aisle/chilled-food/yogurts-desserts/desserts/1215660378320-1215341888021-910000975612"],
    "pizza_pasta_gbread": ["https://groceries.asda.com/aisle/chilled-food/pizza-pasta-garlic-bread/fresh-pizza/1215660378320-1215661254820-910000975409",
                           "https://groceries.asda.com/aisle/chilled-food/pizza-pasta-garlic-bread/pasta-sauce-garlic-bread/1215660378320-1215661254820-910000975441"],
    },
    "bakery": {
    "bakery": ["https://groceries.asda.com/dept/bakery/exceptional-bakery/1215686354843-1215686354845",
                "https://groceries.asda.com/dept/bakery/in-store-bakery/1215686354843-1215686354846",
                "https://groceries.asda.com/dept/bakery/bread-rolls/1215686354843-1215686354847",
                "https://groceries.asda.com/dept/bakery/gluten-free-bakery/1215686354843-1215686354849",
                "https://groceries.asda.com/dept/bakery/wraps-bagels-pittas-naans/1215686354843-1215686354848",
                "https://groceries.asda.com/dept/bakery/scones-teacakes-fruit-loaves/1215686354843-1215686354881",
                "https://groceries.asda.com/dept/bakery/crumpets-muffins-pancakes/1215686354843-1215686354882",
                "https://groceries.asda.com/dept/bakery/cakes/1215686354843-1215686354851",
                "https://groceries.asda.com/dept/bakery/croissants-brioche-on-the-go/1215686354843-1215686354850",
                "https://groceries.asda.com/dept/bakery/cake-bars-slices-tarts/1215686354843-1215686354852",
                "https://groceries.asda.com/dept/bakery/desserts-cream-cakes/1215686354843-1215686354853"],
    },
    "frozen": {
    "frozen_vegetarian": ["https://groceries.asda.com/aisle/frozen-food/vegetarian-vegan/vegetarian-frozen-food/1215338621416-1215338748833-1215339097600"],
    "frozen_vegan": ["https://groceries.asda.com/aisle/frozen-food/vegetarian-vegan/vegan-frozen-food/1215338621416-1215338748833-1215685961783"],
    "frozen_vegtables": ["https://groceries.asda.com/dept/frozen-food/vegetables/1215338621416-1215338747117"],
    "chips_related": ["https://groceries.asda.com/dept/frozen-food/chips-potatoes-sides/1215338621416-1215338621577"],  
    "frozen_meat_poultry": ["https://groceries.asda.com/aisle/frozen-food/chicken-meat-fish/frozen-chicken-turkey/1215338621416-1215666947082-1215685961752",
                            "https://groceries.asda.com/aisle/frozen-food/chicken-meat-fish/frozen-sausages-burgers/1215338621416-1215666947082-1215685961753",
                            "https://groceries.asda.com/aisle/frozen-food/chicken-meat-fish/frozen-beef-lamb-pork/1215338621416-1215666947082-1215685961754",
                            "https://groceries.asda.com/aisle/frozen-food/chicken-meat-fish/frozen-mince/1215338621416-1215666947082-1215685961755",
                            "https://groceries.asda.com/aisle/frozen-food/chicken-meat-fish/frozen-roasting-joints-sides/1215338621416-1215666947082-1215685961756"],
    "frozen_seafood": ["https://groceries.asda.com/aisle/frozen-food/chicken-meat-fish/frozen-fish/1215338621416-1215666947082-1215685961757",
                        "https://groceries.asda.com/aisle/frozen-food/chicken-meat-fish/frozen-prawns-seafood/1215338621416-1215666947082-1215685961758"],
    "frozen_pizza": ["https://groceries.asda.com/aisle/frozen-food/pizza-garlic-bread-party/frozen-thin-crust-pizza/1215338621416-1215338747245-1215685961777",
                    "https://groceries.asda.com/aisle/frozen-food/pizza-garlic-bread-party/frozen-deep-pan-pizza/1215338621416-1215338747245-1215685961778",
                    "https://groceries.asda.com/aisle/frozen-food/pizza-garlic-bread-party/frozen-takeaway-stuffed-crust-pizza/1215338621416-1215338747245-1215686354083",
                    "https://groceries.asda.com/aisle/frozen-food/pizza-garlic-bread-party/frozen-vegetarian-vegan-pizza/1215338621416-1215338747245-1215685961781"],

    "frozen_desserts": ["https://groceries.asda.com/aisle/frozen-food/desserts-pastry/frozen-pies-crumbles/1215338621416-1215338621511-1215685961767",
                        "https://groceries.asda.com/aisle/frozen-food/desserts-pastry/frozen-cheesecakes-tarts/1215338621416-1215338621511-1215685961768",
                        "https://groceries.asda.com/aisle/frozen-food/desserts-pastry/gateaux-roulades-meringues/1215338621416-1215338621511-1215685961769",
                        "https://groceries.asda.com/aisle/frozen-food/desserts-pastry/party-ice-cream-desserts/1215338621416-1215338621511-1215685961770"],
    "frozen_fruit_pastries": ["https://groceries.asda.com/aisle/frozen-food/desserts-pastry/frozen-fruit-smoothie-mixes/1215338621416-1215338621511-1215686356414",
                              "https://groceries.asda.com/aisle/frozen-food/desserts-pastry/frozen-pastry-breakfast/1215338621416-1215338621511-1215339071265"],
    "icecreams": ["https://groceries.asda.com/aisle/frozen-food/ice-cream-parlour/view-all-ice-cream-parlour/1215338621416-1215338747181-1215685901765"],
    },
    "cupboard" : {
    "treats_snacks": ["https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/multipack-chocolate/1215686355680-1215279696813-910000975533",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/sharing-chocolate-bars/1215686355680-1215279696813-1215686353225",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/chocolate-bags-cartons/1215686355680-1215279696813-1215686353226",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/small-chocolate-bars-bags/1215686355680-1215279696813-1215686353227",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/dark-chocolate/1215686355680-1215279696813-1215686353228",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/sweets/1215686355680-1215279696813-910000975627",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/boxed-chocolates-gifts/1215686355680-1215279696813-1215685421655",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/sweet-popcorn/1215686355680-1215279696813-1215686355193",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/mints-chewing-gum/1215686355680-1215279696813-1215681468112",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/fun-size-chocolate-sweets/1215686355680-1215279696813-1215681268562",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/chocolates-sweets/extra-special-chocolates-sweets/1215686355680-1215279696813-1215686351301",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/crisps-nuts-popcorn/multipack-crisps/1215686355680-1215165893478-1215662199368",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/meat-cheese-snacks/cheese-snacks-lunchbox/1215686355680-1215686355681-1215341805914",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/crisps-nuts-popcorn/sharing-crisps/1215686355680-1215165893478-1215662199412",
                    "https://groceries.asda.com/aisle/sweets-treats-snacks/crisps-nuts-popcorn/tortilla-chips-dips/1215686355680-1215165893478-1215684181120"],

    "seed_nuts": ["https://groceries.asda.com/aisle/sweets-treats-snacks/crisps-nuts-popcorn/nuts-dried-fruit/1215686355680-1215165893478-910000975624"],
    "cereals": ["https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/everyday-family-cereals/1215337189632-1215337194729-1215650880276",
                "https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/muesli-granola-crisp/1215337189632-1215337194729-1215650881116",
                "https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/porridge-oats/1215337189632-1215337194729-1215650881414"],
    "canned": ["https://groceries.asda.com/aisle/food-cupboard/tinned-food/baked-beans/1215337189632-1215165876400-910000975571",
                "https://groceries.asda.com/aisle/food-cupboard/tinned-food/tinned-pasta-spaghetti/1215337189632-1215165876400-1215685891277",
                "https://groceries.asda.com/aisle/food-cupboard/tinned-food/tinned-fish/1215337189632-1215165876400-910000975503",
                "https://groceries.asda.com/aisle/food-cupboard/tinned-food/tinned-tomatoes/1215337189632-1215165876400-910000975480",
                "https://groceries.asda.com/aisle/food-cupboard/tinned-food/tinned-vegetables/1215337189632-1215165876400-1215685891278",
                "https://groceries.asda.com/aisle/food-cupboard/tinned-food/tinned-soup/1215337189632-1215165876400-910000975546",
                "https://groceries.asda.com/aisle/food-cupboard/tinned-food/passata-tomato-puree/1215337189632-1215165876400-1215685891279",
                "https://groceries.asda.com/aisle/food-cupboard/tinned-food/tinned-fruit/1215337189632-1215165876400-1215678984489"],

    "carbs": ["https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/pasta/1215337189632-1215337189669-1215337189706",
                "https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/dry-rice-noodles-grains/1215337189632-1215337189669-1215337189751",
                "https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/microwavable-rice-grains/1215337189632-1215337189669-1215685011119",
                "https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/gluten-free-pasta-noodles-rice/1215337189632-1215337189669-1215685641187",
                "https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/quick-rice-pasta-meals/1215337189632-1215337189669-1215686355231"],

    "sauce": ["https://groceries.asda.com/aisle/food-cupboard/cooking-sauces-meal-kits-sides/cooking-sauces/1215337189632-1215165877786-910000975569",
                "https://groceries.asda.com/aisle/food-cupboard/cooking-sauces-meal-kits-sides/italian-sauces-ingredients/1215337189632-1215165877786-1215664037798",
                "https://groceries.asda.com/aisle/food-cupboard/cooking-sauces-meal-kits-sides/far-eastern-sauces-ingredients/1215337189632-1215165877786-1215664046878",
                "https://groceries.asda.com/aisle/food-cupboard/cooking-sauces-meal-kits-sides/cooking-sauces/1215337189632-1215165877786-910000975569",
                "https://groceries.asda.com/aisle/food-cupboard/cooking-sauces-meal-kits-sides/cooking-sauces/1215337189632-1215165877786-910000975569",
                "https://groceries.asda.com/aisle/food-cupboard/cooking-sauces-meal-kits-sides/cooking-sauces/1215337189632-1215165877786-910000975569",
                "https://groceries.asda.com/aisle/food-cupboard/cooking-sauces-meal-kits-sides/cooking-sauces/1215337189632-1215165877786-910000975569"],

    "spread_jam": ["https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/nut-butters/1215337189632-1215685491665-1215685491669",
                    "https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/jams-curds/1215337189632-1215685491665-1215685491666",
                    "https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/marmalade/1215337189632-1215685491665-1215685491667",
                    "https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/chocolate-sweet-spreads/1215337189632-1215685491665-1215685491668",
                    "https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/honey/1215337189632-1215685491665-1215685491670",
                    "https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/marmite-yeast-extracts/1215337189632-1215685491665-1215685491672"],
    },
    "drinks" : {
    "soft_drink": ["https://groceries.asda.com/aisle/drinks/fizzy-drinks/sugar-free-diet-fizzy-drinks/1215135760614-1215166790692-1215504932514",
                    "https://groceries.asda.com/aisle/drinks/fizzy-drinks/cola/1215135760614-1215166790692-1215685911600",
                    "https://groceries.asda.com/aisle/drinks/fizzy-drinks/lemonade/1215135760614-1215166790692-1215685911603",
                    "https://groceries.asda.com/aisle/drinks/fizzy-drinks/flavoured-fizzy-drinks/1215135760614-1215166790692-1215685911604",
                    "https://groceries.asda.com/aisle/drinks/fizzy-drinks/sugar-free-diet-fizzy-drinks/1215135760614-1215166790692-1215504932514",
                    "https://groceries.asda.com/aisle/drinks/fizzy-drinks/sugar-free-diet-fizzy-drinks/1215135760614-1215166790692-1215504932514"],

    "water": ["https://groceries.asda.com/aisle/drinks/water/view-all-water/1215135760614-1215685911631-1215686011409"],
    "squash": ["https://groceries.asda.com/dept/drinks/squash-cordial/1215135760614-1215685911615"],
    "milk": ["https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/fresh-milk/1215660378320-1215339432024-1215339434886"],
    "tea": ["https://groceries.asda.com/aisle/drinks/coffee-tea-hot-chocolate/tea/1215135760614-1215686356326-1215686356332"],
    "coffee": ["https://groceries.asda.com/aisle/drinks/coffee-tea-hot-chocolate/coffee/1215135760614-1215686356326-1215686356343"],
    "beer_cider": ["https://groceries.asda.com/aisle/beer-wine-spirits/beer-lager-ales/view-all-beer-lager-ales/1215685911554-1215345814764-1215686251329",
                    "https://groceries.asda.com/aisle/beer-wine-spirits/cider/view-all-cider/1215685911554-1215685961787-1215686021230"],
    "alc_free": ["https://groceries.asda.com/aisle/beer-wine-spirits/no-low-alcohol/no-low-alcohol-beer/1215685911554-1215685261243-1215448148934",
                "https://groceries.asda.com/aisle/beer-wine-spirits/no-low-alcohol/no-low-alcohol-cider/1215685911554-1215685261243-1215685971337"],
    "spirit": ["https://groceries.asda.com/aisle/beer-wine-spirits/spirits/gin/1215685911554-1215685911575-1215685911574",
                "https://groceries.asda.com/aisle/beer-wine-spirits/spirits/vodka/1215685911554-1215685911575-1215685911577",
                "https://groceries.asda.com/aisle/beer-wine-spirits/spirits/whisky/1215685911554-1215685911575-1215685911576",
                "https://groceries.asda.com/aisle/beer-wine-spirits/spirits/rum/1215685911554-1215685911575-1215685911578",
                "https://groceries.asda.com/aisle/beer-wine-spirits/spirits/brandy-cognac/1215685911554-1215685911575-1215685911579",
                "https://groceries.asda.com/aisle/beer-wine-spirits/spirits/tequila/1215685911554-1215685911575-1215685911584",
                "https://groceries.asda.com/aisle/beer-wine-spirits/spirits/port-sherry-vermouth/1215685911554-1215685911575-910000975511"],
    "wine": ["https://groceries.asda.com/aisle/beer-wine-spirits/wine/all-wine/1215685911554-1215345814806-1215685911557"]
    }
}

# Generalized CSS selectors for product data
'''
* acts as a wildcard, allowing the selector to match both span and div elements within co-item__price-container.
strong at the end ensures that it captures the actual price within both regular and discounted price containers.
'''

#product_box_CSS = '#main-content > main > div:nth-child(7) div[class*="co-product-list"] > ul > li'
product_box_CSS = '#main-content > main div.co-product-list:not([data-type="personalized-recommendation"]) ul.co-product-list__main-cntr > li'
product_name_CSS = 'div[class*="co-product-list"] li div[class*="co-item__col2"] div[class*="co-item__title-container"] h3 a'
product_price_CSS = 'div[class*="co-item__price-container"] strong.co-product__price'
product_price_per_unit_CSS = 'div[class*="co-product-list"] li div[class*="co-item__col3"] div[class*="co-item__price-container"] :is(span p span, div p span)'
next_button_CSS = 'div[class*="page-navigation"] a[class*="co-pagination__arrow--right"]'
disabled_next_button_CSS = 'div[class*="page-navigation"] a[class*="co-pagination__arrow--right co-pagination__arrow--disabled"]'


#accept_cookies_button_CSS = '#onetrust-accept-btn-handler'

# List to hold all product data
all_products = []
current_date = datetime.now().strftime("%Y-%m-%d")




# Loop through each category and URL in the category URLs dictionary
for main_category, subcategories in category_urls.items():
    for subcategory, urls in subcategories.items():
        for url in urls:  # Loop through each URL for the current category
            driver.get(url)
            
            try:
                # Scroll to trigger lazy-loaded content
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

                # Wait for at least one product name to appear
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, product_name_CSS))
                )

            except Exception as e:
                print(f"Skipping {subcategory} due to timeout: {e}")
                continue  # Skip this subcategory and move to the next

            while True:
                time.sleep(3)  # Allow JavaScript-rendered products to load
                product_boxes = driver.find_elements(By.CSS_SELECTOR, product_box_CSS)
                print(f"Found {len(product_boxes)} products for {subcategory}")

                if not product_boxes:
                    print(f"No products found for {subcategory}, skipping...")
                    break  # Skip if no products are detected

                for product in product_boxes:
                    try:
                        # Extract product name safely
                        product_name = product.find_element(By.CSS_SELECTOR, product_name_CSS).text if product.find_elements(By.CSS_SELECTOR, product_name_CSS) else 'null'

                        # Extract price safely
                        price_elements = product.find_elements(By.CSS_SELECTOR, product_price_CSS)
                        price = price_elements[0].text.strip().replace('now', '').strip() if price_elements else 'null'

                        # Extract price per unit safely
                        price_per_unit_elements = product.find_elements(By.CSS_SELECTOR, product_price_per_unit_CSS)
                        price_per_unit = price_per_unit_elements[0].text.strip() if price_per_unit_elements else 'null'

                        # Append product data
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
                        continue  # Move to the next product safely

                # Check if there is a "Next" button available and enabled
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, next_button_CSS))
                    )

                    # Scroll "Next" button into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(1)

                    # Wait for the button to be clickable
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_CSS))
                    )

                    # Check if the "Next" button is disabled
                    if "disabled" in next_button.get_attribute("class") or "co-pagination__arrow--disabled" in next_button.get_attribute("class"):
                        print(f"Last page reached for category: {main_category} - {subcategory}")
                        break  # Exit the loop

                    # Click the "Next" button with retries
                    click_attempts = 0
                    while click_attempts < 3:
                        try:
                            next_button.click()
                            time.sleep(5)  # Wait for the next page to load
                            print("Clicked next button.")
                            break
                        except Exception:
                            print(f"Attempt {click_attempts + 1}: Click intercepted, retrying...")
                            time.sleep(1)
                            click_attempts += 1

                    else:
                        print("Failed to click the next button after multiple attempts.")
                        break

                except Exception as e:
                    print(f"Error while clicking next button: {e}")
                    break  # Exit the loop on any exception

# Create DataFrame from the list
df_products = pd.DataFrame(all_products)

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
csv_file_path = os.path.join(desktop_path, f"Asda_{current_date}.csv")
df_products.to_csv(csv_file_path, index=False, encoding='utf-8')

# Close the browser
driver.quit()

print(f"Data saved to {csv_file_path}")