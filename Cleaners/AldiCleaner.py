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
    if isinstance(price_per_unit, str):  # Ensure the value is a string
        
        # Split into price and unit if 'per' is in the string
        if 'per' in price_per_unit:
            price_value, unit = price_per_unit.split(' per ')  # Split into price and unit
            
            # Check if the price has a 'p' and remove it (e.g., '0.70p' becomes '£0.70')
            if 'p' in price_value:
                # If there's no decimal point, we assume it's in whole pence (e.g., '70p' -> '0.70')
                if '.' not in price_value:
                    price_value = f"£{float(price_value.replace('p', '').strip()) / 100:.2f}"
                else:
                    price_value = price_value.replace('p', '£')  # Replace 'p' with '£'
            
            price_value = float(price_value.replace('£', '').strip())  # Convert price to float and remove '£'
            
            # Unit conversions based on the specific units
            if '100g' in unit:  # Convert 100g to kg
                price_value = price_value * 10  # 100g is 0.1kg, so we multiply price by 10
                unit = 'kg'
            elif 'kg' in unit:  # No conversion needed
                unit = 'kg'
            elif '100ml' in unit:  # Convert 100ml to litre
                price_value = price_value * 10  # 100ml is 0.1l, so we multiply price by 10
                unit = 'litre'
            elif 'litre' in unit:  # No conversion needed
                unit = 'litre'
            elif 'cl' in unit:  # Convert cl to litre (e.g., 75cl to 0.75l)
                price_value = price_value / 10  # 75cl = 0.75l, so divide by 10
                unit = 'litre'
            elif 'each' in unit:  # Handle 'each' (e.g., '5.20 each')
                unit = 'each'

            return price_value, unit
        
        # Handle 'each' without 'per' (e.g., '5.20 each')
        elif 'each' in price_per_unit:  
            price_value, unit = price_per_unit.split(' each')  # Split into price and unit
            if 'p' in price_value:  # Check if 'p' is in price and replace it
                # If there's no decimal point, assume it's in whole pence (e.g., '70p' -> '0.70')
                if '.' not in price_value:
                    price_value = f"£{float(price_value.replace('p', '').strip()) / 100:.2f}"
                else:
                    price_value = price_value.replace('p', '£')  # Replace 'p' with '£'
            price_value = float(price_value.replace('£', '').strip())  # Convert price to float and remove '£'
            return price_value, 'each'

        else:
            return np.nan, np.nan  # Handle rows without valid format
    else:
        return np.nan, np.nan  # If the value is not a string, return NaN for both price and unit


# Apply the function to the dataframe
df[['Standardised price per unit', 'Unit']] = df['Price per Unit'].apply(lambda x: pd.Series(standardize_price_per_unit(x)))

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
