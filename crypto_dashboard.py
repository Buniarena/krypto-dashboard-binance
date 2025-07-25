import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Lista e kriptove me CoinGecko ID
coins = {
    "Bitcoin": "bitcoin",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📊 Krypto Dashboard me Analizë Teknike")

for name, cg_id in coins.items():
    st.header(f"{name} ({cg_id.upper()})")

    # Marrja e të dhënave historike (30 ditë)
    url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart"
    params = {"vs_currency": "usd", "days": "30", "interval": "daily"}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.warning(f"Nuk u morën të dhëna për {name}")
        continue

    data = response.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    # Llogaritja RSI dhe MACD
    df["rsi"] = RSIIndicator(close=df["price"]).rsi()
    macd = MACD(close=df["price"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    # Grafik interaktiv
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi", line=dict(color="blue")))
    fig.update_layout(title=f"Çmimi i {name}", xaxis_title="Data", yaxis_title="USD", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Grafik RSI
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="orange")))
    fig_rsi.update_layout(title="RSI (Relative Strength Index)", yaxis_range=[0, 100])
    st.plotly_chart(fig_rsi, use_container_width=True)

    # Sinjali i fundit
    last_rsi = df["rsi"].iloc[-1]
    signal = ""
    if last_rsi < 30:
        signal = "📈 BLEJ (RSI < 30)"
        st.success(signal)
    elif last_rsi > 70:
        signal = "📉 SHIT (RSI > 70)"
        st.error(signal)
    else:
        signal = "⏸ ASNJË SINJAL (RSI në zonë neutrale)"
        st.info(signal)

    st.markdown("---")
