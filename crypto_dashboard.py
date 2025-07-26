import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk"
}

st.title("📊 Çmimi Aktual dhe RSI për Coinet")

@st.cache_data(ttl=600)
def get_prices(coin_ids):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=600)
def get_historical_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "30",  # 30 days history
        "interval": "daily"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    prices = response.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["price"] = df["price"].astype(float)
    return df

try:
    current_prices = get_prices(list(coins.values()))
except requests.exceptions.RequestException as e:
    st.error(f"Gabim API: {e}")
    current_prices = {}

rows = []
for name, coin_id in coins.items():
    price = current_prices.get(coin_id, {}).get("usd")
    try:
        hist_df = get_historical_prices(coin_id)
        rsi = RSIIndicator(close=hist_df["price"]).rsi().iloc[-1]
        rsi_value = round(rsi, 2)
    except Exception:
        rsi_value = "Nuk u llogarit"
    
    if price is not None:
        rows.append({
            "Coin": name,
            "Çmimi aktual (USD)": f"${price}",
            "RSI (14 ditë)": rsi_value
        })
    else:
        rows.append({
            "Coin": name,
            "Çmimi aktual (USD)": "Nuk u morën të dhënat",
            "RSI (14 ditë)": rsi_value
        })

df = pd.DataFrame(rows)
st.table(df)
st.caption("🔄 Të dhënat rifreskohen çdo 10 minuta. Burimi: CoinGecko | RSI përllogaritet nga çmimet ditore të 30 ditëve.")
