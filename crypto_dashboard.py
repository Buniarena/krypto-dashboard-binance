import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator

st.title("📊 Çmimet & Analizat Teknike me RSI")

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

def fetch_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "daily"}
    r = requests.get(url, params=params)
    data = r.json()
    prices = data.get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

for name, coin_id in coins.items():
    st.subheader(name)

    try:
        # Merr çmimin live
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get(coin_id, {}).get("usd")

        if price is None:
            st.warning(f"Nuk u morën të dhëna për {name}.")
            continue

        st.write(f"Çmimi aktual: ${price}")

        # Merr historikun dhe llogarit RSI
        df = fetch_price_history(coin_id)
        df["RSI"] = RSIIndicator(df["price"], window=14).rsi()

        last_rsi = df["RSI"].iloc[-1]

        if last_rsi < 30:
            st.success(f"Sinjali RSI: BLEJ (RSI = {last_rsi:.2f})")
        elif last_rsi > 70:
            st.error(f"Sinjali RSI: SHIT (RSI = {last_rsi:.2f})")
        else:
            st.info(f"Sinjali RSI: NEUTRAL (RSI = {last_rsi:.2f})")

        st.line_chart(df["price"])

    except Exception as e:
        st.error(f"Gabim për {name}: {e}")
