import streamlit as st
import requests

st.title("Çmimi i Bitcoin")

url = "https://api.coingecko.com/api/v3/simple/price"
params = {"ids": "bitcoin", "vs_currencies": "usd"}
response = requests.get(url, params=params)
data = response.json()
btc_price = data["bitcoin"]["usd"]

st.write(f"Çmimi aktual i Bitcoin është: ${btc_price}")
