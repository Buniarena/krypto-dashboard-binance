import streamlit as st import requests import pandas as pd import ta import time

CoinGecko API endpoint

API_URL = "https://api.coingecko.com/api/v3/simple/price"

Coin list with CoinGecko IDs and symbols

coins = { "BTC": "bitcoin", "XVG": "verge", "FLOKI": "floki", "PEPE": "pepecoin-community", "VET": "vechain", "BONK": "bonk", "DOGE": "dogecoin", "SHIB": "shiba", "WIN": "wink", "BTT": "bittorrent-2" }

Set page config

st.set_page_config(page_title="Crypto Dashboard", layout="wide") st.title("Live Crypto Dashboard (CoinGecko)")

@st.cache_data(ttl=300)  # cache for 5 minutes def fetch_prices(): ids = ','.join(coins.values()) params = { 'ids': ids, 'vs_currencies': 'usd', 'include_24hr_change': 'true' } response = requests.get(API_URL, params=params) return response.json()

def display_data(data): rows = [] for symbol, coingecko_id in coins.items(): if coingecko_id in data: price = data[coingecko_id]["usd"] change = data[coingecko_id]["usd_24h_change"] rows.append({"Symbol": symbol, "Price ($)": price, "24h Change (%)": round(change, 2)})

df = pd.DataFrame(rows)
df = df.sort_values("Symbol")
st.dataframe(df, use_container_width=True)

while True: crypto_data = fetch_prices() display_data(crypto_data) time.sleep(15) st.rerun()

