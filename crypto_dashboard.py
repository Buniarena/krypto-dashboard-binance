import streamlit as st
import requests
import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

st.set_page_config(page_title="Kripto Dashboard", layout="wide")

st.title("📊 Dashboard: BTC, ETH, XRP - RSI & MA")
st.caption("Live nga CoinGecko | Auto-refresh çdo 15 sek | Cache 5 min")

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "XRP": "ripple"
}

@st.cache_data(ttl=300)  # ruan të dhënat për 5 minuta
def fetch_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minute"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    prices = r.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

def analyze(df):
    df["SMA_20"] = SMAIndicator(df["price"], window=20).sma_indicator()
    df["RSI"] = RSIIndicator(df["price"], window=14).rsi()
    return df

placeholder = st.empty()

while True:
    with placeholder.container():
        cols = st.columns(len(coins))
        for i, (name, coin_id) in enumerate(coins.items()):
            try:
                df = fetch_data(coin_id)
                df = analyze(df)
                price_now = df["price"].iloc[-1]
                rsi_now = df["RSI"].iloc[-1]
                ma_now = df["SMA_20"].iloc[-1]

                with cols[i]:
                    st.subheader(f"{name}")
                    st.metric("💰 Çmimi", f"${price_now:,.2f}")
                    st.write(f"📉 RSI: **{rsi_now:.2f}**")
                    st.write(f"📈 MA 20: **{ma_now:.2f}**")
                    if rsi_now < 30:
                        st.success("Sinjal: BLEJ 📥")
                    elif rsi_now > 70:
                        st.error("Sinjal: SHIT 📤")
                    else:
                        st.info("Sinjal: NEUTRAL ⏸")
                    st.line_chart(df[["price", "SMA_20"]])

            except Exception as e:
                st.error(f"Gabim për {name}: {e}")

    time.sleep(15)  # auto-refresh çdo 15 sek
