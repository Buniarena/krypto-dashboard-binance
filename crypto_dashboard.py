import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import time

REFRESH_INTERVAL = 180  # sekonda

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()
        st.experimental_rerun()

# Stil për telefon
st.markdown("""
<style>
body, .stApp {
    background-color: #0F172A;
    color: white;
}
h1 {
    color: #60A5FA;
}
.block {
    background-color: #1E293B;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 RSI, MACD & Sinjalet")

refresh_if_needed()

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk",
    "XVG (Verge)": "verge",
    "Dogs AI": "dogs-ai",
    "WIN": "wink",
    "SLP": "smooth-love-potion",
    "DENT": "dent",
    "SPELL": "spell-token",
    "PEOPLE": "constitutiondao"
}

@st.cache_data(ttl=REFRESH_INTERVAL)
def get_market_data(coin_ids):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coin_ids),
        "price_change_percentage": "24h"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "30",
        "interval": "daily"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()["prices"]
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["price"] = df["price"].astype(float)
    return df

def get_combined_signal(rsi, macd_diff):
    if rsi < 30 and macd_diff > 0:
        return "🟢 Bli"
    elif rsi > 70 and macd_diff < 0:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

def signal_color(signal):
    if "Bli" in signal:
        return "lightgreen"
    elif "Shit" in signal:
        return "red"
    elif "Mbaj" in signal:
        return "orange"
    return "gray"

try:
    market_data = get_market_data(list(coins.values()))
except Exception as e:
    st.error(f"Gabim në të dhëna: {e}")
    market_data = []

market_dict = {c["id"]: c for c in market_data}

for name, coin_id in coins.items():
    data = market_dict.get(coin_id)
    if not data:
        continue
    try:
        price = round(data["current_price"], 5)
        change = round(data["price_change_percentage_24h"], 2)
        df = get_historical_prices(coin_id)
        rsi = round(RSIIndicator(close=df["price"]).rsi().iloc[-1], 2)
        macd = MACD(close=df["price"]).macd_diff().iloc[-1]
        signal = get_combined_signal(rsi, macd)
        st.markdown(f\"\"\"\n<div class=\"block\">\n    <h3>{name}</h3>\n    💰 **Çmimi:** ${price} ({change}%)  \n    📈 **RSI:** {rsi}  \n    📉 **MACD diff:** {round(macd, 4)}  \n    🚨 **Sinjal:** <span style='color:{signal_color(signal)}'>{signal}</span>\n</div>\n\"\"\", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f\"{name}: Nuk u morën të dhënat. ({e})\")

st.info(\"🔄 Të dhënat rifreskohen automatikisht çdo 3 minuta.\")
