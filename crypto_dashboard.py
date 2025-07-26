import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import time

# Vendos këtu API KEY tënd
API_KEY = "VENDOS_API_KEY_KËTU"
HEADERS = {"x-cg-pro-api-key": API_KEY}

REFRESH_INTERVAL = 180  # sekonda

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

def seconds_remaining():
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def get_market_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": 30, "interval": "daily"}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        prices = [price[1] for price in data["prices"]]
        return prices
    except Exception as e:
        return None

def calculate_indicators(prices):
    if prices and len(prices) >= 26:
        df = pd.DataFrame(prices, columns=["close"])
        rsi = RSIIndicator(df["close"]).rsi().iloc[-1]
        macd = MACD(df["close"])
        macd_diff = macd.macd_diff().iloc[-1]
        return rsi, macd_diff
    return None, None

def get_current_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()[coin_id]
        return data["usd"], data["usd_24h_change"]
    except:
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

st.title("📊 Dashboard: RSI, MACD, Çmimi dhe Sinjale")
st.write(f"⏳ Rifreskimi automatik në: {seconds_remaining()} sekonda")

for name, coin_id in coins.items():
    prices = get_market_data(coin_id)
    price, change_24h = get_current_price(coin_id)

    st.subheader(name)
    if price is None or prices is None:
        st.warning(f"Kufizim API (429) për {coin_id}. Nuk mund të marrim të dhënat aktuale.")
        st.write(f"""
        💰 Çmimi: {price or 'N/A'}
        
        📊 Ndryshimi 24h: {round(change_24h, 2) if change_24h else 'N/A'}%
        
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

    📈 RSI: {rsi:.2f}{" (i lartë)" if rsi > 70 else " (i ulët)" if rsi < 30 else ""}

    📉 MACD diff: {macd_diff:.2f}

    💡 Sinjal: {signal}
    """)

st.write("🔄 Të dhënat rifreskohen automatikisht çdo 3 minuta. Burimi: CoinGecko")
