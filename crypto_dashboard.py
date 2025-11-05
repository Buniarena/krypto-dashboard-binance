import time
import random
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands

# ⚙️ Konfigurime
AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
REFRESH_INTERVAL = 60  # rifresko cache çdo 60 sekonda tani që jemi intraday
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

coins = {
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge",
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum"
}

# 🔗 Merr të dhënat aktuale (çmim live)
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        return r.json()[0]
    return None

# ⏱ Merr historikun për 3 orët e fundit (me minuta)
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_last_hours_prices(coin_id, hours=3):
    now_sec = int(time.time())
    start_sec = now_sec - hours * 3600

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {
        "vs_currency": "usd",
        "from": str(start_sec),
        "to": str(now_sec)
    }

    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return pd.DataFrame()

    prices = r.json().get("prices", [])
    # prices = [[timestamp_ms, price], ...]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    # shumë shpesh CoinGecko kthen çdo ~1 min -> perfekt për intraday
    return df

# 🧠 UI header
st.image(HEADER_IMAGE_URL, use_column_width="always")
st.title("📊 Analizë Kripto Intraday (3 orët e fundit)")

selected_coin = st.selectbox("Zgjidh monedhën", list(coins.keys()))
coin_id = coins[selected_coin]

st.caption("Të dhënat teknike më të fundit: RSI, EMA, MACD, Bollinger Bands, sinjali (BLI / SHIT / MBANJ) dhe probabiliteti i lëvizjes.")

# 📈 Merr çmimin aktual + 3 orët e fundit
current_data = get_current_data(coin_id)
if not current_data:
    st.error("Nuk u mund të merren të dhënat live.")
    st.stop()

df = get_last_hours_prices(coin_id, hours=3)
if df.empty or len(df) < 20:
    st.warning("Nuk ka mjaft të dhëna për 3 orët e fundit për këtë monedhë.")
    st.stop()

# 📉 Llogarit indikatorët teknikë
# - RSI (momentumi)
df["rsi"] = RSIIndicator(df["price"]).rsi()

# - EMA (trend afatshkurtër)
df["ema12"] = EMAIndicator(df["price"], 12).ema_indicator()
df["ema26"] = EMAIndicator(df["price"], 26).ema_indicator()

# - MACD (forca e lëvizjes)
macd_calc = MACD(df["price"])
df["macd"] = macd_calc.macd()
df["macd_signal"] = macd_calc.macd_signal()

# - Bollinger Bands (volatiliteti)
bb = BollingerBands(df["price"])
df["boll_upper"] = bb.bollinger_hband()
df["boll_lower"] = bb.bollinger_lband()

# 🧮 Gjenero sinjal për çdo pikë
def gen_signal(row):
    s = 0
    # RSI
    if pd.notna(row.rsi):
        if row.rsi < 30:
            s += 1   # oversold → bli
        elif row.rsi > 70:
            s -= 1   # overbought → shit
    # EMA crossover
    if pd.notna(row.ema12) and pd.notna(row.ema26):
        if row.ema12 > row.ema26:
            s += 1   # bullish
        else:
            s -= 1   # bearish
    # MACD vs signal
    if pd.notna(row.macd) and pd.notna(row.macd_signal):
        if row.macd > row.macd_signal:
            s += 2   # bullish i fortë
        else:
            s -= 2   # bearish i fortë
    # Bollinger extremes
    if pd.notna(row.boll_lower) and pd.notna(row.boll_upper):
        if row.price < row.boll_lower:
            s += 1   # blej dip
        elif row.price > row.boll_upper:
            s -= 1   # shit pump
    return s

df["signal"] = df.apply(gen_signal, axis=1)

# Teksti i sinjalit (BLI / SHIT / MBANJ)
def classify_signal(s):
    if s >= 3:
        return "🟢 BLI"
    elif s <= -3:
        return "🔴 SHIT"
    else:
        return "🟡 MBANJ"

