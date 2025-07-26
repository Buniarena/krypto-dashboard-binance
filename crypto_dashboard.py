import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
import time

REFRESH_INTERVAL = 180

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()
        st.experimental_rerun()

# CSS me dritare horizontale
page_style = """
<style>
body, .stApp {
    background: linear-gradient(135deg, #1c1c1c, #2e2e2e);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.card {
    background-color: #1f2937;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

.card h3 {
    color: #60A5FA;
    margin: 0;
}

.metric-box {
    text-align: center;
}

.metric-value {
    font-size: 24px;
    font-weight: bold;
}

.signal {
    font-size: 20px;
    font-weight: bold;
}
</style>
"""

st.markdown(page_style, unsafe_allow_html=True)

# Logo dhe titulli
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='font-size: 48px; color: #3B82F6; letter-spacing: 4px;'>🏟️ ARENA BUNI</h1>
        <p style='font-size: 18px; color: #ddd;'>Dashboard profesional për çmimet e kriptovalutave</p>
    </div>
""", unsafe_allow_html=True)

st.title("📊 Çmimi, RSI dhe Ndryshimi 24h")
countdown_placeholder = st.empty()
refresh_if_needed()

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
    url = "https://api.coingecko.com/api/v3/coins/markets"
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
        return "lightgreen"
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

# Karta për çdo coin në mënyrë horizontale
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

        # Layout horizontal
        st.markdown(f"""
            <div class='card'>
                <div><h3>{name}</h3></div>
                <div class='metric-box'>
                    <div>💰 Çmimi</div>
                    <div class='metric-value'>${price:,.6f}</div>
                </div>
                <div class='metric-box'>
                    <div>📊 Ndryshimi 24h</div>
                    <div class='metric-value'>{change_24h:.2f}%</div>
                </div>
                <div class='metric-box'>
                    <div>📈 RSI</div>
                    <div class='metric-value'>{rsi_value if rsi_value else "N/A"}</div>
                </div>
                <div class='metric-box'>
                    <div>💡 Sinjal</div>
                    <div class='signal' style='color: {color}'>{signal}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"Nuk u morën të dhënat për {name}.")

st.caption(f"🔄 Të dhënat rifreskohen çdo {REFRESH_INTERVAL//60} minuta. Burimi: CoinGecko")

# Timer për rifreskim
for i in range(seconds_remaining(), -1, -1):
    countdown_placeholder.markdown(f"⏳ Rifreskimi i ardhshëm në: **{i} sekonda**")
    time.sleep(1)
    if i == 0:
        st.experimental_rerun()
