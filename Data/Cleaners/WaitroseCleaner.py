import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import os
from datetime import datetime
from tkinter import Tk, filedialog

# Hide the root window
Tk().withdraw()

print("Please select a CSV file to load") 
file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

# Load CSV
df = pd.read_csv(file)

# Add 'Discount price' column after 'Price', ensuring it's properly initialized
df.insert(df.columns.get_loc('Price') + 1, 'Discount price', np.nan)

df['Store_Name'] = "Waitrose"

''' 
    Splitting the Date column into Year, Month, and Day.
'''
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Convert date safely
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df.drop(columns=['Date'], inplace=True)  # Drop original Date column

''' 
    Cleaning the Price column.
    - Convert '£' values to float.
    - Convert '90p' to 0.90 format.
'''
def clean_price(value):
    if isinstance(value, str):
        value = value.strip()
        try:
            if 'p' in value:  
                return float(value.replace('p', '').strip()) / 100  # Convert pence to pounds
            elif '£' in value:  
                return float(value.replace('£', '').strip())  # Remove currency symbol and convert
        except ValueError:
            pass
    return np.nan  # Convert missing/invalid values to NaN

df['Price'] = df['Price'].apply(clean_price)

'''
    Cleaning and Standardizing 'Price per unit'
    - Convert 100g to kg
    - Convert 100ml to litre
    - Normalize units
'''
def standardize_price_per_unit(value):
    if isinstance(value, str):
        value = value.replace('Price per unit\n', '').strip()  # Remove unwanted prefix

        try:
            if '/' in value:  # Format: "£5.00 / kg"
                price_value, unit = value.split('/')
                price_value = price_value.replace(',', '').strip()

                # Convert price value
                if 'p' in price_value:
                    price_value = float(price_value.replace('p', '').strip()) / 100
                elif '£' in price_value:
                    price_value = float(price_value.replace('£', '').strip())

                # Standardize unit
                unit = unit.strip().lower()
                if '100g' in unit:
                    price_value *= 10  # Convert 100g to kg
                    unit = 'kg'
                elif '10g' in unit:
                    price_value *= 100  # Convert 10g to kg
                    unit = 'kg'
                elif 'kg' in unit:
                    unit = 'kg'
                elif '100ml' in unit:
                    price_value *= 10  # Convert 100ml to litre
                    unit = 'litre'
                elif 'litre' in unit:
                    unit = 'litre'
                elif 'cl' in unit:
                    price_value *= (4/3)  # Convert cl to litre
                    unit = 'litre'
                elif 'each' in unit:
                    unit = 'each'
                else:
                    unit = 'other'  

                return price_value, unit

            elif 'each' in value:  
                price_value = value.replace('each', '').strip()
                if 'p' in price_value:
                    price_value = float(price_value.replace('p', '').strip()) / 100
                elif '£' in price_value:
                    price_value = float(price_value.replace('£', '').strip())
                return price_value, 'each'

        except (ValueError, IndexError):
            return np.nan, 'other'

    return np.nan, np.nan

# Apply function to standardize 'Price per Unit'
df[['Standardised price per unit', 'Unit']] = df['Price per Unit'].apply(
    lambda x: pd.Series(standardize_price_per_unit(x))
)

# Keep only valid units
df = df[df['Unit'].isin(['kg', 'litre', 'each'])]

'''
    Handling NaN values in numeric columns
    - Fill missing values with NULL equivalent (NaN)
    - Ensure data types are correct for PostgreSQL
'''
numeric_columns = ['Price', 'Standardised price per unit']

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Force numeric type

# Drop 'Discount price' if it's completely empty
if df['Discount price'].isna().all():
    df.drop(columns=['Discount price'], inplace=True)

'''
    One-Hot Encoding for 'Unit' Column
'''
encoder = OneHotEncoder(sparse=False, drop='if_binary')
unit_encoded = encoder.fit_transform(df[['Unit']])
unit_columns = encoder.get_feature_names_out(['Unit'])
df[unit_columns] = unit_encoded
df.drop(columns=['Unit', 'Price per Unit'], inplace=True)  # Remove original Unit columns

# Ensure 'Discount price' exists and is explicitly kept
if 'Discount price' not in df.columns:
    df['Discount price'] = np.nan  # Recreate the column if missing

# Drop only rows where 'Price' or 'Standardised price per unit' is NULL
df.dropna(subset=['Price', 'Standardised price per unit'], inplace=True)

# Ensure 'Discount price' remains, even if it's all NaN
df['Discount price'] = df['Discount price'].astype(float)  # Keep as numeric column


'''
    Saving the Cleaned Data
'''
desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
csv_file_path = os.path.join(desktop_path, f"Waitrose_Clean_{current_date}.csv")

df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data saved to {csv_file_path}")
