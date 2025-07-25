import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import MACD
import matplotlib.pyplot as plt

st.set_page_config(page_title="Krypto Dashboard me Analizë", layout="wide")
st.title("📊 Dashboard Krypto me Analizë Teknike (RSI & MACD)")

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
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Gabim gjatë marrjes së të dhënave për {coin_id}: {e}")
        return None

def analyze(df):
    df["RSI"] = RSIIndicator(df["price"], window=14).rsi()
    macd_indicator = MACD(df["price"])
    df["MACD"] = macd_indicator.macd()
    df["MACD_signal"] = macd_indicator.macd_signal()
    df["MACD_diff"] = macd_indicator.macd_diff()
    # Sinjale bazuar tek RSI
    last_rsi = df["RSI"].iloc[-1]
    if last_rsi < 30:
        rsi_signal = "📥 BLEJ (RSI < 30)"
    elif last_rsi > 70:
        rsi_signal = "📤 SHIT (RSI > 70)"
    else:
        rsi_signal = "⏸ MBANJE (RSI normal)"
    # Sinjal bazuar tek MACD (kryqëzimi i MACD me MACD_signal)
    last_macd = df["MACD"].iloc[-1]
    last_signal = df["MACD_signal"].iloc[-1]
    if last_macd > last_signal:
        macd_signal = "📈 Trend pozitiv (MACD mbi sinjal)"
    else:
        macd_signal = "📉 Trend negativ (MACD poshtë sinjalit)"
    return df, rsi_signal, macd_signal

for name, coin_id in coins.items():
    st.subheader(name)
    df = fetch_data(coin_id)
    if df is not None and not df.empty:
        df, rsi_signal, macd_signal = analyze(df)

        st.write(f"💰 Çmimi i fundit: **${df['price'].iloc[-1]:,.4f}**")
        st.write(f"📊 Sinjali RSI: **{rsi_signal}**")
        st.write(f"📈 Sinjali MACD: **{macd_signal}**")

        # Grafikët
        with st.expander("📉 Grafik çmimi"):
            st.line_chart(df["price"])

        with st.expander("📈 Grafik RSI"):
            fig, ax = plt.subplots()
            df["RSI"].plot(ax=ax, color="blue")
            ax.axhline(30, color="green", linestyle="--")
            ax.axhline(70, color="red", linestyle="--")
            ax.set_title("RSI")
            st.pyplot(fig)

        with st.expander("📊 Grafik MACD"):
            fig, ax = plt.subplots()
            df["MACD"].plot(ax=ax, label="MACD", color="purple")
            df["MACD_signal"].plot(ax=ax, label="Signal", color="orange")
            ax.fill_between(df.index, df["MACD_diff"], 0, alpha=0.3, color="grey")
            ax.legend()
            ax.set_title("MACD")
            st.pyplot(fig)

    else:
        st.warning(f"Nuk u morën të dhëna për {name}.")
