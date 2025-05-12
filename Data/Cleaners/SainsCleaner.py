#Double check missing values

import pandas as pd
import re
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import time
import os
from datetime import datetime
from tkinter import *
from tkinter.filedialog import askopenfilename

Tk().withdraw()
print("Please select a csv file to load") 
file = askopenfilename()
df = pd.read_csv(file)
df.insert(df.columns.get_loc('Price') + 1, 'Discount price', None)


df['Store_Name'] = "Sainsburys"
''' 
    Splitting the date into three columns.
        Convert 'Date' column to datetime format (this automatically handles the conversion to day, month, and year)
        Split the 'Date' column into individual components: Year, Month, Day
        Drop the original 'Date' column if it's no longer needed
'''
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df = df.drop(columns=['Date'])

'''
    Cleaning the Price.
'''

def clean_price(value):
    """
    Cleans the Price column by:
    - Handling pence (e.g., '90p / kg' or '90p') by removing 'p' and dividing by 100.
    - Handling pounds (e.g., '£2.50') by removing '£' and converting to float.
    - Extracting only the numeric value before '/' if such a case exists.
    """
    if isinstance(value, str):  # Ensure the value is a string
        if '/' in value:  # Special case: '90p / kg'
            value = value.split('/')[0].strip()  # Take only the part before '/'
        
        if 'p' in value:  # Case for pence
            return float(value.replace('p', '').strip()) / 100
        elif '£' in value:  # Case for pounds
            return float(value.replace('£', '').strip())
    return np.nan  # Return NaN for invalid or missing values

# Apply the cleaning function to the 'Nectar price' column
df['Discount price'] = df['Nectar price'].apply(clean_price)

# Drop the original 'Nectar price' column after extraction
df.drop(columns=['Nectar price'], inplace=True)

# Apply the cleaning function to the 'Nectar price' column
df['Price'] = df['Price'].apply(clean_price)

'''
    Cleaning the Price per unit and standardising the units into three(each,litre,kg).
        Function to clean and standardize the price per unit
        There was issue with pence. Some of the price was written like 0.70p instead of in pounds.
        Also typos like £12.00 typo was written like 12,000.00 which nearly f ed up my code.
        Also litre was written lt and there was cases where there was 10g lol and cl was written c3
        ugly ahh data

'''
def standardize_price_per_unit(price_per_unit):
    if isinstance(price_per_unit, str):  # Ensure the value is a string
        if '/' in price_per_unit:
            try:
                price_value, unit = price_per_unit.split(' / ')  # Split into price and unit

                # Handle price values with 'p' and '£'
                if 'p' in price_value:
                    if '.' not in price_value:
                        price_value = f"{float(price_value.replace('p', '').strip()) / 100:.3f}"  # Convert pence to pound
                    else:
                        price_value = price_value.replace('p', '')  # Remove 'p' if already in decimal form
                price_value = float(price_value.replace('£', '').strip())  # Convert price to float and remove '£'

                # Unit conversions and categorization
                if '100g' in unit:  # Convert 100g to kg
                    price_value = price_value * 10  # 100g is 0.1kg, so multiply price by 10
                    unit = 'kg'
                elif '10g' in unit:
                    price_value = price_value * 100  # 10g is 0.01kg, so multiply price by 100
                    unit = 'kg'
                elif 'kg' in unit:  # No conversion needed
                    unit = 'kg'
                elif '100ml' in unit:  # Convert 100ml to litre
                    price_value = price_value * 10  # 100ml is 0.1l, so multiply price by 10
                    unit = 'litre'
                elif 'ltr' in unit:  # No conversion needed
                    unit = 'litre'
                elif '75cl' in unit:  # Convert cl to litre
                    price_value = price_value * (4/3)  # 75cl = 0.75l
                    unit = 'litre'
                elif 'ea' in unit:  # Handle 'each'
                    unit = 'each'
                elif 'bisc' in unit:
                    unit = 'each'
                elif '1000ml' in unit:
                    unit = 'litre'
                elif '100cl' in unit:
                    unit = 'litre'
                else:
                    # If the unit is not recognized, classify it as 'other'
                    unit = 'other'

                return price_value, unit  # Return the price and standardized unit as a tuple

            except Exception as e:
                # Handle any error during processing
                return np.nan, np.nan
        else:
            return np.nan, np.nan  # Return NaN values if the format doesn't match 'per'
    else:
        return np.nan, np.nan  # Return NaN if the value is not a string
    
# Apply the function to the dataframe
df[['Standardised price per unit', 'Unit']] = df['Price per Unit'].apply(
    lambda x: pd.Series(standardize_price_per_unit(x))
)

# Filter out invalid unit values (only keep valid units)
df = df[df['Unit'].isin(['kg', 'litre', 'each',])]

# One-hot encode the 'Unit' column
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')  # Avoid errors for unknown units
unit_encoded = encoder.fit_transform(df[['Unit']])

# Create new columns based on one-hot encoding
unit_columns = encoder.get_feature_names_out(['Unit'])
df[unit_columns] = unit_encoded

# Drop the original 'Unit' and 'Price per Unit' columns
df.drop(columns=['Unit', 'Price per Unit'], inplace=True)

'''
    Saving the clean data.
'''

# Replace empty strings with NaN (NULL equivalent in PostgreSQL)
df.replace("", pd.NA, inplace=True)


desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = os.path.join(desktop_path, f"Sainsburys_Clean_{current_date}.csv")
df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data saved to {csv_file_path}")
