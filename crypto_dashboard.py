import streamlit as st import requests import pandas as pd import ta import time

CoinGecko API endpoint

API_URL = "https://api.coingecko.com/api/v3"

Coin list with CoinGecko IDs and symbols

coins = { "BTC": "bitcoin", "XVG": "verge", "FLOKI": "floki", "PEPE": "pepecoin-community", "VET": "vechain", "BONK": "bonk", "DOGE": "dogecoin", "SHIB": "shiba", "WIN": "wink", "BTT": "bittorrent-2" }

Set page config

st.set_page_config(page_title="Crypto Dashboard", layout="wide") st.title("📈 Live Crypto Dashboard me Analiza RSI & MA")

@st.cache_data(ttl=300)  # cache for 5 minutes def fetch_prices(): ids = ','.join(coins.values()) params = { 'ids': ids, 'vs_currencies': 'usd', 'include_24hr_change': 'true' } response = requests.get(f"{API_URL}/simple/price", params=params) return response.json()

@st.cache_data(ttl=300) def fetch_market_data(coin_id, days=90): url = f"{API_URL}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}" res = requests.get(url) data = res.json() prices = data.get("prices", []) df = pd.DataFrame(prices, columns=["timestamp", "price"]) df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms") df.set_index("timestamp", inplace=True) df["rsi"] = ta.momentum.rsi(df["price"], window=14) df["ma50"] = df["price"].rolling(window=50).mean() df["ma200"] = df["price"].rolling(window=200).mean() return df.dropna()

def display_data(prices): for symbol, coin_id in coins.items(): st.subheader(f"💰 {symbol.upper()}")

if coin_id not in prices:
        st.warning(f"Nuk u gjetën të dhëna për {symbol}")
        continue

    price = prices[coin_id].get("usd")
    change = prices[coin_id].get("usd_24h_change", 0)
    st.markdown(f"**Çmimi Aktual:** ${price:.6f} | **24h Ndryshim:** {change:.2f}%")

    df = fetch_market_data(coin_id)
    if df.empty:
        st.warning("Nuk u morën të dhëna historike.")
        continue

    latest_rsi = df["rsi"].iloc[-1]
    ma50 = df["ma50"].iloc[-1]
    ma200 = df["ma200"].iloc[-1]
    trend = "📈 Bullish" if ma50 > ma200 else "📉 Bearish"

    if latest_rsi < 30 and trend == "📈 Bullish":
        signal = "🚀 Sinjal: Bli"
    elif latest_rsi > 70 and trend == "📉 Bearish":
        signal = "⚠️ Sinjal: Shit"
    else:
        signal = "➡️ Sinjal: Mbaj"

    st.markdown(f"**Trend:** {trend} | **RSI:** {latest_rsi:.2f} | {signal}")
    st.line_chart(df[["price", "ma50", "ma200"]], height=250)

crypto_data = fetch_prices() if crypto_data: display_data(crypto_data) else: st.error("Nuk u mund të ngarkohen të dhënat nga CoinGecko")

st.caption("Daten via CoinGecko • Auto Refresh çdo 15s • Cache 5 min")

