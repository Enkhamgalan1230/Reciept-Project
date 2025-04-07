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
# Ensure 'Discount price' is after 'Price'
df.insert(df.columns.get_loc('Price') + 1, 'Discount price', None)

df['Store_Name'] = "Aldi"

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
# Apply the cleaning function to the 'Nectar price' column
df['Discount price'] = None

df['Price'] = df['Price'].replace('£', '', regex=True).astype(float)


'''
    Cleaning the Price per unit and standardising the units into three(each,litre,kg).
        Function to clean and standardize the price per unit
        There was issue with pence. Some of the price was written like 0.70p instead of in pounds.
'''

def standardize_price_per_unit(price_per_unit):
    """
    Converts price per unit to a standardised float and one of the units: 'kg', 'litre', or 'each'.
    Handles strings like '£0.75/100G', '70p/75CL', '(£0.32/75CL)', '£5 each', etc.
    """
    if isinstance(price_per_unit, str):
        # Remove wrapping parentheses and extra whitespace
        price_per_unit = price_per_unit.strip("()").strip()
        
        if '/' in price_per_unit:
            try:
                price_value, unit = price_per_unit.split('/')
                price_value = price_value.replace('£', '').replace('p', '').strip()
                unit = unit.strip().upper()
                price_value = float(price_value)
            except:
                return np.nan, 'other'

            # Convert to standard unit
            if unit in ['100G', '100GNE']:
                price_value *= 10
                unit = 'kg'
            elif unit == '10G':
                price_value *= 100
                unit = 'kg'
            elif unit in ['1KG', '1KGE', '1KNE']:
                unit = 'kg'
            elif unit == '100ML':
                price_value *= 10
                unit = 'litre'
            elif unit == '75CL':
                price_value *= (4 / 3)
                unit = 'litre'
            elif unit == '70CL':
                price_value *= (10 / 7)
                unit = 'litre'
            elif unit in ['1L', 'L']:
                unit = 'litre'
            elif unit in ['1EA', '1SHT', '1PAC']:
                unit = 'each'
            else:
                unit = 'other'
            
            return price_value, unit
        
        elif 'each' in price_per_unit.lower():
            try:
                price_value = price_per_unit.lower().replace('£', '').replace('each', '').replace('(', '').replace(')', '').strip()
                return float(price_value), 'each'
            except:
                return np.nan, 'other'
    
    return np.nan, np.nan

# Apply the function to 'Price per Unit' column
df[['Standardised price per unit', 'Unit']] = df['Price per Unit'].apply(
    lambda x: pd.Series(standardize_price_per_unit(x))
)

print(df['Unit'].value_counts())

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

# Replace empty strings with NaN (NULL equivalent in PostgreSQL)
df.replace("", pd.NA, inplace=True)

#Saving
desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = os.path.join(desktop_path, f"Aldi_Clean_{current_date}.csv")
df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data saved to {csv_file_path}")

