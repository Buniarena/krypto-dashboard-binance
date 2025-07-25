import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import matplotlib.pyplot as plt

st.title("📊 PEPE Crypto Price & Analiza Teknike")

# Merr të dhëna historike 1 ditore me interval 5 minuta nga CoinGecko për PEPE
def fetch_pepe_data():
    url = "https://api.coingecko.com/api/v3/coins/pepe/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minute"}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        prices = data["prices"]  # listë [ [timestamp, price], ... ]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        st.error(f"Gabim në marrjen e të dhënave: {e}")
        return None

df = fetch_pepe_data()

if df is not None and not df.empty:
    # Llogarit RSI dhe MACD
    df["RSI"] = RSIIndicator(df["price"], window=14).rsi()
    macd = MACD(df["price"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_diff"] = macd.macd_diff()

    st.write(f"Çmimi aktual i PEPE: **${df['price'].iloc[-1]:.6f}**")

    # Sinjali RSI
    rsi_now = df["RSI"].iloc[-1]
    if rsi_now < 30:
        st.success(f"Sinjal RSI: BLEJ (RSI = {rsi_now:.2f} < 30)")
    elif rsi_now > 70:
        st.warning(f"Sinjal RSI: SHIT (RSI = {rsi_now:.2f} > 70)")
    else:
        st.info(f"Sinjal RSI: NEUTRAL (RSI = {rsi_now:.2f})")

    # Sinjali MACD
    if df["MACD"].iloc[-1] > df["MACD_signal"].iloc[-1]:
        st.success("Sinjal MACD: Trend pozitiv (MACD > Signal)")
    else:
        st.warning("Sinjal MACD: Trend negativ (MACD < Signal)")

    # Grafikët
    st.subheader("Grafiku i Çmimit të PEPE")
    st.line_chart(df["price"])

    st.subheader("Grafiku RSI")
    fig, ax = plt.subplots()
    df["RSI"].plot(ax=ax)
    ax.axhline(30, color="green", linestyle="--")
    ax.axhline(70, color="red", linestyle="--")
    st.pyplot(fig)

    st.subheader("Grafiku MACD")
    fig2, ax2 = plt.subplots()
    df["MACD"].plot(ax=ax2, label="MACD")
    df["MACD_signal"].plot(ax=ax2, label="Signal")
    ax2.fill_between(df.index, df["MACD_diff"], 0, alpha=0.3, color="grey")
    ax2.legend()
    st.pyplot(fig2)

else:
    st.error("Nuk u morën të dhëna për PEPE.")
