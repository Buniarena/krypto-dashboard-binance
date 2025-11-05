import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# ⚙️ Konfigurime
AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
REFRESH_INTERVAL = 180
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

coins = {
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge",
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum"
}

# 🔗 Marrja e të dhënave
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        return r.json()[0]
    return None

@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id, days=60):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days), "interval": "daily"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        data = r.json().get("prices", [])
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    return pd.DataFrame()

# 🧩 Fillimi
st.image(HEADER_IMAGE_URL, use_column_width="always")
st.title("📊 Analizë Kriptovalutash: RSI, EMA, MACD, Bollinger & Sinjalet")

selected_coin = st.selectbox("Zgjidh monedhën", list(coins.keys()))
coin_id = coins[selected_coin]
days = st.slider("Numri i ditëve historike", 30, 90, 60)

# 📈 Merr të dhëna
current_data = get_current_data(coin_id)
if not current_data:
    st.error("Nuk u mund të merren të dhënat.")
    st.stop()

df = get_historical_prices(coin_id, days)
if df.empty:
    st.warning("Nuk ka të dhëna historike.")
    st.stop()

# 📉 Llogarit indikatorët
df["rsi"] = RSIIndicator(df["price"]).rsi()
df["ema12"] = EMAIndicator(df["price"], 12).ema_indicator()
df["ema26"] = EMAIndicator(df["price"], 26).ema_indicator()
macd = MACD(df["price"])
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()
bb = BollingerBands(df["price"])
df["boll_upper"] = bb.bollinger_hband()
df["boll_lower"] = bb.bollinger_lband()

# 🧠 Gjenero sinjale
def gen_signal(row):
    s = 0
    if row.rsi < 30: s += 1
    elif row.rsi > 70: s -= 1
    if row.ema12 > row.ema26: s += 1
    else: s -= 1
    if row.macd > row.macd_signal: s += 2
    else: s -= 2
    if row.price < row.boll_lower: s += 1
    elif row.price > row.boll_upper: s -= 1
    return s

df["signal"] = df.apply(gen_signal, axis=1)

def classify_signal(s):
    if s >= 3: return "🟢 BLI"
    elif s <= -3: return "🔴 SHIT"
    else: return "🟡 MBANJ"

df["text_signal"] = df["signal"].apply(classify_signal)

def get_color(s):
    if s >= 3: return "darkgreen"
    elif s > 0: return "green"
    elif s <= -3: return "darkred"
    elif s < 0: return "red"
    else: return "yellow"

colors = df["signal"].apply(get_color)

# 🎨 Grafik
fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    row_heights=[0.5, 0.2, 0.3],
                    subplot_titles=(f"Çmimi & EMA ({selected_coin})", "RSI", "MACD"))

# Çmimi dhe EMA
fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi", line=dict(color="blue")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema12"], name="EMA12", line=dict(color="orange")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema26"], name="EMA26", line=dict(color="purple")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["price"], mode="markers",
                         name="Sinjal", marker=dict(color=colors, size=8)), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="teal")), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# MACD
fig.add_trace(go.Scatter(x=df.index, y=df["macd"], name="MACD", line=dict(color="blue")), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], name="MACD Signal", line=dict(color="orange")), row=3, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=1)

fig.update_layout(height=900, showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# 📊 Sinjali më i fundit
latest = df.iloc[-1]
signal_text = classify_signal(latest.signal)
prob_up = min(95, max(5, 50 + latest.signal * 10 + random.randint(-5, 5)))
prob_down = 100 - prob_up

st.subheader("📢 Sinjali i fundit tregtar")
st.markdown(f"### {signal_text}")
st.progress(prob_up / 100)
st.markdown(f"**📈 Mundësia që të ngrihet: {prob_up}%**")
st.markdown(f"**📉 Mundësia që të bjerë: {prob_down}%**")

# Tabela
st.subheader("📋 Të dhënat e fundit (5 ditët e fundit)")
st.dataframe(df.tail(5)[["price", "rsi", "ema12", "ema26", "macd", "macd_signal", "signal", "text_signal"]])