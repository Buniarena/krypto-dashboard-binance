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
    "🐸 PEPE": ("PEPEUSDT", "pepe"),
    "🐕 Shiba Inu": ("SHIBUSDT", "shiba-inu"),
    "⚡ Verge (XVG)": ("XVGUSDT", "verge")
}
st.set_page_config(page_title="ElbuharBot PRO – Hybrid Edition", layout="wide")

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

st.title("💹 ElbuharBot PRO – Hybrid Bybit + CoinGecko Radar")

# ======================== FUNKSIONE ========================
def get_current_bybit(symbol):
    try:
        url = "https://api.bybit.com/v5/market/tickers"
        params = {"category": "spot", "symbol": symbol}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "result" in data and "list" in data["result"]:
            return float(data["result"]["list"][0]["lastPrice"])
    except:
        return None
    return None

def get_current_cg(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        r = requests.get(url, params={"ids": coin_id, "vs_currencies": "usd"}, timeout=10)
        data = r.json()
        return float(data[coin_id]["usd"])
    except:
        return None

def get_historical_bybit(symbol, limit=180):
    try:
        url = "https://api.bybit.com/v5/market/kline"
        params = {"category": "spot", "symbol": symbol, "interval": "1", "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "result" not in data or "list" not in data["result"]:
            return pd.DataFrame()
        df = pd.DataFrame(data["result"]["list"], columns=["time","open","high","low","close","volume"])
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df["price"] = df["close"].astype(float)
        df = df[["time","price"]].set_index("time").sort_index()
        return df
    except:
        return pd.DataFrame()

def get_historical_cg(coin_id, hours=3):
    try:
        now = int(time.time())
        past = now - hours * 3600
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
        params = {"vs_currency": "usd", "from": str(past), "to": str(now)}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "prices" not in data:
            return pd.DataFrame()
        df = pd.DataFrame(data["prices"], columns=["time","price"])
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
symbol, cg_id = COINS[coin_label]

# Çmimi aktual (Bybit ose CG)
price = get_current_bybit(symbol)
source = "Bybit"
if not price:
    price = get_current_cg(cg_id)
    source = "CoinGecko"
if not price:
    st.error("❌ Nuk mund të merren të dhëna as nga Bybit, as nga CoinGecko.")
    st.stop()

# Historiku
df = get_historical_bybit(symbol)
if df.empty:
    df = get_historical_cg(cg_id, hours=3)
    source = "CoinGecko (fallback)"

if df.empty:
    st.warning("⚠️ Nuk u gjetën të dhëna historike.")
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
st.caption(f"📡 Burim: {source}")
col1, col2 = st.columns(2)
col1.metric("💵 Çmimi aktual", f"${price:.6f}")
col2.metric("📈 Mundësia për ngritje", f"{prob_up}%")

# ======================== GRAFIKU ========================
fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True, row_heights=[0.5,0.25,0.25],
    subplot_titles=(f"{coin_label} – Çmimi & EMA", "RSI", "MACD")
)
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
st.dataframe(df.tail(10)[[
    "price", "rsi", "ema12", "ema26",
    "macd", "macd_signal", "boll_upper",
    "boll_lower", "signal_text"
]])

# ======================== PORTOFOLI ========================
st.markdown("---")
st.header("📦 Portofoli im")

# Marrim çmimet aktuale për të gjitha monedhat e portofolit
prices_now = {}
for label, (sym, cg) in COINS.items():
    p = get_current_bybit(sym)
    if not p:
        p = get_current_cg(cg)
    prices_now[label] = p

# Ruajmë sasitë në session_state që të mos humbin me çdo refresh
if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = {label: 0.0 for label in COINS.keys()}

st.subheader("🔢 Vendos sasitë që ke në portofol")
cols_port = st.columns(len(COINS))

for i, (label, (sym, cg)) in enumerate(COINS.items()):
    with cols_port[i]:
        qty = st.number_input(
            f"{label} sasia",
            min_value=0.0,
            step=0.000001,
            value=float(st.session_state["portfolio"].get(label, 0.0)),
            format="%.6f"
        )
        st.session_state["portfolio"][label] = qty
        price_now = prices_now[label]
        if price_now:
            st.caption(f"Çmimi: ${price_now:.8f}")
        else:
            st.caption("❌ Pa çmim aktual")

# 📊 Tabela e portofolit
rows = []
total_value = 0.0

for label, qty in st.session_state["portfolio"].items():
    price_now = prices_now[label]
    if price_now is None or qty == 0:
        value = 0.0
    else:
        value = qty * price_now
    total_value += value
    rows.append({
        "Monedha": label,
        "Sasia": qty,
        "Çmimi aktual (USD)": price_now,
        "Vlera (USD)": value
    })

port_df = pd.DataFrame(rows)

st.subheader("📊 Portofoli – Vlera aktuale")
st.dataframe(port_df)
st.metric("💰 Vlera totale e portofolit", f"${total_value:,.2f}")

# 🎯 Sinjali i lidhur me portofolin për monedhën e zgjedhur
st.subheader("🎯 Sinjali për portofolin tënd")
qty_current_coin = st.session_state["portfolio"].get(coin_label, 0.0)

if qty_current_coin > 0:
    st.write(f"Ke **{qty_current_coin}** nga {coin_label}.")
    if "BLI" in sig:
        st.write("Sinjali është **BLI** – nëse beson algoritmin, mund të mendosh për rritje pozicioni (me kujdes).")
    elif "SHIT" in sig:
        st.write("Sinjali është **SHIT** – ndoshta ia vlen të mbyllësh një pjesë të pozicionit, sipas strategjisë tënde.")
    else:
        st.write("Sinjali është **MBANJ** – as blerje agresive, as shitje agresive.")
else:
    st.write(f"Nuk ke {coin_label} në portofol aktualisht.")

# ======================== TIMER ========================
ph = st.empty()
for s in range(REFRESH_INTERVAL, 0, -1):
    ph.markdown(f"<div class='countdown'>⏳ Rifreskim pas {s} sekondash...</div>", unsafe_allow_html=True)
    time.sleep(1)
ph.empty()
st.rerun()