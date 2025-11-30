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

st.set_page_config(page_title="ElbuharBot PRO – Binance Edition", layout="wide")

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

st.title("💹 ElbuharBot PRO – Binance Radar + Portofol")

# ======================== FUNKSIONE ========================
BINANCE_BASE = "https://api.binance.com"

def get_current_price(symbol):
    """Çmimi aktual nga Binance."""
    try:
        url = f"{BINANCE_BASE}/api/v3/ticker/price"
        r = requests.get(url, params={"symbol": symbol}, timeout=10)
        if r.status_code != 200:
            st.write("Binance price status:", r.status_code, r.text[:200])
            return None
        data = r.json()
        return float(data["price"])
    except Exception as e:
        st.write("Gabim Binance price:", e)
        return None


def get_historical_binance(symbol, interval="1m", limit=180):
    """Historik candlestick nga Binance."""
    try:
        url = f"{BINANCE_BASE}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            st.write("Binance kline status:", r.status_code, r.text[:200])
            return pd.DataFrame()

        data = r.json()
        if not data:
            return pd.DataFrame()

        # Kline format: [openTime, open, high, low, close, volume, ...]
        rows = []
        for k in data:
            open_time = int(k[0])   # ms
            close_price = float(k[4])
            rows.append([open_time, close_price])

        df = pd.DataFrame(rows, columns=["time", "price"])
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        df = df.set_index("time").sort_index()
        return df

    except Exception as e:
        st.write("Gabim Binance kline:", e)
        return pd.DataFrame()


def generate_signal(row):
    s = 0
    if pd.notna(row.rsi):
        if row.rsi < 30:
            s += 1
        elif row.rsi > 70:
            s -= 1
    if pd.notna(row.ema12) and pd.notna(row.ema26):
        s += 1 if row.ema12 > row.ema26 else -1
    if pd.notna(row.macd) and pd.notna(row.macd_signal):
        s += 2 if row.macd > row.macd_signal else -2
    if pd.notna(row.price) and pd.notna(row.boll_upper) and pd.notna(row.boll_lower):
        if row.price < row.boll_lower:
            s += 1
        elif row.price > row.boll_upper:
            s -= 1
    return s


def classify_signal(s):
    if s >= 3:
        return "🟢 BLI"
    elif s <= -3:
        return "🔴 SHIT"
    else:
        return "🟡 MBANJ"


# ======================== UI ========================
coin_label = st.selectbox("💎 Zgjidh monedhën:", list(COINS.keys()))
symbol, cg_id = COINS[coin_label]

# Çmimi aktual (Binance)
price = get_current_price(symbol)
source = "Binance"

if price is None:
    st.error("❌ Nuk mund të merren të dhëna nga Binance.")
    st.stop()

# Historiku nga Binance
df = get_historical_binance(symbol, interval="1m", limit=180)

if df.empty:
    st.warning("⚠️ Nuk u gjetën të dhëna historike nga Binance.")
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
prob_up = min(95, max(5, 50 + last.signal * 10 + random.randint(-5, 5)))

# ======================== SINJALI ========================
st.markdown(f"<div class='neon' style='color:{color};'>{sig}</div>", unsafe_allow_html=True)
st.caption(f"📡 Burim: {source}")

col1, col2 = st.columns(2)
col1.metric("💵 Çmimi aktual", f"${price:.6f}")
col2.metric("📈 Mundësia për ngritje", f"{prob_up}%")

# ======================== GRAFIKU ========================
fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.25, 0.25],
    subplot_titles=(f"{coin_label} – Çmimi & EMA", "RSI", "MACD")
)

fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi",
                         line=dict(color="#00E5FF", width=2)))
fig.add_trace(go.Scatter(x=df.index, y=df["ema12"], name="EMA12",
                         line=dict(color="#FFA500")))
fig.add_trace(go.Scatter(x=df.index, y=df["ema26"], name="EMA26",
                         line=dict(color="#9400D3")))

fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI",
                         line=dict(color="teal")), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df["macd"], name="MACD",
                         line=dict(color="blue")), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], name="MACD Signal",
                         line=dict(color="orange")), row=3, col=1)
fig.add_trace(go.Bar(x=df.index, y=df["macd_histogram"], name="Histogram",
                     marker_color="gray"), row=3, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="white", row=3, col=1)

