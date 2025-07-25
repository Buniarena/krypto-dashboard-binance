import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator

st.title("Çmimet dhe Analizat RSI për BTC, XRP dhe DOGE")

coins = {
    "Bitcoin": "bitcoin",
    "XRP": "ripple",
    "Dogecoin": "dogecoin"
}

def fetch_current_price(coin_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data[coin_id]["usd"]
    except Exception as e:
        st.error(f"Gabim në marrjen e çmimit për {coin_id}: {e}")
        return None

def fetch_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "daily"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        st.error(f"Gabim në marrjen e historikut për {coin_id}: {e}")
        return None

for name, coin_id in coins.items():
    st.subheader(name)
    price = fetch_current_price(coin_id)
    if price:
        st.write(f"💰 Çmimi aktual: ${price}")
        df = fetch_price_history(coin_id)
        if df is not None:
            df["RSI"] = RSIIndicator(df["price"], window=14).rsi()
            last_rsi = df["RSI"].iloc[-1]
            if last_rsi < 30:
                st.success(f"📈 Sinjal RSI: BLEJ (RSI = {last_rsi:.2f})")
            elif last_rsi > 70:
                st.error(f"📉 Sinjal RSI: SHIT (RSI = {last_rsi:.2f})")
            else:
                st.info(f"⏸ Sinjal RSI: NEUTRAL (RSI = {last_rsi:.2f})")
            st.line_chart(df["price"])
            st.line_chart(df["RSI"])
        else:
            st.warning("Nuk mund të marrëm historikun për analizë.")
    else:
        st.warning("Nuk mund të marrëm çmimin aktual.")
