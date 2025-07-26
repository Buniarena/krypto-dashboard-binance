import streamlit as st
import requests
import pandas as pd

# Emrat e coineve dhe simbolat në Binance (USDT market)
coins = {
    "Bitcoin": "BTCUSDT",
    "PEPE": "PEPEUSDT",
    "Doge": "DOGEUSDT",
    "Shiba": "SHIBUSDT",
    "Bonk": "BONKUSDT"
}

st.set_page_config(page_title="📊 Çmimi Aktual për Coinet (Binance API)", layout="centered")
st.title("📊 Çmimi Aktual për Coinet (Binance API)")

def get_binance_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        price = float(response.json().get("price", 0))
        return price
    except Exception as e:
        st.write(f"⚠️ Gabim te {symbol}: {e}")
        return None

data = []
for name, symbol in coins.items():
    price = get_binance_price(symbol)
    if price is not None:
        data.append({"Coin": name, "Çmimi aktual (USD)": f"${price:.6f}"})
    else:
        data.append({"Coin": name, "Çmimi aktual (USD)": "Nuk u morën të dhënat"})

df = pd.DataFrame(data)
st.table(df)

st.caption("🔄 Të dhënat rifreskohen çdo herë që hap aplikacionin. Burimi: Binance API")
