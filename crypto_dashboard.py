import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk"
}

st.set_page_config(page_title="📈 RSI dhe Çmimi Aktual", layout="centered")
st.title("📊 Çmimi Aktual dhe RSI për Coinet")

@st.cache_data(ttl=300)
def get_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "2", "interval": "hourly"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        prices = response.json().get("prices", [])
        if not prices:
            return None
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except requests.exceptions.RequestException:
        return None

def calculate_rsi(df, window=14):
    if df is None or len(df) < window:
        return None
    rsi = RSIIndicator(close=df["price"], window=window).rsi()
    return round(rsi.iloc[-1], 2)

def get_signal(rsi):
    if rsi is None:
        return "❓ Nuk ka të dhëna"
    elif rsi < 30:
        return "🟢 Bli"
    elif rsi > 70:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

for name, coin_id in coins.items():
    st.markdown(f"### {name}")
    df = get_price_history(coin_id)
    if df is not None:
        price = round(df["price"].iloc[-1], 6)
        rsi = calculate_rsi(df)
        signal = get_signal(rsi)
        st.write(f"💰 **Çmimi aktual:** ${price}")
        st.write(f"📈 **RSI:** {rsi if rsi is not None else 'N/A'}")
        st.write(f"📊 **Sinjali:** {signal}")
    else:
        st.warning("⚠️ Nuk u morën të dhënat. CoinGecko mund të jetë offline ose ka problem lidhjeje.")

st.caption("🔄 Të dhënat rifreskohen çdo 5 minuta. Burimi: CoinGecko")
