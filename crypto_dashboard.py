import streamlit as st
import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD
import plotly.graph_objects as go
import datetime

# Konfigurimi i faqes
st.set_page_config(page_title="📈 Krypto Sinjal Dashboard", layout="wide")
st.title("📈 Krypto Sinjal Dashboard (CoinGecko + RSI/MACD)")

# Lista e coin-ave me ID nga CoinGecko
coins = {
    "BTC 🟠": "bitcoin",
    "XVG 🧿": "verge",
    "FLOKI 🐶": "floki",
    "PEPE 🐸": "pepecoin-community",
    "VET 🔗": "vechain",
    "BONK 🦴": "bonk",
    "DOGE 🐕": "dogecoin",
    "SHIB 🦊": "shiba",
    "WIN 🎯": "wink",
    "BTT 📡": "bittorrent-2"
}

# Funksioni për të marrë çmimet aktuale + ndryshimet 24h
@st.cache_data(ttl=300)
def fetch_current_prices():
    ids = ",".join(coins.values())
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ids,
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        st.error("❌ Nuk mund të lidhem me CoinGecko")
        return {}
    return res.json()

# Funksioni për të marrë historikun (p.sh. 7 ditë për grafik, RSI, MACD)
def fetch_historical_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': 7,
        'interval': 'hourly'
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return None
    prices = res.json().get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# Funksioni për të gjeneruar sinjalin
def generate_signal(prices):
    if prices is None or len(prices) < 50:
        return "N/A", None, None

    close = prices["price"]
    rsi = RSIIndicator(close).rsi()
    macd = MACD(close).macd_diff()

    last_rsi = rsi.iloc[-1]
    last_macd = macd.iloc[-1]

    if last_rsi < 30 and last_macd > 0:
        return "🟢 Bli", round(last_rsi, 2), round(last_macd, 4)
    elif last_rsi > 70 and last_macd < 0:
        return "🔴 Shit", round(last_rsi, 2), round(last_macd, 4)
    else:
        return "🟡 Mbaj", round(last_rsi, 2), round(last_macd, 4)

# Funksioni për grafik mini
def mini_chart(df, name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["price"],
        mode="lines", name=name, line=dict(color="deepskyblue")
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=150,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    return fig

# Marrim të dhënat
prices_now = fetch_current_prices()

# Tabela përmbledhëse
cols = ["Coin", "Çmimi ($)", "Ndryshim 24h (%)", "RSI", "MACD", "Sinjal"]
rows = []

for name, coin_id in coins.items():
    info = prices_now.get(coin_id)
    if not info:
        continue

    price = info.get("usd")
    change = info.get("usd_24h_change")

    hist = fetch_historical_data(coin_id)
    signal, rsi, macd = generate_signal(hist)

    row = {
        "Coin": name,
        "Çmimi ($)": round(price, 6) if isinstance(price, (int, float)) else "N/A",
        "Ndryshim 24h (%)": round(change, 2) if isinstance(change, (int, float)) else "N/A",
        "RSI": rsi if rsi is not None else "N/A",
        "MACD": macd if macd is not None else "N/A",
        "Sinjal": signal
    }
    rows.append((row, hist))

# Shfaq të dhënat me grafik
for row, hist in rows:
    st.subheader(row["Coin"])
    col1, col2 = st.columns([2, 3])

    with col1:
        st.metric("Çmimi", row["Çmimi ($)"], f"{row['Ndryshim 24h (%)']}%")
        st.write(f"**RSI:** {row['RSI']} • **MACD:** {row['MACD']}")
        st.write(f"**📢 Sinjal:** {row['Sinjal']}")

    with col2:
        if hist is not None:
            fig = mini_chart(hist, row["Coin"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nuk ka grafik")

st.caption("⏱️ Rifreskim çdo 5 minuta nga CoinGecko • RSI/MACD për sinjale")
