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

page_style = """
<style>
body, .stApp {
    background-color: #0F172A;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.block {
    background-color: #1E293B;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
.title {
    font-size: 28px;
    font-weight: bold;
    color: #60A5FA;
}
.signal {
    font-size: 20px;
    font-weight: bold;
}
.blink {
    animation: blinker 1s linear infinite;
}
@keyframes blinker {
    50% { opacity: 0; }
}
</style>
"""

st.markdown(page_style, unsafe_allow_html=True)
st.title("📊 Dashboard: RSI, MACD, Çmimi dhe Sinjale")

countdown_placeholder = st.empty()
refresh_if_needed()

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge",
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
def get_historical_prices_safe(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "60",  # më shumë pika për MACD
        "interval": "daily"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        prices = response.json()["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["price"] = df["price"].astype(float)
        return df
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            st.warning(f"Kufizim API (429) për {coin_id}. Nuk mund të marrim të dhënat aktuale.")
            return None
        else:
            raise e

def get_signal(rsi, macd_diff):
    if isinstance(rsi, float) and isinstance(macd_diff, float):
        if rsi < 30 and macd_diff > 0:
            return "🟢 Bli"
        elif rsi > 70 and macd_diff < 0:
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

for idx, (name, coin_id) in enumerate(coins.items()):
    data = market_data_dict.get(coin_id)
    if data:
        price = data["current_price"]
        change_24h = data["price_change_percentage_24h"]

        try:
            if idx != 0:
                time.sleep(1)  # Delay për shmangien e 429

            hist_df = get_historical_prices_safe(coin_id)
            if hist_df is None:
                rsi_value = None
                macd_diff_value = None
            else:
                # Debug print - mund t'i hiqni më vonë
                st.write(f"{name} - Numri i të dhënave historike: {len(hist_df)}")

                rsi = RSIIndicator(close=hist_df["price"]).rsi().iloc[-1]
                rsi_value = round(rsi, 2)

                macd_indicator = MACD(close=hist_df["price"])
                macd_diff = macd_indicator.macd_diff().iloc[-1]
                macd_diff_value = round(macd_diff, 4)
        except Exception as e:
            rsi_value = None
            macd_diff_value = None
            st.warning(f"Probleme me llogaritjen e indikatorëve për {name}: {e}")

        signal = get_signal(rsi_value, macd_diff_value)
        color = signal_color(signal)
        alarm_class = "blink" if signal in ["🟢 Bli", "🔴 Shit"] else ""

        st.markdown(f"""
            <div class='block'>
                <div class='title'>{name}</div>
                <p>💰 <b>Çmimi:</b> ${price:,.8f}</p>
                <p>📊 <b>Ndryshimi 24h:</b> {change_24h:.2f}%</p>
                <p>📈 <b>RSI:</b> {rsi_value if rsi_value is not None else "N/A"}</p>
                <p>📉 <b>MACD diff:</b> {macd_diff_value if macd_diff_value is not None else "N/A"}</p>
                <p>💡 <b>Sinjal:</b> <span class='signal {alarm_class}' style='color:{color}'>{signal}</span></p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"Nuk u morën të dhënat për {name}.")

st.caption("🔄 Të dhënat rifreskohen automatikisht çdo 3 minuta. Burimi: CoinGecko")

for i in range(seconds_remaining(), -1, -1):
    countdown_placeholder.markdown(f"⏳ Rifreskimi automatik në: **{i} sekonda**")
    time.sleep(1)
    if i == 0:
        st.experimental_rerun()
