import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Lista e monedhave me ID nga CoinGecko
coins = {
    "Bitcoin": "bitcoin",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📊 Krypto Dashboard me Analizë Teknike")

# Funksion për të marrë të dhëna historike
def get_price_history(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    return None

# Loop për çdo monedhë
for name, cg_id in coins.items():
    st.subheader(f"{name} ({cg_id.upper()})")
    df = get_price_history(cg_id)

    if df is None or df.empty:
        st.error(f"Nuk u morën të dhëna për {name}")
        st.markdown("---")
        continue

    # Llogarit RSI dhe MACD
    df["RSI"] = RSIIndicator(close=df["price"]).rsi()
    macd = MACD(close=df["price"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    # Grafik i çmimit
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi", line=dict(color="blue")))
    fig.update_layout(title="📈 Çmimi në 30 ditët e fundit", xaxis_title="Data", yaxis_title="USD", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # RSI
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="orange")))
    fig_rsi.update_layout(title="📊 RSI (Relative Strength Index)", yaxis_range=[0, 100])
    st.plotly_chart(fig_rsi, use_container_width=True)

    # MACD
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="green")))
    fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal", line=dict(color="red")))
    fig_macd.update_layout(title="📉 MACD", height=300)
    st.plotly_chart(fig_macd, use_container_width=True)

    # Sinjal blerje/shitje nga RSI
    latest_rsi = df["RSI"].iloc[-1]
    if latest_rsi < 30:
        st.success("📥 SINJAL: BLEJ (RSI < 30)")
    elif latest_rsi > 70:
        st.error("📤 SINJAL: SHIT (RSI > 70)")
    else:
        st.info("⏸ SINJAL: PRITJE (RSI në zonë neutrale)")

    st.markdown("---")
