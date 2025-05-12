#Double check missing values

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import re
import numpy as np
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


df['Store_Name'] = "Tesco"
''' 
    This part One hot Encodes the Categorical Columns.

        Initialize the OneHotEncoder
        Fit and transform the 'Category' and 'Subcategory' columns together
        Get the feature names for the transformed data
        Convert the encoded result to a DataFrame with correct column names
        Drop the original 'Category' and 'Subcategory' columns from the DataFrame
        Concatenate the one-hot encoded DataFrame with the original DataFrame

    encoder = OneHotEncoder(sparse=False)
    encoded = encoder.fit_transform(df[['Category', 'Subcategory']])
    encoded_columns = encoder.get_feature_names_out(['Category', 'Subcategory'])
encoded_df = pd.DataFrame(encoded, columns=encoded_columns)
df = df.drop(columns=['Category', 'Subcategory'])
df = pd.concat([df, encoded_df], axis=1)
'''

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
# Cleaning the Price: remove £ and commas, then convert to float
df['Price'] = df['Price'].replace('£', '', regex=True).replace(',', '', regex=True).astype(float)



# Apply the cleaning function to the 'Nectar price' column
df['Discount price'] = df['Clubcard Discount']

# Drop the original 'Nectar price' column after extraction
df.drop(columns=['Clubcard Discount'], inplace=True)
'''
    Cleaning the Price per unit and standardising the units into three(each,litre,kg).
        Function to clean and standardize the price per unit
'''
# Function to clean and standardize the price per unit
def standardize_price_per_unit(price_per_unit):
    if pd.isna(price_per_unit):  # Check for NaN values
        return np.nan, np.nan

    if isinstance(price_per_unit, str):  
        price_per_unit = price_per_unit.lstrip('£')  
        try:
            price_value, unit = price_per_unit.split('/')  
            price_value = float(price_value.replace(',', ''))  # Remove commas and convert to float
        except ValueError:
            return np.nan, np.nan  # Return NaN if conversion fails

        # Handle different units
        if '100g' in unit:  # Convert 100g to kg (100g = 0.1kg, multiply by 10)
            price_value = price_value * 10  # Multiply by 10 to get price per kg
            unit = 'kg'
        elif 'cl' in unit and '75cl' in unit:  # Convert 75cl to litre (75cl = 0.75l, multiply by 4/3)
            price_value = price_value * (4 / 3)  # Multiply by 4/3 to get price per litre
            unit = 'litre'
        elif '100ml' in unit:
            price_value *= 10
            unit = 'litre'
        elif '10g' in unit:
            price_value *= 100
            unit = 'kg'
        elif 'kg' in unit:  # No conversion needed for kg
            unit = 'kg'
        elif 'litre' in unit:  # No conversion needed for litre
            unit = 'litre'
        elif 'each' in unit:  # No conversion needed for 'each'
            unit = 'each'
        else:
            unit ='other'
        return price_value, unit
    else:
        return np.nan, np.nan  # If the value is not a string, return NaN for both price and unit


# Apply the function to the dataframe
df[['Standardised price per unit', 'Unit']] = df['Price per Unit'].apply(lambda x: pd.Series(standardize_price_per_unit(x)))

# Filter out invalid unit values (anything not 'kg', 'litre', or 'each')
df = df[df['Unit'].isin(['kg', 'litre', 'each'])]

# One-hot encode the 'Unit' column
encoder = OneHotEncoder(sparse_output=False, drop='if_binary')  # Drop 'unit_nan' column if it exists
unit_encoded = encoder.fit_transform(df[['Unit']])

# Create new columns based on one-hot encoding
unit_columns = encoder.get_feature_names_out(['Unit'])
df[unit_columns] = unit_encoded

# Drop the original 'Unit' and 'Price per Unit' columns, as they're no longer needed
df.drop(columns=['Unit', 'Price per Unit'], inplace=True)

# Replace empty strings with NaN (NULL equivalent in PostgreSQL)
df.replace("", pd.NA, inplace=True)


'''
    Saving the clean data.
'''

desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = os.path.join(desktop_path, f"Tesco_Clean_{current_date}.csv")
df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data saved to {csv_file_path}")
