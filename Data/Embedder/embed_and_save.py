from tkinter import Tk, filedialog
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os
from datetime import datetime

# Hide the root window
Tk().withdraw()

# Ask user to select the merged latest CSV file
print(" Please select your merged latest CSV file")
file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

if not file_path:
    print(" No file selected.")
    exit()

# Load the merged CSV
df = pd.read_csv(file_path)
df.replace("", pd.NA, inplace=True)

# Embed the product names
product_names = df["Name"].astype(str).tolist()
model = SentenceTransformer("all-MiniLM-L6-v2")

print(f"🧠 Embedding {len(product_names)} product names...")
embeddings = model.encode(product_names, convert_to_numpy=True, show_progress_bar=True)

# Save embeddings to Desktop
desktop_path = os.path.expanduser("~/Desktop")
current_date = datetime.now().strftime("%Y-%m-%d")
embedding_file_path = os.path.join(desktop_path, f"latest_embeddings_{current_date}.npy")
np.save(embedding_file_path, embeddings)


print(f"✅ Embeddings saved to: {embedding_file_path}")