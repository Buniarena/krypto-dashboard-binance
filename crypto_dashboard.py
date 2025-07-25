import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
import matplotlib.pyplot as plt

st.set_page_config(page_title="Krypto RSI", layout="wide")
st.title("📊 Analiza Ditore e Kriptomonedhave + RSI")

coins = {
    "Bitcoin (BTC)": "bitcoin",
    "Dogecoin (DOGE)": "dogecoin",
    "XRP (Ripple)": "ripple"
}

def fetch_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "hourly"}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, params=params, headers=headers)
        data = res.json()["prices"]
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        st.warning(f"⚠️ Nuk u morën të dhëna për {coin_id.upper()}: {e}")
        return None

def analyze(df):
    rsi = RSIIndicator(df["price"]).rsi()
    df["RSI"] = rsi
    last = rsi.iloc[-1]
    signal = "📥 BLEJ" if last < 30 else "📤 SHIT" if last > 70 else "⏸ MBANJE"
    return df, last, signal

for name, id in coins.items():
    st.subheader(name)
    df = fetch_data(id)
    if df is not None:
        st.line_chart(df["price"])
        df, rsi_val, signal = analyze(df)
        st.markdown(f"**💰 Çmimi i fundit:** ${df['price'].iloc[-1]:,.2f}")
        st.markdown(f"**📈 RSI:** {rsi_val:.2f} → {signal}")
        with st.expander("Shfaq RSI chart"):
            fig, ax = plt.subplots()
            df["RSI"].plot(ax=ax, color="blue")
            ax.axhline(30, color="green", linestyle="--")
            ax.axhline(70, color="red", linestyle="--")
            ax.set_title("RSI")
            st.pyplot(fig)
    else:
        st.error(f"Nuk mund të ngarkohen të dhënat për {name}")
