import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
import time

REFRESH_INTERVAL = 600  # 10 minuta

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def reset_timer():
    st.session_state.start_time = time.time()

st.title("📊 Dashboard: Çmimi, RSI dhe Ndryshimi 24h")

if st.button("🔄 Rifresko Të Dhënat"):
    reset_timer()
    st.experimental_rerun()

countdown_placeholder = st.empty()

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk",
    "XVG (Verge)": "verge"
}

@st.cache_data(ttl=REFRESH_INTERVAL)
def get_market_data(coin_ids):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coin_ids),
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "30",
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
    return "❓ N/A"

def signal_color(signal):
    if "Bli" in signal:
        return "green"
    elif "Shit" in signal:
        return "red"
    elif "Mbaj" in signal:
        return "orange"
    return "gray"

try:
    market_data = get_market_data(list(coins.values()))
except Exception as e:
    st.error(f"Gabim gjatë marrjes së të dhënave: {e}")
    market_data = []

market_data_dict = {coin["id"]: coin for coin in market_data}

alerts = []

for name, coin_id in coins.items():
    data = market_data_dict.get(coin_id)
    if data:
        price = data["current_price"]
        change_24h = data["price_change_percentage_24h"]
        try:
            hist_df = get_historical_prices(coin_id)
            rsi = RSIIndicator(close=hist_df["price"]).rsi().iloc[-1]
            rsi_value = round(rsi, 2)
        except:
            rsi_value = None
        signal = get_signal(rsi_value)
        color = signal_color(signal)

        if rsi_value is not None:
            if rsi_value < 30:
                alerts.append(f"🔔 {name} është në zonën e blerjes (RSI = {rsi_value})!")
            elif rsi_value > 70:
                alerts.append(f"⚠️ {name} është në zonën e shitjes (RSI = {rsi_value})!")

        with st.container():
            st.markdown(f"### {name}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Çmimi (USD)", f"${price:,.6f}")
            col2.metric("📊 Ndryshimi 24h", f"{change_24h:.2f}%")
            col3.metric("📈 RSI (14 ditë)", f"{rsi_value}" if rsi_value is not None else "N/A")
            col4.markdown(f"<span style='color:{color}; font-weight:bold; font-size:24px'>{signal}</span>", unsafe_allow_html=True)
    else:
        st.warning(f"Nuk u morën të dhënat për {name}.")

if alerts:
    for alert in alerts:
        if "🔔" in alert:
            st.success(alert)
        else:
            st.warning(alert)

st.caption(f"🔄 Të dhënat rifreskohen automatikisht çdo {REFRESH_INTERVAL//60} minuta ose me butonin manual. Burimi: CoinGecko")

seconds_left = seconds_remaining()
countdown_placeholder.markdown(f"⏳ Rifreskimi automatik në: **{seconds_left} sekonda**")
