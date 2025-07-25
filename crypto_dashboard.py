import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
import matplotlib.pyplot as plt
from datetime import datetime

# Titulli i aplikacionit
st.title("📈 Krypto Analizë Ditore me Sinjale Blerje/Shitje")
st.write("Të dhëna për 1 ditë për BTC, DOGE dhe XRP nga CoinGecko + RSI")

# Lista e kriptove dhe ID e tyre në CoinGecko
coins = {
    "Bitcoin (BTC)": "bitcoin",
    "Dogecoin (DOGE)": "dogecoin",
    "XRP (Ripple)": "ripple"
}

# Funksioni për të marrë të dhëna
def fetch_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "hourly"}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            prices = data["prices"]
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        else:
            st.warning(f"⛔ Gabim {response.status_code} nga CoinGecko")
            return None
    except Exception as e:
        st.error(f"❌ Gabim: {e}")
        return None

# Funksioni për analizë teknike dhe sinjal
def analyze_rsi(df):
    rsi = RSIIndicator(close=df["price"], window=14).rsi()
    df["RSI"] = rsi
    last_rsi = rsi.iloc[-1]

    # Vendos sinjalin sipas RSI
    if last_rsi < 30:
        signal = "📥 BLEJ (RSI < 30)"
    elif last_rsi > 70:
        signal = "📤 SHIT (RSI > 70)"
    else:
        signal = "⏸ MBANJE (RSI i qetë)"
    return df, last_rsi, signal

# Loop për çdo kripto
for name, id in coins.items():
    st.subheader(name)
    df = fetch_data(id)

    if df is not None and not df.empty:
        st.line_chart(df["price"])
        df, rsi, signal = analyze_rsi(df)

        st.write(f"💵 Çmimi i fundit: **${df['price'].iloc[-1]:,.4f}**")
        st.write(f"📊 RSI: **{rsi:.2f}**")
        st.write(f"📢 Sinjali: **{signal}**")

        with st.expander("📉 Shfaq grafikun RSI"):
            fig, ax = plt.subplots()
            df["RSI"].plot(ax=ax)
            ax.axhline(30, color='green', linestyle='--', label="Bli (30)")
            ax.axhline(70, color='red', linestyle='--', label="Shit (70)")
            ax.set_title(f"RSI për {name}")
            ax.legend()
            st.pyplot(fig)
    else:
        st.warning(f"Nuk u morën të dhëna për {name}. Kontrollo lidhjen.")
