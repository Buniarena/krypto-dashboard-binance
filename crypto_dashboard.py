import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import time

# ⚙️ Titulli
st.title("📊 Çmimet dhe Analiza RSI & MA – BTC, ETH, XRP")

# ⏱️ Auto-refresh çdo 15 sekonda
st_autorefresh = st.experimental_rerun
st.caption("⏳ Rifreskim automatik çdo 15 sekonda (Cache 5 min)")

@st.cache_data(ttl=300)
def fetch_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "1",
            "interval": "minute"
        }
        headers = {
            "User-Agent": "MyCryptoDashboard/1.0"
        }
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        prices = r.json()["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        return None

def show_analysis(name, coin_id):
    df = fetch_data(coin_id)
    st.subheader(f"{name}")
    if df is None or df.empty:
        st.error(f"Nuk u morën të dhëna për {name}.")
        return

    price = df["price"].iloc[-1]
    rsi = RSIIndicator(df["price"]).rsi().iloc[-1]
    ma = SMAIndicator(df["price"], window=20).sma_indicator().iloc[-1]

    st.write(f"💰 **Çmimi aktual:** ${price:,.2f}")
    st.write(f"📈 **Mesatarja 20P (MA):** ${ma:,.2f}")
    st.write(f"📊 **RSI:** {rsi:.2f}")

    # ✅ Sinjal i thjeshtë bazuar në RSI
    if rsi > 70:
        st.warning("📉 RSI: OVERBOUGHT – Mund të bjerë")
    elif rsi < 30:
        st.success("📈 RSI: OVERSOLD – Mund të rritet")
    else:
        st.info("⏸ RSI: NEUTRAL")

    # 📈 Grafik për çmimin
    st.line_chart(df["price"])

# 🔄 Trego të dhënat për secilën kriptomonedhë
show_analysis("Bitcoin", "bitcoin")
show_analysis("Ethereum", "ethereum")
show_analysis("XRP", "ripple")

# Auto-refresh pas 15 sekondave
time.sleep(15)
st.experimental_rerun()
