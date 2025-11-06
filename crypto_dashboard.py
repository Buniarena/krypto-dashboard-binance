# app.py — ElbuharBot PRO (vetëm PEPE, SHIBA, XVG) — refresh 30s, fallback CoinGecko->Binance
import streamlit as st
import requests, time, random
import pandas as pd
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ================== KONFIG ==================
REFRESH_INTERVAL = 30  # çdo 30 sekonda
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1635321380509-9c5e91b7f82c?auto=format&fit=crop&w=1600&q=80"

# Vetëm këto tre: PEPE, SHIB, XVG
COINS = {
    "🐸 PEPE": ("pepe", "PEPEUSDT"),
    "🐕 Shiba Inu": ("shiba-inu", "SHIBUSDT"),
    "⚡ Verge (XVG)": ("verge", "XVGUSDT"),
}

# Sidebar: opsionale CoinGecko API key
st.sidebar.header("⚙️ Settings")
CG_API_KEY = st.sidebar.text_input("CoinGecko API key (opsionale)", type="password")
st.sidebar.caption("Nëse bosh, do provojë pa key. Fallback te Binance automatikisht.")
UA = {"User-Agent": "ElbuharBot/1.0 (+streamlit)"}  # ndihmon kundër bllokimeve

# ================== HELPER: HTTP me retry/backoff ==================
def http_get_json(url, params=None, headers=None, max_retry=4):
    if headers is None: headers = {}
    headers = {**UA, **headers}
    delay = 0.8
    last_err = None
    for _ in range(max_retry):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.json(), None
            if r.status_code in (429, 403, 500, 502, 503, 504):
                last_err = f"{r.status_code}: {r.text[:120]}"
                time.sleep(delay); delay = min(delay*1.8, 5)
                continue
            return None, f"{r.status_code}: {r.text[:200]}"
        except Exception as e:
            last_err = str(e)
            time.sleep(delay); delay = min(delay*1.8, 5)
    return None, last_err or "unknown error"

# ================== DATASOURCES ==================
def get_current_cg(coin_id):
    headers = {}
    if CG_API_KEY:
        headers = {"x-cg-demo-api-key": CG_API_KEY}
    url = "https://api.coingecko.com/api/v3/coins/markets"
    js, err = http_get_json(url, {"vs_currency":"usd","ids":coin_id}, headers=headers)
    if js and isinstance(js, list) and js:
        return {"price": float(js[0]["current_price"]),
                "volume": float(js[0].get("total_volume", 0))}, None
    return None, err or "empty response from CoinGecko"

