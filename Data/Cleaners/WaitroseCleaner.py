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

df['Store_Name'] = "Waitrose"
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

def clean_price(value):
    """
    Cleans the Price column by:
    - Handling pence (e.g., '90p / kg' or '90p') by removing 'p' and dividing by 100.
    - Handling pounds (e.g., '£2.50') by removing '£' and converting to float.
    """
    if isinstance(value, str):  # Ensure the value is a string
        value = value.strip()  # Remove any extra whitespace
        try:
            if 'p' in value:  # Case for pence
                return float(value.replace('p', '')) / 100
            elif '£' in value:  # Case for pounds
                return float(value.replace('£', ''))
        except ValueError:
            pass  # Ignore values that don't match expected formats
    return np.nan  # Return NaN for invalid or missing values

# Apply the cleaning function to the 'price' column
df['Price'] = df['Price'].apply(clean_price)

def standardize_price_per_unit(price_per_unit):
    """
    Standardizes the 'Price per unit' column:
    - Removes the prefix 'Price per unit\n'.
    - Splits price and unit where applicable.
    - Converts prices to floats, handling 'p' and '£' cases.
    - Converts units like 'each' and recognizes 'other' units explicitly.
    """
    if isinstance(price_per_unit, str):  # Ensure the input is a string
        # Remove the prefix
        price_per_unit = price_per_unit.replace('Price per unit\n', '').strip()

        try:
            if '/' in price_per_unit:  # Split into price and unit
                price_value, unit = price_per_unit.split('/')
                price_value = price_value.replace(',', '').strip()  # Remove commas and whitespace

                # Handle price values with 'p' or '£'
                if 'p' in price_value:
                    price_value = float(price_value.replace('p', '')) / 100  # Pence to pounds
                elif '£' in price_value:
                    price_value = float(price_value.replace('£', ''))  # Pounds to float

                # Standardize units
                unit = unit.strip().lower()
                if 'each' in unit:
                    unit = 'each'
                elif '100g' in unit:
                    price_value *= 10  # 100g to kg 
                    unit = 'kg'
                elif '10g' in unit:
                    price_value *= 100  # 10g to kg
                    unit = 'kg'
                elif 'kg' in unit:
                    unit = 'kg'
                elif '100ml' in unit:
                    price_value *= 10  # 100ml to litre
                    unit = 'litre'
                elif 'litre' in unit:
                    unit = 'litre'
                elif 'cl' in unit:
                    price_value *= (4/3)  # Convert cl to litre
                    unit = 'litre'
                else:
                    unit = 'other'  # Unhandled units

                return price_value, unit

            elif 'each' in price_per_unit:  # Handle cases like '63.8p each' or '£5 each'
                price_value = price_per_unit.replace('each', '').strip()
                if 'p' in price_value:
                    price_value = float(price_value.replace('p', '')) / 100
                elif '£' in price_value:
                    price_value = float(price_value.replace('£', ''))
                return price_value, 'each'

            else:  # Handle unexpected formats
                return np.nan, 'other'
        except (ValueError, IndexError):
            return np.nan, 'other'  # Return defaults for malformed entries

    return np.nan, np.nan  # Return defaults for non-string inputs

#Apply the function to 'Price per Unit' column
df[['Standardised price per unit', 'Unit']] = df['Price per Unit'].apply(
    lambda x: pd.Series(standardize_price_per_unit(x))
)

# Filter out invalid unit values (anything not 'kg', 'litre', or 'each')
df = df[df['Unit'].isin(['kg', 'litre', 'each'])]

# One-hot encode the 'Unit' column
encoder = OneHotEncoder(sparse=False, drop='if_binary')  # Drop 'unit_nan' column if it exists
unit_encoded = encoder.fit_transform(df[['Unit']])

# Create new columns based on one-hot encoding
unit_columns = encoder.get_feature_names_out(['Unit'])
df[unit_columns] = unit_encoded

# Drop the original 'Unit' and 'Price per Unit' columns, as they're no longer needed
df.drop(columns=['Unit', 'Price per Unit'], inplace=True)

'''
    Saving the clean data.
'''
desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = os.path.join(desktop_path, f"Waitrose_Clean_{current_date}.csv")
df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data saved to {csv_file_path}")