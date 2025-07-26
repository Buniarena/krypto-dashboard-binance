import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
import time

REFRESH_INTERVAL = 180  # 180 sekonda = 3 minuta

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    remaining = REFRESH_INTERVAL - elapsed
    return max(0, int(remaining))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()
        st.experimental_rerun()

st.title("📊 Dashboard: Çmimi Aktual dhe RSI për Coinet")

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
def get_prices(coin_ids):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd"
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
    else:
        return "❓ N/A"

def signal_color(signal):
    if signal == "🟢 Bli":
        return "green"
    elif signal == "🔴 Shit":
        return "red"
    elif signal == "🟡 Mbaj":
        return "orange"
    else:
        return "gray"

def play_alert_sound():
    # Luaj zilen (mund ta zëvendësosh me ndonjë tjetër URL tingulli)
    st.components.v1.html("""
    <audio autoplay>
      <source src="https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg" type="audio/ogg">
      Your browser does not support the audio element.
    </audio>
    """, height=0)

try:
    current_prices = get_prices(list(coins.values()))
except requests.exceptions.RequestException as e:
    st.error(f"Gabim API: {e}")
    current_prices = {}

for name, coin_id in coins.items():
    price = current_prices.get(coin_id, {}).get("usd")
    try:
        hist_df = get_historical_prices(coin_id)
        rsi = RSIIndicator(close=hist_df["price"]).rsi().iloc[-1]
        rsi_value = round(rsi, 2)
    except Exception:
        rsi_value = None
    
    signal = get_signal(rsi_value)

    # Nëse RSI është nën 30 ose mbi 70, luaj zilen
    if isinstance(rsi_value, float) and (rsi_value < 30 or rsi_value > 70):
        play_alert_sound()

    signal_html = f'<span style="color:{signal_color(signal)}; font-weight: bold;">{signal}</span>'

    with st.container():
        st.markdown(f"### {name}")
        if price is not None:
            col1, col2, col3 = st.columns([1.5, 1.5, 1])
            col1.metric(label="💰 Çmimi aktual (USD)", value=f"${price:,.6f}")
            if rsi_value is not None:
                col2.metric(label="📈 RSI (14 ditë)", value=f"{rsi_value}")
            else:
                col2.markdown("📈 RSI: ❓ N/A")
            col3.markdown(signal_html, unsafe_allow_html=True)
        else:
            st.warning("Nuk u morën të dhënat për këtë coin.")

st.caption(f"🔄 Të dhënat rifreskohen çdo {REFRESH_INTERVAL//60} minuta. Burimi: CoinGecko | RSI bazuar në çmimet ditore të 30 ditëve.")

for i in range(seconds_remaining(), -1, -1):
    countdown_placeholder.markdown(f"⏳ Rifreskimi i ardhshëm në: **{i} sekonda**")
    time.sleep(1)
    if i == 0:
        st.experimental_rerun()
