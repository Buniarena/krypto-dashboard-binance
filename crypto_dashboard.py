import streamlit as st
import requests
import pandas as pd
import time

# Konfiguro pamjen e aplikacionit
st.set_page_config(
    page_title="Live Crypto Dashboard",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Titulli
st.markdown("<h1 style='text-align: center;'>📊 Live Crypto Dashboard<br>(CoinGecko)</h1>", unsafe_allow_html=True)

# Lista e monedhave që do të shfaqim
coins = {
    "BTC": "bitcoin",
    "XVG": "verge",
    "FLOKI": "floki",
    "VET": "vechain",
    "BONK": "bonk",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "WIN": "wink"
}

def get_prices():
    prices = []
    for symbol, coingecko_id in coins.items():
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url)
        data = response.json()

        try:
            price = data[coingecko_id]["usd"]
            change = data[coingecko_id]["usd_24h_change"]
        except KeyError:
            price = 0
            change = 0

        prices.append({
            "Symbol": symbol,
            "Price ($)": round(price, 8),
            "24h Change (%)": round(change, 2)
        })

    df = pd.DataFrame(prices)
    return df

# Vendos një placeholder për tabelën që do të rifreskohet
table_placeholder = st.empty()

# Refresh çdo 15 sekonda
while True:
    df = get_prices()
    table_placeholder.dataframe(df, use_container_width=True)

    st.markdown("<p style='text-align: center;'>💡 Të dhënat përditësohen automatikisht çdo 15 sekonda • Burimi: <strong>CoinGecko</strong></p>", unsafe_allow_html=True)
    
    time.sleep(15)
