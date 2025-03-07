import streamlit as st
import mysql.connector
import pandas as pd

st.title("Hello World 👋")

connection = mysql.connector.connect(
    host = '127.0.0.1:3306',
    user = 'root',
    password = 'lkjH0987@',
    database = 'products'
)

print('connected')

cursor = connection.cursor()

cursor.execute("SELECT * FROM products.product")
data = cursor.fetchall()

df = pd.DataFrame(data, columns=cursor.column_names)
st.dataframe(df)
