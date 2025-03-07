from tkinter import *
from tkinter.filedialog import askopenfilename
import pandas as pd
from tkinter import Tk, filedialog
import os
from datetime import datetime

# Hide the root window
Tk().withdraw()

# Ask user to select multiple CSV files
print("Please select CSV files to load")
files = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])

# Ensure at least one file is selected
if not files:
    print("No files selected.")
else:
    # Read and merge all selected CSV files
    df_list = [pd.read_csv(file) for file in files]
    merged_df = pd.concat(df_list, ignore_index=True)

    # Define save path to Desktop
    desktop_path = os.path.expanduser(r"C:\Users\Entwan\Desktop")
    current_date = datetime.now().strftime("%Y-%m-%d")
    csv_file_path = os.path.join(desktop_path, f"Merged_{current_date}.csv")
    # Save merged CSV
    merged_df.to_csv(csv_file_path, index=False,encoding='utf-8')
    print(f"Merged CSV saved at: {csv_file_path}")
    