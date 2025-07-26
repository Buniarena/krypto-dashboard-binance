import streamlit as st
import pandas as pd
import requests
import ta

# Titulli dhe përshkrimi
st.set_page_config(page_title="Live Crypto Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>📊 ARENA BUNI - Live Crypto Dashboard</h1>", unsafe_allow_html=True)

# Lista e kriptovalutave që duam të shfaqim
coins = ["bitcoin", "xvg", "floki", "vet", "bonk", "dogecoin", "shiba-inu", "wink"]

# Marrja e të dhënave nga CoinGecko
url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(coins)}&price_change_percentage=24h"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    # Përgatitja e dataframe
    df = pd.DataFrame([{
        "Symbol": coin["symbol"].upper(),
        "Price ($)": coin["current_price"],
        "24h Change (%)": round(coin["price_change_percentage_24h"], 2)
    } for coin in data])

    # Vendosje vlerave të RSI fiktivisht për ilustrim
    df["RSI"] = [65, 25, 75, 45, 30, 70, 50, 35]  # Shembull

    # Ngjyrosje për RSI nën 30 ose mbi 70
    def color_rsi(val):
        if val < 30:
            return "background-color: #ffcccc"  # e kuqe e lehtë
        elif val > 70:
            return "background-color: #ccffcc"  # e gjelbër e lehtë
        return ""

    # Shfaqja e tabelës
    st.dataframe(df.style.applymap(color_rsi, subset=["RSI"]), use_container_width=True)

    st.markdown("💡 Të dhënat merren nga CoinGecko pa rifreskim automatik.")
else:
    st.error("❌ Nuk u morën të dhënat nga CoinGecko.")
