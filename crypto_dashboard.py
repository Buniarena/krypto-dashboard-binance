import streamlit as st
import pandas as pd
import requests
import ta
import datetime

# Coinet dhe emrat e tyre në CoinGecko
coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk"
}

# Konfigurimi i faqes
st.set_page_config(page_title="📈 RSI Dashboard", layout="centered")
st.title("📊 RSI dhe Çmimi për Coinet")

# Funksioni për të marrë të dhëna historike për çdo coin
def get_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "2",  # 2 ditë për të marrë 1h interval
        "interval": "hourly"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        prices = response.json()["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    else:
        return None

# Funksioni për të llogaritur RSI
def calculate_rsi(df):
    if len(df) < 20:
        return None
    rsi = ta.momentum.RSIIndicator(df["price"]).rsi()
    return round(rsi.iloc[-1], 2)

# Funksioni për sinjalin
def get_signal(rsi):
    if rsi is None:
        return "❓ Nuk ka të dhëna"
    elif rsi < 30:
        return "🟢 Bli"
    elif rsi > 70:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

# Shfaq të dhënat për çdo coin
for name, coin_id in coins.items():
    with st.container():
        st.markdown(f"### {name}")
        df = get_price_history(coin_id)
        if df is not None:
            price = round(df["price"].iloc[-1], 6)
            rsi = calculate_rsi(df)
            signal = get_signal(rsi)
            st.write(f"💰 **Çmimi aktual:** ${price}")
            st.write(f"📈 **RSI:** {rsi if rsi is not None else 'N/A'}")
            st.write(f"📊 **Sinjali:** {signal}")
        else:
            st.warning("Nuk u morën të dhënat. CoinGecko mund të jetë offline.")

st.caption("🔄 Të dhënat rifreskohen çdo herë që hap aplikacionin. Burimi: CoinGecko")
