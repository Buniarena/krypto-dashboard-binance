import streamlit as st 
import pandas as pd 
import requests 
import datetime from ta.momentum 
import RSIIndicator from ta.trend 
import MACD

Konfiguro faqen

st.set_page_config(page_title="📈 Live Crypto Dashboard", layout="wide") st.title("📊 Live Crypto Dashboard me Sygjerime Bli/Shit/Mbaj")

Lista e coin-ave

coins = { "BTC 🟠": "bitcoin", "XVG 🧿": "verge", "FLOKI 🐶": "floki", "PEPE 🐸": "pepecoin-community", "VET 🔗": "vechain", "BONK 🦴": "bonk", "DOGE 🐕": "dogecoin", "SHIB 🦊": "shiba", "WIN 🎯": "wink", "BTT 📡": "bittorrent-2" }

Funksioni për të marrë historikun e çmimeve

@st.cache_data(ttl=300) def get_price_history(coin_id): url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart" params = {"vs_currency": "usd", "days": "7", "interval": "hourly"} r = requests.get(url, params=params) if r.status_code != 200: return None prices = r.json()["prices"] df = pd.DataFrame(prices, columns=["timestamp", "price"]) df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms") return df

Funksioni për të analizuar të dhënat

def analyze_coin(df): df = df.copy() df.set_index("timestamp", inplace=True) df["rsi"] = RSIIndicator(df["price"], window=14).rsi() macd = MACD(df["price"], window_slow=26, window_fast=12, window_sign=9) df["macd"] = macd.macd() df["macd_signal"] = macd.macd_signal()

last_rsi = df["rsi"].iloc[-1]
last_macd = df["macd"].iloc[-1]
last_signal = df["macd_signal"].iloc[-1]

# Vendimi
if last_rsi < 30 and last_macd > last_signal:
    decision = "🟢 BLIJ"
elif last_rsi > 70 and last_macd < last_signal:
    decision = "🔴 SHIT"
else:
    decision = "🟡 MBAJ"

return df, last_rsi, last_macd, last_signal, decision

Aplikimi për çdo coin

for name, coin_id in coins.items(): st.subheader(f"{name}") df = get_price_history(coin_id) if df is None: st.warning("Nuk u ngarkuan të dhënat.") continue

df_analysis, rsi, macd, signal, vendim = analyze_coin(df)

# Grafiku
st.line_chart(df.set_index("timestamp")["price"], use_container_width=True)

# Tabela e analizës
col1, col2, col3, col4 = st.columns(4)
col1.metric("RSI", f"{rsi:.2f}")
col2.metric("MACD", f"{macd:.4f}")
col3.metric("MACD Signal", f"{signal:.4f}")
col4.metric("Vendimi", vendim)

st.caption("📡 Të dhënat janë marrë nga CoinGecko dhe përditësohen çdo 5 minuta.")

