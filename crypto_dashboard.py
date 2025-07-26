import streamlit as st
import requests
import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Konfigurime
REFRESH_INTERVAL = 180  # sekonda (3 minuta)

# Lista e monedhave me emër dhe ID CoinGecko
coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

# API KEY për CoinGecko (opsionale)
API_KEY = ""  # Vendos çelësin nëse ke CoinGecko PRO
headers = {"x-cg-pro-api-key": API_KEY} if API_KEY else {}

# Funksioni për të marrë çmimin aktual
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()[0]
    except Exception:
        return None

# Funksioni për të marrë historikun e çmimit
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "60", "interval": "daily"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        prices = response.json().get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["price"] = df["price"].astype(float)
        return df
    except Exception:
        return pd.DataFrame()

# Llogarit RSI dhe MACD
def calculate_indicators(df):
    if df.empty or len(df) < 35:
        return None, None
    try:
        rsi = RSIIndicator(close=df["price"]).rsi().iloc[-1]
        macd_line = MACD(close=df["price"]).macd()
        macd_signal = MACD(close=df["price"]).macd_signal()
        macd_diff = macd_line - macd_signal
        return round(rsi, 2), round(macd_diff.iloc[-1], 6)
    except Exception:
        return None, None

# Gjenero sinjal nga RSI dhe MACD
def generate_signal(rsi, macd_diff):
    if rsi is None or macd_diff is None:
        return "❓ N/A"
    if rsi < 30 and macd_diff > 0:
        return "🟢 Bli"
    elif rsi > 70 and macd_diff < 0:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

# Rifreskimi automatik
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()

# UI - Fillimi i dashboard-it
st.title("📊 Dashboard: RSI, MACD, Çmimi dhe Sinjale")
st.caption(f"⏳ Rifreskimi automatik në: {seconds_remaining()} sekonda")

refresh_if_needed()

# Loop për çdo monedhë
for name, coin_id in coins.items():
    st.subheader(name)

    data = get_current_data(coin_id)
    historical = get_historical_prices(coin_id)

    if not data:
        st.warning(f"Kufizim API (429) ose gabim për '{coin_id}'.")
        continue

    price = data.get("current_price", "N/A")
    change_24h = data.get("price_change_percentage_24h", "N/A")
    rsi, macd_diff = calculate_indicators(historical)
    signal = generate_signal(rsi, macd_diff)

    # Formatim i çmimit
    price_str = f"${price:,.8f}" if isinstance(price, float) and price < 1 else f"${price:,.2f}"

    # Trego informacionin
    st.markdown(f"""
    💰 **Çmimi:** {price_str}  
    📊 **Ndryshimi 24h:** {change_24h:.2f}%  
    📈 **RSI:** {rsi if rsi is not None else "N/A"}  
    📉 **MACD diff:** {macd_diff if macd_diff is not None else "N/A"}  
    💡 **Sinjal:** {signal}
    """)

st.info("🔄 Të dhënat rifreskohen automatikisht çdo 3 minuta. Burimi: CoinGecko")
