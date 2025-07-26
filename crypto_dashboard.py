import streamlit as st
import pandas as pd
import requests
import time
from ta.momentum import RSIIndicator

st.set_page_config(page_title="Live Crypto Dashboard", layout="centered")
st.markdown("<h1 style='text-align:center; color:#60A5FA;'>📊 ARENA BUNI - Live Crypto Dashboard</h1>", unsafe_allow_html=True)

coins = {
    "BTC": "bitcoin",
    "XVG": "verge",
    "BONK": "bonk",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu"
}

def fetch_market_data(ids):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": ",".join(ids), "price_change_percentage": "24h"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_hourly_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "hourly"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    prices = resp.json()["prices"]
    df = pd.DataFrame(prices, columns=["ts", "price"])
    df["price"] = df["price"].astype(float)
    return df

rows = []
try:
    market = fetch_market_data(list(coins.values()))
    for coin in market:
        symbol = coin["symbol"].upper()
        price = coin["current_price"]
        change24 = coin.get("price_change_percentage_24h", 0.0)

        hist = fetch_hourly_prices(coin["id"])
        rsi = RSIIndicator(hist["price"]).rsi().iloc[-1]
        rsi = round(rsi,2)

        rows.append({
            "Symbol": symbol,
            "Price ($)": price,
            "24h Change (%)": change24,
            "RSI (24h, 14)": rsi
        })
except requests.exceptions.RequestException as e:
    st.error(f"❌ Gabim API: {e}")

if rows:
    df = pd.DataFrame(rows)
    def style_rsi(v):
        if v < 30:
            return "background-color:#ffcccc"
        if v > 70:
            return "background-color:#ccffcc"
        return ""
    st.dataframe(df.style.applymap(style_rsi, subset=["RSI (24h, 14)"]).set_precision(2), use_container_width=True)

    st.markdown("<p style='text-align:center; color:#aaa;'>💡 Të dhënat merren nga CoinGecko. RSI mes <30 (oversold), >70 (overbought).</p>", unsafe_allow_html=True)