def get_hist_cg(coin_id, hours=3):
    headers = {}
    if CG_API_KEY:
        headers = {"x-cg-demo-api-key": CG_API_KEY}
    now_sec = int(time.time())
    frm_sec = now_sec - hours*3600
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    js, err = http_get_json(url, {"vs_currency":"usd","from":str(frm_sec),"to":str(now_sec)}, headers=headers)
    if js and "prices" in js and js["prices"]:
        df = pd.DataFrame(js["prices"], columns=["ts","price"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        df = df.dropna()
        df = df[~df["ts"].duplicated(keep="last")]
        df = df.set_index("ts").sort_index()
        return df, None
    return None, err or "empty prices from CoinGecko"

def get_current_binance(symbol):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    js, err = http_get_json(url, {"symbol": symbol})
    if js and "lastPrice" in js:
        return {"price": float(js["lastPrice"]), "volume": float(js.get("volume",0))}, None
    return None, err or "empty response from Binance"

def get_hist_binance(symbol, interval="5m", limit=36):
    url = "https://api.binance.com/api/v3/klines"
    js, err = http_get_json(url, {"symbol":symbol, "interval":interval, "limit":limit})
    if js and isinstance(js, list) and js:
        rows = []
        for k in js:
            ts = pd.to_datetime(k[0], unit="ms")
            close = float(k[4])
            rows.append((ts, close))
        df = pd.DataFrame(rows, columns=["ts","price"]).set_index("ts").sort_index()
        return df, None
    return None, err or "empty klines from Binance"

# Wrapper me fallback: CoinGecko -> Binance
def get_current_data(coin_id, symbol):
    data, err = get_current_cg(coin_id)
    if data: return data, None, "CoinGecko"
    data, err2 = get_current_binance(symbol)
    if data: return data, None, "Binance"
    return None, f"CG:{err} | BIN:{err2}", None

def get_hist_df(coin_id, symbol):
    df, err = get_hist_cg(coin_id, hours=3)
    if df is not None and not df.empty: return df, None, "CoinGecko"
    df, err2 = get_hist_binance(symbol, "5m", 36)
    if df is not None and not df.empty: return df, None, "Binance"
    return None, f"CG:{err} | BIN:{err2}", None

# ================== UI – NEON STYLE ==================
st.markdown("""
    <style>
    body { background-color:black; color:white; }
    .neon {
        font-size: 60px; text-align:center;
        color: #00FFB2;
        text-shadow: 0 0 10px #00FFB2, 0 0 30px #00FFB2, 0 0 50px #00FFB2;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%{opacity:1;} 50%{opacity:0.55;} 100%{opacity:1;} }
    .countdown { text-align:center; font-size:20px; color:#00FFC6; margin-top:10px; }
    </style>
""", unsafe_allow_html=True)

st.image(HEADER_IMAGE_URL, use_column_width=True)
st.markdown("<h1 style='text-align:center; color:#00E0FF;'>💹 ElbuharBot PRO – Neon Live Radar</h1>", unsafe_allow_html=True)
st.caption(f"⚡ 3 orë histori | Auto-refresh çdo {REFRESH_INTERVAL}s | Fallback CG→Binance")

# ZGJEDH MONEDHËN
label = st.selectbox("💎 Zgjidh monedhën:", list(COINS.keys()))
coin_id, symbol = COINS[label]

# MERR TË DHËNA (me fallback)
current, err_cur, source_cur = get_current_data(coin_id, symbol)
df, err_hist, source_hist = get_hist_df(coin_id, symbol)

if (not current) or (df is None or df.empty):
    st.error("❌ Nuk mund të merren të dhënat tani.")
    if err_cur: st.code(f"[Current] {err_cur}")
    if err_hist: st.code(f"[History] {err_hist}")
    st.stop()

# ================== INDIKATORËT ==================
df["rsi"] = RSIIndicator(df["price"]).rsi()
df["ema12"] = EMAIndicator(df["price"], 12).ema_indicator()
df["ema26"] = EMAIndicator(df["price"], 26).ema_indicator()
macd = MACD(df["price"])
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()
bb = BollingerBands(df["price"])
df["boll_upper"] = bb.bollinger_hband()
df["boll_lower"] = bb.bollinger_lband()

def score_row(row):
    s = 0
    if pd.notna(row.rsi):
        s += 1 if row.rsi < 30 else -1 if row.rsi > 70 else 0
    s += 1 if pd.notna(row.ema12) and pd.notna(row.ema26) and row.ema12 > row.ema26 else -1
    s += 2 if pd.notna(row.macd) and pd.notna(row.macd_signal) and row.macd > row.macd_signal else -2
    if pd.notna(row.price) and pd.notna(row.boll_upper) and pd.notna(row.boll_lower):
        s += 1 if row.price < row.boll_lower else -1 if row.price > row.boll_upper else 0
    return s

df["signal"] = df.apply(score_row, axis=1)

def classify(s):
    return "🟢 BLI" if s >= 3 else ("🔴 SHIT" if s <= -3 else "🟡 MBANJ")

df["signal_text"] = df["signal"].apply(classify)

latest = df.iloc[-1]
signal_text = latest.signal_text
color = "lime" if "BLI" in signal_text else ("red" if "SHIT" in signal_text else "yellow")
prob_up = min(95, max(5, 50 + latest.signal*10 + random.randint(-5,5)))
prob_down = 100 - prob_up

# ================== SINJALI NË KRYE ==================
st.markdown(f"<div class='neon' style='color:{color};'>{signal_text}</div>", unsafe_allow_html=True)
st.caption(f"📡 Burim çmimi: {source_cur} | Histori: {source_hist}")

# ================== GAUGE ==================
radar = go.Figure()
radar.add_trace(go.Indicator(
    mode="gauge+number+delta",
    value=prob_up,
    delta={'reference': 50},
    title={'text': "📈 Mundësia për ngritje"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': color},
        'steps': [
            {'range': [0, 40], 'color': 'rgba(255,0,0,0.3)'},
            {'range': [40, 60], 'color': 'rgba(255,255,0,0.3)'},
            {'range': [60, 100], 'color': 'rgba(0,255,0,0.3)'}
        ],
    }
))
radar.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
st.plotly_chart(radar, use_container_width=True)

# ================== GRAFIKU ==================
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4],
                    subplot_titles=(f"{label} – Çmimi & EMA", "RSI & MACD"))
fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi", line=dict(color="#00E5FF", width=2)))
fig.add_trace(go.Scatter(x=df.index, y=df["ema12"], name="EMA12", line=dict(color="#FFA500", width=1)))
fig.add_trace(go.Scatter(x=df.index, y=df["ema26"], name="EMA26", line=dict(color="#9400D3", width=1)))
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="teal", width=2)), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
fig.update_layout(height=820, paper_bgcolor="black", plot_bgcolor="black", font=dict(color="white"))
st.plotly_chart(fig, use_container_width=True)

# ================== PANEL & TIMER ==================
col1, col2 = st.columns(2)
col1.metric("💵 Çmimi aktual", f"${current['price']:.6f}")
col2.metric("📊 Vëllimi 24h", f"${current['volume']:,.0f}")

st.markdown("<hr>", unsafe_allow_html=True)
placeholder = st.empty()
for sec in range(REFRESH_INTERVAL, 0, -1):
    placeholder.markdown(
        f"<div class='countdown'>⏳ Rifreskim pas {sec} sekondash...</div>",
        unsafe_allow_html=True
    )
    time.sleep(1)
    placeholder.empty()

st.rerun()