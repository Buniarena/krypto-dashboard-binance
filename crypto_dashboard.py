import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import time

# ⏱️ Koha për rifreskim
REFRESH_INTERVAL = 180  # sekonda

# Monedhat që do të shfaqen
coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

# Inicializimi i cache për të shmangur 429
if "cached_data" not in st.session_state:
    st.session_state.cached_data = {}
if "last_fetch" not in st.session_state:
    st.session_state.last_fetch = {}

def get_market_data(coin_id):
    now = time.time()
    # Kontrolli i cache
    if coin_id in st.session_state.cached_data and now - st.session_state.last_fetch[coin_id] < REFRESH_INTERVAL:
        return st.session_state.cached_data[coin_id]
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": 30, "interval": "daily"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = [price[1] for price in data["prices"]]
        st.session_state.cached_data[coin_id] = prices
        st.session_state.last_fetch[coin_id] = now
        return prices
    except:
        return None

def get_current_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()[coin_id]
        return data["usd"], data["usd_24h_change"]
    except:
        return None, None

def calculate_indicators(prices):
    if prices and len(prices) >= 26:
        df = pd.DataFrame(prices, columns=["close"])
        rsi = RSIIndicator(df["close"]).rsi().iloc[-1]
        macd = MACD(df["close"])
        macd_diff = macd.macd_diff().iloc[-1]
        return rsi, macd_diff
    return None, None

def generate_signal(rsi):
    if rsi is None:
        return "❓ N/A"
    elif rsi < 30:
        return "🟢 Bli"
    elif rsi > 70:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

def seconds_remaining():
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

# UI
st.title("📊 Dashboard: RSI, MACD, Çmimi dhe Sinjale")
st.write(f"⏳ Rifreskimi automatik në: {seconds_remaining()} sekonda")

for name, coin_id in coins.items():
    prices = get_market_data(coin_id)
    price, change_24h = get_current_price(coin_id)

    st.subheader(name)
    if prices is None or price is None:
        st.warning(f"Kufizim API për {coin_id}. Nuk mund të marrim të dhënat aktuale.")
        st.write(f"""
        💰 Çmimi: N/A

        📊 Ndryshimi 24h: N/A

        📈 RSI: N/A

        📉 MACD diff: N/A

        💡 Sinjal: ❓ N/A
        """)
        continue

    rsi, macd_diff = calculate_indicators(prices)
    signal = generate_signal(rsi)

    st.write(f"""
    💰 Çmimi: ${price:.8f}

    📊 Ndryshimi 24h: {change_24h:.2f}%

    📈 RSI: {rsi:.2f}{" (i ulët)" if rsi < 30 else " (i lartë)" if rsi > 70 else ""}

    📉 MACD diff: {macd_diff:.2f}

    💡 Sinjal: {signal}
    """)

st.write("🔄 Të dhënat rifreskohen automatikisht çdo 3 minuta. Burimi: CoinGecko (pa API key)")
