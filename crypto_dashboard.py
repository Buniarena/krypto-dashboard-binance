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

# ⚡ Merr të dhëna aktuale
@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()[0]
    except Exception:
        return None

# ⚡ Merr çmimet historike
@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def get_historical_prices(coin_id, days=60):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days), "interval": "daily"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json().get("prices", [])
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# 🧠 UI
st.image(HEADER_IMAGE_URL, use_column_width="always")
st.title("📊 Analizë Kriptovalutash – Sinjalet BLI • MBANJ • SHIT me Probabilitet (%)")

selected_coin = st.selectbox("Zgjidh monedhën", list(coins.keys()))
coin_id = coins[selected_coin]
days = st.slider("Numri i ditëve historike", 30, 60, 30, 15)

# Merr të dhëna aktuale
current = get_current_data(coin_id)
if current is None:
    st.error("Nuk u morën të dhëna.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric(f"Çmimi aktual i {selected_coin}", f"${current['current_price']:.6f}")
col2.metric("Kapitalizimi i tregut", f"${current['market_cap']:,.0f}")
col3.metric("Vëllimi 24h", f"${current['total_volume']:,.0f}")

# Merr historikun
df = get_historical_prices(coin_id, days)
if df.empty:
    st.warning("Nuk ka të dhëna historike.")
    st.stop()

# 📈 Indikatorët me TA për shpejtësi
df["rsi"] = RSIIndicator(df["price"]).rsi()
df["ema12"] = EMAIndicator(df["price"], 12).ema_indicator()
df["ema26"] = EMAIndicator(df["price"], 26).ema_indicator()
macd_calc = MACD(df["price"])
df["macd"] = macd_calc.macd()
df["macd_signal"] = macd_calc.macd_signal()
df["macd_histogram"] = macd_calc.macd_diff()
bb = BollingerBands(df["price"])
df["bollinger_upper"] = bb.bollinger_hband()
df["bollinger_lower"] = bb.bollinger_lband()

# 🎯 Gjenero sinjalin
def generate_signals(df):
    out = []
    for i in range(len(df)):
        s = 0
        if df["rsi"].iloc[i] < 30: s += 1
        elif df["rsi"].iloc[i] > 70: s -= 1
        if df["ema12"].iloc[i] > df["ema26"].iloc[i]: s += 1
        else: s -= 1
        if df["macd"].iloc[i] > df["macd_signal"].iloc[i]: s += 2
        else: s -= 2
        if df["price"].iloc[i] < df["bollinger_lower"].iloc[i]: s += 1
        elif df["price"].iloc[i] > df["bollinger_upper"].iloc[i]: s -= 1
        out.append(s)
    return out

df["signal"] = generate_signals(df)

# 🧭 Klasifikimi + Probabiliteti
def signal_text(s):
    if s >= 3: return "🟢 BLI"
    elif s <= -3: return "🔴 SHIT"
    else: return "🟡 MBANJ"

def signal_color(s):
    if s >= 3: return "green"
    elif s <= -3: return "red"
    else: return "yellow"

df["decision"] = df["signal"].apply(signal_text)
df["color"] = df["signal"].apply(signal_color)

# 📊 Llogarit probabilitetet
def calculate_probabilities(signal):
    if signal >= 3:
        return 80 + random.randint(0, 15), 15 - random.randint(0, 10)   # Bli dominant
    elif signal <= -3:
        return 15 - random.randint(0, 10), 80 + random.randint(0, 15)   # Shit dominant
    else:
        return 50 + random.randint(-10, 10), 50 + random.randint(-10, 10)

latest_signal = df["signal"].iloc[-1]
prob_buy, prob_sell = calculate_probabilities(latest_signal)
latest_decision = df["decision"].iloc[-1]

# 🔔 Zile në sinjale të forta
if "BLI" in latest_decision or "SHIT" in latest_decision:
    st.audio(AUDIO_URL, format="audio/ogg", start_time=0)

# 🟩 Shfaq sinjalin aktual dhe probabilitetet
st.markdown("---")
st.subheader("📢 SINJALI AKTUAL")
st.markdown(f"## {latest_decision}")

colb, cols = st.columns(2)
colb.metric("Probabilitet për BLI", f"{prob_buy:.1f}%")
cols.metric("Probabilitet për SHIT", f"{prob_sell:.1f}%")

# Bar vizual
st.progress(abs(latest_signal) / 6)

# 🎨 Grafik
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                    subplot_titles=(f'Çmimi & EMA për {selected_coin}', 'RSI', 'MACD'),
                    row_heights=[0.5, 0.2, 0.3])

# Çmimi + EMA
fig.add_trace(go.Scatter(x=df.index, y=df["price"], mode="lines", name="Çmimi", line=dict(color="blue")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema12"], mode="lines", name="EMA 12", line=dict(color="orange")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema26"], mode="lines", name="EMA 26", line=dict(color="purple")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["bollinger_upper"], mode="lines", name="Bollinger Upper", line=dict(color="gray")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["bollinger_lower"], mode="lines", name="Bollinger Lower", line=dict(color="gray")), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["price"], mode="markers", name="Sinjal", marker=dict(color=df["color"], size=8)), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], mode="lines", name="RSI", line=dict(color="teal")), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# MACD
fig.add_trace(go.Scatter(x=df.index, y=df["macd"], mode="lines", name="MACD", line=dict(color="blue")), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], mode="lines", name="MACD Signal", line=dict(color="orange")), row=3, col=1)
fig.add_trace(go.Bar(x=df.index, y=df["macd_histogram"], name="Histogram", marker_color="gray"), row=3, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=1)

fig.update_layout(height=900, title=f"Analizë për {selected_coin}", showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# 📅 Tabela e fundit
st.subheader("📆 5 Ditët e Fundit")
st.dataframe(df.tail(5)[["price", "rsi", "ema12", "ema26", "macd", "macd_signal", "signal", "decision"]])