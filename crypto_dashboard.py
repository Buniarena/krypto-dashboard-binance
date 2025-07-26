import streamlit as st
import requests
import pandas as pd
import ta

# Konfigurimi fillestar
st.set_page_config(page_title="BTC RSI Dashboard", layout="centered")
st.title("📊 BTC Live RSI & Trend (CoinGecko)")

API_URL = "https://api.coingecko.com/api/v3"
coin_id = "bitcoin"

@st.cache_data(ttl=300)
def fetch_price():
    params = {
        'ids': coin_id,
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    r = requests.get(f"{API_URL}/simple/price", params=params)
    return r.json().get(coin_id, {})

@st.cache_data(ttl=300)
def fetch_market_data(days=90):
    url = f"{API_URL}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    res = requests.get(url)
    data = res.json()
    prices = data.get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["rsi"] = ta.momentum.rsi(df["price"], window=14)
    df["ma50"] = df["price"].rolling(window=50).mean()
    df["ma200"] = df["price"].rolling(window=200).mean()
    return df.dropna()

# Merr të dhënat
price_data = fetch_price()
df = fetch_market_data()

# Paraqit të dhënat
if price_data and not df.empty:
    price = price_data.get("usd", 0)
    change = price_data.get("usd_24h_change", 0)
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

    st.metric("💰 Çmimi Aktual", f"${price:,.2f}", f"{change:.2f}% / 24h")
    st.markdown(f"**RSI:** `{latest_rsi:.2f}` | **Trend:** {trend} | {signal}")
    st.line_chart(df[["price", "ma50", "ma200"]], height=300)

else:
    st.error("Nuk u ngarkuan të dhënat. Mund të jetë problem me CoinGecko.")

st.caption("📡 Marrë nga CoinGecko • Cache 5 minuta")
