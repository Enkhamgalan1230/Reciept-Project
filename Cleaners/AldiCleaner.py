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
'''

def standardize_price_per_unit(price_per_unit):
    """
    Converts price per unit to standardized float value and unit ('kg', 'litre', 'each').
    Handles specific formats like '£5 per kg', '£5 per 100g', etc.
    """
    if isinstance(price_per_unit, str):  # Ensure the value is a string
        price_per_unit = price_per_unit.strip()  # Remove leading/trailing spaces
        
        if 'per' in price_per_unit:  # Handle 'per' formats
            
            # Split the string into price and unit
            price_value, unit = price_per_unit.split(' per ')
            price_value = price_value.strip()  # Clean whitespace
            unit = unit.strip()  # Clean whitespace
                
            if 'p' in price_value:
                price_value = float(price_value.replace('p', '').strip()) / 100  # Convert pence to pound
            elif '£' in price_value:
                price_value = float(price_value.replace('£', '').strip())  # Convert price to float and remove '£'
            
            # Handle specific unit conversions
            if '100g' in unit:  # Convert 100g to kg
                price_value *= 10  # 100g is 0.1kg
                unit = 'kg'
            elif '10g' in unit:
                price_value *= 100
                unit = 'kg'
            elif 'kg' in unit:  # No conversion needed
                unit = 'kg'
            elif '100ml' in unit:  # Convert 100ml to litre
                price_value *= 10  # 100ml is 0.1 litre
                unit = 'litre'
            elif '75cl' in unit:
                price_value *= (4 / 3) 
                unit = 'litre'
            elif 'litre' in unit:  # No conversion needed
                unit = 'litre'
            elif 'each' in unit:  # Handle 'each'
                unit = 'each'
            else:
                unit ='other'
                    
            return price_value, unit
            
        elif 'each' in price_per_unit:  # Handle '£5 each' format
            try:
                price_value = float(price_per_unit.replace('£', '').replace('each', '').strip())
                return price_value, 'each'
            except ValueError:
                return np.nan, 'other'
    
    return np.nan, np.nan  # Return NaN for invalid or missing values
# Apply the function to 'Price per Unit' column
df[['Standardised Price per Unit', 'Unit']] = df['Price per Unit'].apply(
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
csv_file_path = os.path.join(desktop_path, f"Aldi_Clean_{current_date}.csv")
df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data saved to {csv_file_path}")
