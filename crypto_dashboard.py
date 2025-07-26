import streamlit as st
import requests
import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Konfigurime
REFRESH_INTERVAL = 180  # sekonda

# Lista e monedhave me emër dhe ID CoinGecko
coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

# Funksioni për të marrë çmimin aktual
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": coin_id
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()[0]
    except Exception as e:
        return None

# Funksioni për të marrë të dhënat historike të çmimit
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "60",
        "interval": "daily"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        prices = response.json()["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["price"] = df["price"].astype(float)
        return df
    except Exception:
        return pd.DataFrame()

# Llogarit RSI dhe MACD
def calculate_indicators(df):
    if df.empty or len(df) < 35:
        return None, None
    rsi = RSIIndicator(close=df["price"]).rsi().iloc[-1]
    macd = MACD(close=df["price"])
    macd_diff = macd.macd_diff().iloc[-1]
    return round(rsi, 2), round(macd_diff, 6)

# Gjenero sinjal bazuar në RSI dhe MACD
def generate_signal(rsi, macd_diff):
    if rsi is None or macd_diff is None:
        return "❓ N/A"
    if rsi < 30 and macd_diff > 0:
        return "🟢 Bli"
    elif rsi > 70 and macd_diff < 0:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

# Koha e rifreskimit
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()
        st.cache_data.clear()

refresh_if_needed()

# Fillimi i dashboardit
st.title("📊 Dashboard: RSI, MACD, Çmimi dhe Sinjale")
st.caption(f"⏳ Rifreskimi automatik në: {seconds_remaining()} sekonda")

# Paraqitja e monedhave
for name, coin_id in coins.items():
    col = st.container()
    col.subheader(name)

    data = get_current_data(coin_id)
    hist_df = get_historical_prices(coin_id)

    if data is None:
        col.error(f"Kufizim API (429) për {coin_id}. Nuk mund të marrim të dhëna.")
        continue

    price = data["current_price"]
    change = data["price_change_percentage_24h"]

    rsi, macd_diff = calculate_indicators(hist_df)
    signal = generate_signal(rsi, macd_diff)

    col.markdown(f"**💰 Çmimi:** ${price:.8f}")
    col.markdown(f"**📈 Ndryshimi 24h:** {change:.2f}%")
    col.markdown(f"**📊 RSI:** {rsi if rsi else 'N/A'}")
    col.markdown(f"**📉 MACD diff:** {macd_diff if macd_diff else 'N/A'}")
    col.markdown(f"**💡 Sinjal:** {signal}")

st.info("🔄 Të dhënat rifreskohen automatikisht çdo 3 minuta. Burimi: CoinGecko")
