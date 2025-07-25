import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator

st.title("Çmimi dhe Analiza RSI për Bitcoin")

def fetch_price_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "daily"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

# Merr çmimin aktual
def fetch_current_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    return data["bitcoin"]["usd"]

# Shfaq çmimin aktual
current_price = fetch_current_price()
st.write(f"💰 Çmimi aktual i Bitcoin është: **${current_price:.2f}**")

# Merr historikun dhe llogarit RSI
df = fetch_price_history()
df["RSI"] = RSIIndicator(df["price"], window=14).rsi()

# Sinjal bazuar tek RSI i fundit
last_rsi = df["RSI"].iloc[-1]

if last_rsi < 30:
    st.success(f"📈 Sinjal RSI: BLEJ (RSI = {last_rsi:.2f})")
elif last_rsi > 70:
    st.error(f"📉 Sinjal RSI: SHIT (RSI = {last_rsi:.2f})")
else:
    st.info(f"⏸ Sinjal RSI: MBANJE (RSI = {last_rsi:.2f})")

# Grafik çmimi dhe RSI
st.subheader("Grafiku i Çmimit të Bitcoin")
st.line_chart(df["price"])

st.subheader("Grafiku RSI")
st.line_chart(df["RSI"])