df["text_signal"] = df["signal"].apply(classify_signal)

# Ngjyrë sinjali për pikën në graf
def get_color(s):
    if s >= 3:
        return "darkgreen"
    elif s > 0:
        return "green"
    elif s <= -3:
        return "darkred"
    elif s < 0:
        return "red"
    else:
        return "yellow"

colors = df["signal"].apply(get_color)

# 📌 Pika më e fundit (sinjali aktual live)
latest = df.iloc[-1]
live_price = current_data["current_price"]
signal_text = latest["text_signal"]

# Probabiliteti i lëvizjes:
# Matet nga sinjali total → kthehet në % shanse që rritet
prob_up = min(95, max(5, 50 + latest.signal * 10 + random.randint(-3, 3)))
prob_down = 100 - prob_up

# =======================
#  SHFAQ METRIKAT KRYESORE
# =======================
col_a, col_b, col_c = st.columns(3)
col_a.metric("Çmimi aktual", f"${live_price:.6f}")
col_b.metric("24h Volume", f"${current_data['total_volume']:,.0f}")
col_c.metric("Market Cap", f"${current_data['market_cap']:,.0f}")

st.markdown("---")
st.subheader("📢 SINJALI I FUNDIT (live)")

st.markdown(f"### {signal_text}")
st.markdown(f"**Çmimi tani:** `${live_price:.6f}` USD")
st.markdown(f"**RSI:** {latest.rsi:.2f}   |   **EMA12 vs EMA26:** {'bullish' if latest.ema12 > latest.ema26 else 'bearish'}")
st.markdown(f"**MACD:** {latest.macd:.6f}   |   **MACD Signal:** {latest.macd_signal:.6f}")

# Dritare probabiliteti (mundësia të hypë / bjerë)
st.markdown("#### 📈 Mundësia që çmimi të rritet (bullish bias)")
st.progress(prob_up / 100)
st.write(f"📈 Mundësia të ngrihet: **{prob_up}%**")
st.write(f"📉 Mundësia të bjerë: **{prob_down}%**")

# =======================
#  GRAFIKU INTRADAY (3h)
# =======================
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.07,
    row_heights=[0.5, 0.2, 0.3],
    subplot_titles=(f"Çmimi (3h) & EMA ({selected_coin})", "RSI (3h)", "MACD (3h)")
)

# Row 1: çmimi, EMA, sinjalet
fig.add_trace(go.Scatter(
    x=df.index, y=df["price"],
    mode="lines",
    name="Çmimi",
    line=dict(color="blue")
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["ema12"],
    mode="lines",
    name="EMA12",
    line=dict(color="orange")
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["ema26"],
    mode="lines",
    name="EMA26",
    line=dict(color="purple")
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["price"],
    mode="markers",
    name="Sinjal",
    marker=dict(color=colors, size=7)
), row=1, col=1)

# Row 2: RSI
fig.add_trace(go.Scatter(
    x=df.index, y=df["rsi"],
    mode="lines",
    name="RSI",
    line=dict(color="teal")
), row=2, col=1)

fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# Row 3: MACD
fig.add_trace(go.Scatter(
    x=df.index, y=df["macd"],
    mode="lines",
    name="MACD",
    line=dict(color="blue")
), row=3, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["macd_signal"],
    mode="lines",
    name="MACD Signal",
    line=dict(color="orange")
), row=3, col=1)

fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=1)

fig.update_layout(
    height=900,
    showlegend=True,
    title=f"Analizë Intraday për {selected_coin} (3 orët e fundit)"
)

st.plotly_chart(fig, use_container_width=True)

# =======================
#  TABELA E FUNDIt
# =======================
st.subheader("📋 Minutat e fundit (Të dhënat e fundit)")
st.dataframe(
    df.tail(10)[[
        "price",
        "rsi",
        "ema12",
        "ema26",
        "macd",
        "macd_signal",
        "signal",
        "text_signal"
    ]]
)