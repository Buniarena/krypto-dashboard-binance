import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import time

st.title("📲 BTC Live me RSI & MA")

@st.cache_data(ttl=300)
def fetch_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minute"}
    headers = {"User-Agent": "TermuxCryptoApp/1.0"}
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    prices = r.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

df = fetch_data()
price = df["price"].iloc[-1]
rsi = RSIIndicator(df["price"]).rsi().iloc[-1]
ma = SMAIndicator(df["price"], window=20).sma_indicator().iloc[-1]

st.metric("💰 BTC Çmimi", f"${price:,.2f}")
st.write(f"📊 RSI: {rsi:.2f}")
st.write(f"📉 MA (20): ${ma:,.2f}")

if rsi > 70:
    st.warning("RSI: OVERBOUGHT")
elif rsi < 30:
    st.success("RSI: OVERSOLD")
else:
    st.info("RSI: NEUTRAL")

st.line_chart(df["price"])
time.sleep(15)
st.experimental_rerun()
