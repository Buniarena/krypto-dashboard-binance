import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator

st.title("Çmimet dhe Analiza RSI për BTC, ETH dhe XRP")

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "XRP": "ripple"
}

def fetch_current_price(coin_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    return data[coin_id]["usd"]

def fetch_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "daily"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

for name, coin_id in coins.items():
    st.subheader(name)
    try:
        current_price = fetch_current_price(coin_id)
        st.write(f"💰 Çmimi aktual: **${current_price:.4f}**")

        df = fetch_price_history(coin_id)
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

    except Exception as e:
        st.error(f"Nuk u morën të dhëna për {name}: {e}")
