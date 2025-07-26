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

st.title("📊 Çmimi Aktual, RSI dhe Sinjali për Coinet")

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
        "days": "30",  # 30 ditë historik
        "interval": "daily"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    prices = response.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["price"] = df["price"].astype(float)
    return df

def get_signal(rsi):
    if isinstance(rsi, float):
        if rsi < 30:
            return "🟢 Bli"
        elif rsi > 70:
            return "🔴 Shit"
        else:
            return "🟡 Mbaj"
    else:
        return "❓ N/A"

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
    
    signal = get_signal(rsi_value if isinstance(rsi_value, float) else None)

    if price is not None:
        rows.append({
            "Coin": name,
            "Çmimi aktual (USD)": f"${price}",
            "RSI (14 ditë)": rsi_value,
            "Sinjali": signal
        })
    else:
        rows.append({
            "Coin": name,
            "Çmimi aktual (USD)": "Nuk u morën të dhënat",
            "RSI (14 ditë)": rsi_value,
            "Sinjali": signal
        })

df = pd.DataFrame(rows)
st.table(df)
st.caption("🔄 Të dhënat rifreskohen çdo 10 minuta. Burimi: CoinGecko | RSI bazuar në çmimet ditore të 30 ditëve.")
