import streamlit as st
import requests
import pandas as pd
import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Coin-at që duam të monitorojmë
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

st.set_page_config(page_title="📊 Krypto Sinjal Dashboard", layout="wide")
st.title("📈 Krypto Sinjal Dashboard (CoinGecko + RSI/MACD)")

# Funksioni për të marrë çmimet historike (për RSI dhe MACD)
def fetch_market_chart(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "hourly"}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    return None

# Funksioni për analizë teknike dhe vendim
def analyze_signal(df):
    if df is None or len(df) < 26:
        return "N/A", None

    rsi = RSIIndicator(df["price"], window=14).rsi()
    macd = MACD(df["price"]).macd_diff()

    latest_rsi = rsi.iloc[-1]
    latest_macd = macd.iloc[-1]

    if latest_rsi < 30 and latest_macd > 0:
        return "🟢 BLIJ", latest_rsi
    elif latest_rsi > 70 and latest_macd < 0:
        return "🔴 SHIT", latest_rsi
    else:
        return "🟡 MBAJ", latest_rsi

# Marrja e çmimeve të momentit
def fetch_live_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    ids = ",".join(coins.values())
    params = {
        "ids": ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    r = requests.get(url, params=params)
    return r.json() if r.status_code == 200 else {}

# Shfaqja e tabelës
def show_dashboard():
    data = fetch_live_prices()
    all_rows = []

    for name, coin_id in coins.items():
        price = data.get(coin_id, {}).get("usd", "N/A")
        change = data.get(coin_id, {}).get("usd_24h_change", 0)

        df = fetch_market_chart(coin_id)
        vendim, rsi = analyze_signal(df)

        # Mini-grafiku
        if df is not None:
            with st.expander(f"{name} 📉 Mini Grafik"):
                st.line_chart(df.set_index("timestamp")["price"])

        row = {
            "Coin": name,
            "Çmimi ($)": round(price, 6),
            "Ndryshim 24h (%)": round(change, 2),
            "RSI": round(rsi, 2) if rsi else "N/A",
            "Vendim": vendim
        }
        all_rows.append(row)

    st.dataframe(pd.DataFrame(all_rows), use_container_width=True)

# Ekzekuto dashboardin
show_dashboard()
st.caption("📡 Të dhënat nga CoinGecko • RSI/MACD analizë • Rifreskim manual")