fig.update_layout(
    height=900,
    paper_bgcolor="black",
    plot_bgcolor="black",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# ======================== TABELA ========================
st.subheader("📊 Të dhënat e fundit (10 rreshta)")
st.dataframe(df.tail(10)[[
    "price", "rsi", "ema12", "ema26",
    "macd", "macd_signal",
    "boll_upper", "boll_lower",
    "signal_text"
]])

# ======================== PORTOFOLI ========================
st.markdown("---")
st.header("📦 Portofoli im")

# Marrim çmimet aktuale për të gjitha monedhat (Binance)
prices_now = {}
for label, (sym, cg) in COINS.items():
    p = get_current_price(sym)
    prices_now[label] = p

# Ruajmë sasitë në session_state
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
        if price_now is not None:
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

# 🎯 Sinjali për monedhën e zgjedhur, lidhur me portofolin
st.subheader("🎯 Sinjali për portofolin tënd")
qty_current_coin = st.session_state["portfolio"].get(coin_label, 0.0)

if qty_current_coin > 0:
    st.write(f"Ke **{qty_current_coin}** nga {coin_label}.")
    if "BLI" in sig:
        st.write("Sinjali është **BLI** – mund të mendosh për rritje pozicioni (me strategji të kujdesshme).")
    elif "SHIT" in sig:
        st.write("Sinjali është **SHIT** – mund të mendosh për mbyllje të një pjese të pozicionit.")
    else:
        st.write("Sinjali është **MBANJ** – as blerje agresive, as shitje agresive.")
else:
    st.write(f"Nuk ke {coin_label} në portofol aktualisht.")

# ======================== ALBUNI STRATEGY KALKULATOR ========================
st.markdown("---")
st.header("🧮 Albuni Strategy – Kalkulatori i Hedging (Futures + Spot)")

colA, colB = st.columns(2)

with colA:
    investimi_total = st.number_input(
        "💰 Investimi total (USDT)",
        min_value=0.0,
        value=20000.0,
        step=100.0
    )
    spot_pct = st.slider("📊 Përqindja në SPOT (%)", 0, 100, 70)
    leverage = st.number_input(
        "⚙️ Leverage për FUTURES (x)",
        min_value=1.0,
        value=2.0,
        step=0.5
    )

with colB:
    futures_pct = 100 - spot_pct
    st.write(f"📉 Përqindja në FUTURES: **{futures_pct}%**")
    drop_percent = st.number_input(
        "📉 Rënia ku mbyll SHORT-in (–%)",
        min_value=0.1,
        max_value=80.0,
        value=4.0,
        step=0.1
    )
    price_entry = st.number_input(
        "💲 Çmimi hyrës i coinit (opsionale)",
        min_value=0.0,
        value=0.00000457,
        format="%.12f"
    )

# Llogaritjet vetëm nëse ka investim
if investimi_total > 0:
    d = drop_percent / 100.0

    # Kapitali në spot & futures
    spot_cap = investimi_total * spot_pct / 100.0
    fut_margin = investimi_total * futures_pct / 100.0
    fut_notional = fut_margin * leverage

    # Në -X% rënie
    spot_loss_drop = spot_cap * d                    # humbja në SPOT
    fut_profit_drop = fut_notional * d               # fitimi në FUTURES

    spot_value_after_drop = spot_cap * (1 - d)       # vlera e spot pas rënies
    # Fitimi i futures hidhet në spot në çmimin e rënies
    spot_value_after_profit = spot_value_after_drop + fut_profit_drop

    # Rikthimi nga -X% në 0% → rritje faktori = 1/(1-d)
    factor_up = 1.0 / (1.0 - d)
    spot_final = spot_value_after_profit * factor_up

    # Futures margin mbetet siç ishte (profitin e kemi kaluar në spot)
    total_final = spot_final + fut_margin
    total_pnl_final = total_final - investimi_total

    # Totali në momentin e -X% (kur mbyll short-in)
    total_at_drop = spot_value_after_drop + fut_margin + fut_profit_drop
    total_pnl_drop = total_at_drop - investimi_total

    # Nëse kemi çmim hyrës, llogarisim edhe sasinë e coinit
    coins_initial = coins_from_profit = coins_total = None
    if price_entry > 0:
        price_drop = price_entry * (1 - d)
        coins_initial = spot_cap / price_entry
        coins_from_profit = fut_profit_drop / price_drop
        coins_total = coins_initial + coins_from_profit

    # Ndërtojmë tabelën e rezultateve
    calc_rows = [{
        "Investimi total (USDT)": round(investimi_total, 2),
        "SPOT fillestar (USDT)": round(spot_cap, 2),
        "FUTURES margin (USDT)": round(fut_margin, 2),
        "Leverage FUTURES": leverage,
        "Rënia ku mbyllet short (%)": drop_percent,
        "Fitimi FUTURES në -X% (USDT)": round(fut_profit_drop, 2),
        "Humbja SPOT në -X% (USDT)": round(spot_loss_drop, 2),
        "P&L total në -X% (USDT)": round(total_pnl_drop, 2),
        "Fitimi total kur kthehet 0% (USDT)": round(total_pnl_final, 2),
        "Totali final në 0% (USDT)": round(total_final, 2),
    }]

    if coins_total is not None:
        calc_rows[0]["Sasia fillestare (coin)"] = round(coins_initial, 2)
        calc_rows[0]["Coin nga fitimi i futures"] = round(coins_from_profit, 2)
        calc_rows[0]["Sasia totale në 0% (coin)"] = round(coins_total, 2)

    calc_df = pd.DataFrame(calc_rows)

    st.subheader("📊 Rezultatet e Albuni Strategy për këtë skenar")
    st.dataframe(calc_df)

    st.markdown(f"""
**🧾 Përmbledhje:**
- Fitimi i futures në -{drop_percent}%: **{fut_profit_drop:.2f} USDT**
- Humbja e spot në -{drop_percent}%: **{spot_loss_drop:.2f} USDT**
- P&L total në momentin –{drop_percent}%: **{total_pnl_drop:.2f} USDT**
- Fitimi total kur çmimi kthehet në 0%: **{total_pnl_final:.2f} USDT**
""")
else:
    st.info("👉 Shkruaj një shumë > 0 në 'Investimi total' për të parë llogaritjet.")

# ======================== TIMER ========================
ph = st.empty()
for s in range(REFRESH_INTERVAL, 0, -1):
    ph.markdown(
        f"<div class='countdown'>⏳ Rifreskim pas {s} sekondash...</div>",
        unsafe_allow_html=True
    )
    time.sleep(1)

ph.empty()
st.rerun()