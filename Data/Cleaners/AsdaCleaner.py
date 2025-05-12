#Approved working.

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
df['Discount price'] = None
df['Store_Name'] = "Asda"


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
        Remove the '£' sign and convert to float

'''
df['Price'] = df['Price'].replace('£', '', regex=True).astype(float)

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
        
        # Remove any parentheses around the price value (if present)
        price_per_unit = price_per_unit.replace('(', '').replace(')', '')
        
        # Remove the 'was' keyword and any leading/trailing whitespace or line breaks
        price_per_unit = price_per_unit.lower().replace('was', '').strip()

        # Split into price and unit if '/' is in the string
        if '/' in price_per_unit:
            try:
                price_value, unit = price_per_unit.split('/')  # Split into price and unit
                
                # Remove any commas in the price (to handle values like '12,000.00')
                price_value = price_value.replace(',', '')  # Remove commas for thousands
                
                # If the price has a 'p' (e.g., '15.7p'), remove it and convert to pounds (e.g., '15.7p' -> '0.0157')
                if 'p' in price_value:
                    price_value = float(price_value.replace('p', '').strip()) / 100  # Convert pence to pound
                elif '£' in price_value:
                    price_value = float(price_value.replace('£', '').strip())  # Convert price to float and remove '£'
                
                # Unit conversions based on the specific units
                if '100g' in unit:  # Convert 100g to kg
                    price_value = price_value * 10  # 100g is 0.1kg, so we multiply price by 10
                    unit = 'kg'
                elif '10g' in unit:
                    price_value = price_value * 100  # 10g to kg
                    unit = 'kg'
                elif 'kg' in unit:  # No conversion needed
                    unit = 'kg'
                elif '100ml' in unit:  # Convert 100ml to litre
                    price_value = price_value * 10  # 100ml is 0.1l, so we multiply price by 10
                    unit = 'litre'
                elif 'lt' in unit:  # No conversion needed
                    unit = 'litre'
                elif '75c3' in unit:  # Convert cl to litre (e.g., 75cl to 0.75l)
                    price_value = price_value / 10  # 75cl = 0.75l, so divide by 10
                    unit = 'litre'
                elif 'each' in unit:  # Handle 'each' (e.g., '5.20 each')
                    unit = 'each'

                # Handle edge case for prices like '12,000.00' (typo, should be '12.00')
                if price_value > 1000:
                    price_value = price_value / 1000  # Fix the typo, converting to correct value (e.g., 12000 becomes 12.00)

                return price_value, unit
            except ValueError:
                    # Handle splitting errors
                    return np.nan, 'other'

        else:
            return np.nan, np.nan  # Handle rows without valid format
    
    else:
        return np.nan, np.nan  # If the value is not a string, return NaN for both price and unit
    
# Apply the function to the dataframe
df[['Standardised price per unit', 'Unit']] = df['Price per Unit'].apply(
    lambda x: pd.Series(standardize_price_per_unit(x))
)

# Filter out invalid unit values (only keep valid units)
df = df[df['Unit'].isin(['kg', 'litre', 'each'])]

# One-hot encode the 'Unit' column
encoder = OneHotEncoder(sparse_output = False, handle_unknown='ignore')  # Avoid errors for unknown units
unit_encoded = encoder.fit_transform(df[['Unit']])

# Create new columns based on one-hot encoding
unit_columns = encoder.get_feature_names_out(['Unit'])
df[unit_columns] = unit_encoded

# Drop the original 'Unit' and 'Price per Unit' columns
df.drop(columns=['Unit', 'Price per Unit'], inplace=True)

# Replace empty strings with NaN (NULL equivalent in PostgreSQL)
df.replace("", pd.NA, inplace=True)


'''
    Saving the clean data.
'''

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = os.path.join(desktop_path, f"Asda_Clean_{current_date}.csv")
df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data saved to {csv_file_path}")


