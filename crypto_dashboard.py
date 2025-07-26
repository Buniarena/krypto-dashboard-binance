import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
import time

REFRESH_INTERVAL = 180  # sekonda

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "last_signal" not in st.session_state:
    st.session_state.last_signal = {}

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    remaining = REFRESH_INTERVAL - elapsed
    return max(0, int(remaining))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()
        st.experimental_rerun()

st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📊 Krypto Dashboard: Çmimi • % Ndryshim • RSI • Sinjali")

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
def get_prices_and_change(coin_ids):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd",
        "include_24hr_change": "true"
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
    return {
        "🟢 Bli": "green",
        "🔴 Shit": "red",
        "🟡 Mbaj": "orange"
    }.get(signal, "gray")

def play_alert_sound(signal):
    if signal == "🟢 Bli":
        sound_url = "https://actions.google.com/sounds/v1/alarms/bugle_tune.ogg"
    elif signal == "🔴 Shit":
        sound_url = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
    else:
        return
    st.components.v1.html(f"""
    <audio autoplay>
      <source src="{sound_url}" type="audio/ogg">
    </audio>
    """, height=0)

# Merr çmimet dhe ndryshimin 24h
try:
    price_data = get_prices_and_change(list(coins.values()))
except requests.exceptions.RequestException as e:
    st.error(f"Gabim API: {e}")
    price_data = {}

# Krijo një listë me të dhëna për tabelën
table_rows = []

for name, coin_id in coins.items():
    price_info = price_data.get(coin_id, {})
    price = price_info.get("usd")
    change_24h = price_info.get("usd_24h_change")

    try:
        hist_df = get_historical_prices(coin_id)
        rsi = RSIIndicator(close=hist_df["price"]).rsi().iloc[-1]
        rsi_value = round(rsi, 2)
    except Exception:
        rsi_value = None

    signal = get_signal(rsi_value)

    # Alarm për sinjal të ri
    if (isinstance(rsi_value, float) and (rsi_value < 30 or rsi_value > 70)):
        if st.session_state.last_signal.get(name) != signal:
            play_alert_sound(signal)
            st.session_state.last_signal[name] = signal

    # Ngjyra për sinjal
    color = signal_color(signal)
    signal_html = f'<span style="color:{color}; font-weight:bold;">{signal}</span>'

    # Rreshti në tabelë
    row = {
        "🪙 Coin": name,
        "💰 Çmimi": f"${price:,.6f}" if price is not None else "N/A",
        "📊 % Ndryshim (24h)": f"{change_24h:.2f}%" if change_24h is not None else "N/A",
        "📈 RSI": f"{rsi_value}" if rsi_value is not None else "N/A",
        "⚠️ Sinjali": signal_html
    }
    table_rows.append(row)

# Shfaq të dhënat si tabelë me HTML për sinjalin
df = pd.DataFrame(table_rows)
st.write("### 📋 Tabela e Coin-ëve me sinjale:")

# Render tabela me HTML për sinjalin
from st_aggrid import AgGrid, GridOptionsBuilder

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("⚠️ Sinjali", editable=False, cellRenderer='html')
gridOptions = gb.build()
AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True, fit_columns_on_grid_load=True)

st.caption(f"⏱️ Rifreskimi automatik çdo {REFRESH_INTERVAL//60} minuta")

# Timer i mbetur
for i in range(seconds_remaining(), -1, -1):
    countdown_placeholder.markdown(f"⏳ Rifreskimi i ardhshëm në: **{i} sekonda**")
    time.sleep(1)
    if i == 0:
        st.experimental_rerun()
