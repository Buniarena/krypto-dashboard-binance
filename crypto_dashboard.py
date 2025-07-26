import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
import time

REFRESH_INTERVAL = 180  # 3 minuta

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()
        st.experimental_rerun()

# Sfond me CSS dhe overlay me ngjyrë për lexueshmëri
page_bg_img = '''
<style>
body, .stApp {
    background-image: url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1470&q=80");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    height: 100vh;
    color: white;
    position: relative;
}

.main {
    position: relative;
    z-index: 1;
    background: rgba(0,0,0,0.55); /* overlay për lexueshmëri */
    padding: 20px 40px;
    border-radius: 15px;
}

h1, h2, h3, h4, h5, h6, p {
    color: white !important;
}

.metric-label, .metric-value {
    color: white !important;
}

div.stMarkdown > h1, div.stMarkdown > h2 {
    color: #00BFFF !important; /* Bluja në tituj */
}

</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

# Logo me stil
st.markdown("""
    <div style='
        display:flex;
        align-items:center;
        justify-content:center;
        gap: 15px;
        margin-bottom: 30px;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.7);
    '>
        <div style='font-size:56px;'>🏟️</div>
        <h1 style='color:#00BFFF; margin:0; font-weight:900; font-size:48px; letter-spacing: 4px;'>ARENA BUNI</h1>
    </div>
""", unsafe_allow_html=True)

st.title("📊 Dashboard: Çmimi, RSI dhe Ndryshimi 24h")

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

        with st.container():
            st.markdown(f"### {name}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Çmimi (USD)", f"${price:,.6f}")
            col2.metric("📊 Ndryshimi 24h", f"{change_24h:.2f}%")
            col3.metric("📈 RSI (14 ditë)", f"{rsi_value}" if rsi_value is not None else "N/A")
            col4.markdown(f"<span style='color:{color}; font-weight:bold; font-size:22px'>{signal}</span>", unsafe_allow_html=True)
    else:
        st.warning(f"Nuk u morën të dhënat për {name}.")

st.caption(f"🔄 Të dhënat rifreskohen çdo {REFRESH_INTERVAL//60} minuta. Burimi: CoinGecko")

for i in range(seconds_remaining(), -1, -1):
    countdown_placeholder.markdown(f"⏳ Rifreskimi i ardhshëm në: **{i} sekonda**")
    time.sleep(1)
    if i == 0:
        st.experimental_rerun()
