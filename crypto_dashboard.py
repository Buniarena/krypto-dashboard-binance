import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator

st.title("Çmimi dhe Analiza RSI për Shiba Inu (SHIB)")

def fetch_current_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "shiba-inu", "vs_currencies": "usd"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    return data["shiba-inu"]["usd"]

def fetch_price_history():
    url = "https://api.coingecko.com/api/v3/coins/shiba-inu/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "daily"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

current_price = fetch_current_price()
st.write(f"💰 Çmimi aktual i SHIB: ${current_price:.8f}")

df = fetch_price_history()
df["RSI"] = RSIIndicator(df["price"], window=14).rsi()

last_rsi = df["RSI"].iloc[-1]

if last_rsi < 30:
    st.success(f"📈 Sinjal RSI: BLEJ (RSI = {last_rsi:.2f})")
elif last_rsi > 70:
    st.error(f"📉 Sinjal RSI: SHIT (RSI = {last_rsi:.2f})")
else:
    st.info(f"⏸ Sinjal RSI: NEUTRAL (RSI = {last_rsi:.2f})")

st.subheader("Grafiku i Çmimit të SHIB (7 ditë)")
st.line_chart(df["price"])

st.subheader("Grafiku RSI")
st.line_chart(df["RSI"])
