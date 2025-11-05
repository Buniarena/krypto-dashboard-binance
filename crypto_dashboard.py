import streamlit as st
import requests
import pandas as pd
import random
import time
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ⚙️ KONFIGURIME
REFRESH_INTERVAL = 60  # çdo 1 minutë
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1629654297299-cf0f61f84ad2?auto=format&fit=crop&w=1200&q=80"

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

# 🧠 Marrje të dhënash
@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def get_current_data(coin_id):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "ids": coin_id}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()[0]
    except:
        return None
    return None

@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def get_historical_prices_last_hours(coin_id, hours=3):
    now_sec = int(time.time())
    frm_sec = now_sec - hours * 3600
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {"vs_currency": "usd", "from": str(frm_sec), "to": str(now_sec)}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json().get("prices", [])
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df.dropna()
        return df
    except:
        return pd.DataFrame()

# 🌄 HEADER
st.image(HEADER_IMAGE_URL, use_column_width=True)
st.markdown("<h1 style='text-align:center; color:#00C4CC;'>🚀 ElbuharBot PRO Live Radar</h1>", unsafe_allow_html=True)
st.caption("⏱️ Analizë e gjallë për 3 orët e fundit | Rifreskohet çdo 1 minutë")

# 💰 ZGJEDHJA E MONEDHËS
selected_coin = st.selectbox("💎 Zgjidh monedhën për analizë:", list(coins.keys()))
coin_id = coins[selected_coin]

# 🔍 Merr të dhëna
current = get_current_data(coin_id)
df = get_historical_prices_last_hours(coin_id, 3)

if not current or df.empty:
    st.error("❌ Nuk mund të merren të dhënat.")
    st.stop()

# 📊 Indikatorët
df["rsi"] = RSIIndicator(df["price"]).rsi()
df["ema12"] = EMAIndicator(df["price"], 12).ema_indicator()
df["ema26"] = EMAIndicator(df["price"], 26).ema_indicator()
macd = MACD(df["price"])
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()
bb = BollingerBands(df["price"])
df["boll_upper"] = bb.bollinger_hband()
df["boll_lower"] = bb.bollinger_lband()

# 🎯 Gjenerim sinjali
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
df["signal_text"] = df["signal"].apply(lambda s: "🟢 BLI" if s >= 3 else "🔴 SHIT" if s <= -3 else "🟡 MBANJ")

# 🧠 SINJALI I FUNDIT
latest = df.iloc[-1]
signal_text = latest.signal_text
prob_up = min(95, max(5, 50 + latest.signal * 10 + random.randint(-5, 5)))
prob_down = 100 - prob_up

# 🎨 GRÁFIK I GJALLË
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4],
                    subplot_titles=(f"💰 {selected_coin} – Çmimi & EMA", "RSI & MACD"))

# Çmimi & EMA
fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi", line=dict(color="#00BFFF", width=2)))
fig.add_trace(go.Scatter(x=df.index, y=df["ema12"], name="EMA12", line=dict(color="#FFA500", width=1)))
fig.add_trace(go.Scatter(x=df.index, y=df["ema26"], name="EMA26", line=dict(color="#9B30FF", width=1)))

# RSI dhe MACD
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="teal", width=2)), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

fig.update_layout(
    height=800,
    showlegend=True,
    paper_bgcolor="black",
    plot_bgcolor="black",
    font=dict(color="white"),
)

st.plotly_chart(fig, use_container_width=True)

# ⚡ PANEL SINJALI
st.markdown("---")
st.markdown(f"<h2 style='text-align:center;'>📢 {signal_text}</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1.metric("💵 Çmimi aktual", f"${current['current_price']:.6f}")
col2.metric("📊 Vëllimi 24h", f"${current['total_volume']:,.0f}")

# 🔮 RADAR I MUNDËSISË
radar_fig = go.Figure()
radar_fig.add_trace(go.Indicator(
    mode="gauge+number+delta",
    value=prob_up,
    delta={'reference': 50},
    title={'text': "📈 Mundësia për ngritje"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "lime" if prob_up > 60 else "orange" if 40 <= prob_up <= 60 else "red"},
        'steps': [
            {'range': [0, 40], 'color': 'rgba(255,0,0,0.3)'},
            {'range': [40, 60], 'color': 'rgba(255,255,0,0.3)'},
            {'range': [60, 100], 'color': 'rgba(0,255,0,0.3)'}
        ],
    }
))
radar_fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white", size=14))
st.plotly_chart(radar_fig, use_container_width=True)

# 🕒 Footer
st.markdown(f"<div style='text-align:center; color:gray;'>🔄 Rifreskim automatik çdo 1 minutë | Përditësuar më: {datetime.utcnow().strftime('%H:%M:%S UTC')}</div>", unsafe_allow_html=True)