import streamlit as st
import requests
import time

st.title("📊 Çmimet Live me Binance API")

coins = {
    "Bitcoin": "BTCUSDT",
    "Dogecoin": "DOGEUSDT",
    "XRP": "XRPUSDT"
}

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except Exception as e:
        st.error(f"Gabim te {symbol}: {e}")
        return None

placeholder = st.empty()

while True:
    prices = {}
    for name, symbol in coins.items():
        price = get_price(symbol)
        if price:
            prices[name] = price

    with placeholder.container():
        for name, price in prices.items():
            st.metric(label=name, value=f"${price:,.4f}")

    time.sleep(5)  # Merr çmimet çdo 5 sekonda
