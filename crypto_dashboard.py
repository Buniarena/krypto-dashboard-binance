import streamlit as st
import requests, time, random
import pandas as pd
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ⚙️ Konfigurime
REFRESH_INTERVAL = 30
COINS = {
    "🐸 PEPE": "PEPEUSDT",
    "🐕 Shiba Inu": "SHIBUSDT",
    "⚡ Verge (XVG)": "XVGUSDT"
}
st.set_page_config(page_title="ElbuharBot PRO – Binance Fast Edition", layout="wide")

# 🎨 Stil Neon
st.markdown("""
<style>
body { background-color:black; color:white; }
.neon {
    font-size:60px; text-align:center; color:#00ffcc;
    text-shadow:0 0 10px #00ffcc, 0 0 30px #00ffcc;
    animation:pulse 2s infinite;
}
@keyframes pulse {0%{opacity:1;}50%{opacity:0.5;}100%{opacity:1;}}
.countdown {text-align:center;font-size:20px;color:#00ffc6;margin-top:10px;}
</style>
""", unsafe_allow_html=True)

st.title("💹 ElbuharBot PRO – Binance Fast Edition")

# ======================== FUNKSIONE ========================
def get_current_price(symbol):
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        r = requests.get(url, params={"symbol": symbol}, timeout=10)
        return float(r.json()["price"])
    except:
        return None

def get_historical_data(symbol, limit=180):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": "1m", "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        df = pd.DataFrame([[x[0], float(x[4])] for x in data], columns=["time", "price"])
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        df.set_index("time", inplace=True)
        return df
    except:
        return pd.DataFrame()

def generate_signal(row):
    s = 0
    if pd.notna(row.rsi):
        if row.rsi < 30: s += 1
        elif row.rsi > 70: s -= 1
    if pd.notna(row.ema12) and pd.notna(row.ema26):
        s += 1 if row.ema12 > row.ema26 else -1
    if pd.notna(row.macd) and pd.notna(row.macd_signal):
        s += 2 if row.macd > row.macd_signal else -2
    if pd.notna(row.price) and pd.notna(row.boll_upper) and pd.notna(row.boll_lower):
        s += 1 if row.price < row.boll_lower else -1 if row.price > row.boll_upper else 0
    return s

def classify_signal(s):
    if s >= 3: return "🟢 BLI"
    elif s <= -3: return "🔴 SHIT"
    else: return "🟡 MBANJ"

# ======================== UI ========================
coin_label = st.selectbox("💎 Zgjidh monedhën:", list(COINS.keys()))
symbol = COINS[coin_label]
price = get_current_price(symbol)
if not price:
    st.error("❌ Nuk mund të merren të dhëna nga Binance.")
    st.stop()

df = get_historical_data(symbol)
if df.empty:
    st.warning("⚠️ Nuk ka të dhëna historike për momentin.")
    st.stop()

# ======================== INDIKATORËT ========================
df["rsi"] = RSIIndicator(df["price"]).rsi()
df["ema12"] = EMAIndicator(df["price"], 12).ema_indicator()
df["ema26"] = EMAIndicator(df["price"], 26).ema_indicator()
macd = MACD(df["price"])
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()
df["macd_histogram"] = macd.macd_diff()
bb = BollingerBands(df["price"])
df["boll_upper"] = bb.bollinger_hband()
df["boll_lower"] = bb.bollinger_lband()

df["signal"] = df.apply(generate_signal, axis=1)
df["signal_text"] = df["signal"].apply(classify_signal)
last = df.iloc[-1]
sig = last.signal_text
color = "lime" if "BLI" in sig else "red" if "SHIT" in sig else "yellow"

prob_up = min(95, max(5, 50 + last.signal * 10 + random.randint(-5,5)))

# ======================== SINJALI ========================
st.markdown(f"<div class='neon' style='color:{color};'>{sig}</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
col1.metric("💵 Çmimi aktual", f"${price:.6f}")
col2.metric("📈 Mundësia për ngritje", f"{prob_up}%")

# ======================== GRAFIKU ========================
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5,0.25,0.25],
                    subplot_titles=(f"{coin_label} – Çmimi & EMA", "RSI", "MACD"))
fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi", line=dict(color="#00E5FF", width=2)))
fig.add_trace(go.Scatter(x=df.index, y=df["ema12"], name="EMA12", line=dict(color="#FFA500")))
fig.add_trace(go.Scatter(x=df.index, y=df["ema26"], name="EMA26", line=dict(color="#9400D3")))
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="teal")), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["macd"], name="MACD", line=dict(color="blue")), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], name="MACD Signal", line=dict(color="orange")), row=3, col=1)
fig.add_trace(go.Bar(x=df.index, y=df["macd_histogram"], name="Histogram", marker_color="gray"), row=3, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="white", row=3, col=1)
fig.update_layout(height=900, paper_bgcolor="black", plot_bgcolor="black", font=dict(color="white"))
st.plotly_chart(fig, use_container_width=True)

# ======================== TABELA ========================
st.subheader("📊 Të dhënat e fundit (10 rreshta)")
st.dataframe(df.tail(10)[["price", "rsi", "ema12", "ema26", "macd", "macd_signal",
                          "boll_upper", "boll_lower", "signal_text"]])

# ======================== TIMER ========================
ph = st.empty()
for s in range(REFRESH_INTERVAL, 0, -1):
    ph.markdown(f"<div class='countdown'>⏳ Rifreskim pas {s} sekondash...</div>", unsafe_allow_html=True)
    time.sleep(1)
ph.empty()
st.rerun()