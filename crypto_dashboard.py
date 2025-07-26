import streamlit as st
import requests
import pandas as pd
import ta

st.set_page_config(page_title="BTC RSI", layout="centered")
st.title("📈 BTC Dashboard me RSI & Moving Averages")

API_URL = "https://api.coingecko.com/api/v3"
coin_id = "bitcoin"

@st.cache_data(ttl=300)
def fetch_price():
    url = f"{API_URL}/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data.get(coin_id, {})
    else:
        return {}

@st.cache_data(ttl=300)
def fetch_market_data(days=90):
    url = f"{API_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
    }
    r = requests.get(url)
    if r.status_code != 200:
        return pd.DataFrame()
    prices = r.json().get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["rsi"] = ta.momentum.RSIIndicator(df["price"], window=14).rsi()
    df["ma50"] = df["price"].rolling(window=50).mean()
    df["ma200"] = df["price"].rolling(window=200).mean()
    return df.dropna()

# Ngarko të dhënat
price_data = fetch_price()
market_df = fetch_market_data()

if price_data and not market_df.empty:
    current_price = price_data.get("usd", 0)
    change_24h = price_data.get("usd_24h_change", 0)
    latest_rsi = market_df["rsi"].iloc[-1]
    ma50 = market_df["ma50"].iloc[-1]
    ma200 = market_df["ma200"].iloc[-1]

    trend = "📈 Bullish" if ma50 > ma200 else "📉 Bearish"

    if latest_rsi < 30 and trend == "📈 Bullish":
        signal = "🚀 Bli"
    elif latest_rsi > 70 and trend == "📉 Bearish":
        signal = "⚠️ Shit"
    else:
        signal = "➡️ Mbaj"

    st.metric("💰 Çmimi BTC", f"${current_price:,.2f}", f"{change_24h:.2f}% / 24h")
    st.markdown(f"**RSI:** `{latest_rsi:.2f}` | **Trend:** {trend} | **{signal}**")
    st.line_chart(market_df[["price", "ma50", "ma200"]])

else:
    st.error("❌ Nuk u ngarkuan të dhënat. Kontrollo lidhjen ose API-në.")
