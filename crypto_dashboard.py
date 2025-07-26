import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Coinet që do të shfaqim me CoinGecko ID
coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk"
}

# Funksion për të marrë të dhënat historike të çmimit nga CoinGecko
@st.cache_data(ttl=3600)
def get_price_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "hourly"}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None
    data = r.json()
    prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
    return prices

# Funksion për të llogaritur RSI dhe MACD
def calculate_indicators(prices):
    prices = prices.copy()
    prices["rsi"] = RSIIndicator(close=prices["price"], window=14).rsi()
    macd = MACD(close=prices["price"])
    prices["macd_diff"] = macd.macd_diff()
    return prices

# Funksion për të vendosur sinjalin
def get_signal(rsi, macd_diff):
    if rsi < 30 and macd_diff > 0:
        return "BLI"
    elif rsi > 70 and macd_diff < 0:
        return "SHIT"
    else:
        return "MBAJ"

# Ngjyra për sinjal
def signal_color(signal):
    if signal == "BLI":
        return "green"
    elif signal == "SHIT":
        return "red"
    else:
        return "orange"

# Interfejsi në Streamlit
st.set_page_config(page_title="📈 Krypto Dashboard", layout="centered")
st.title("📊 RSI dhe Çmimi për Coinet")

for name, coin_id in coins.items():
    prices = get_price_data(coin_id)

    if prices is None or prices.empty:
        st.markdown(f"### {name}\n❌ Nuk u morën të dhënat. CoinGecko mund të jetë offline.")
        continue

    indicators = calculate_indicators(prices.dropna())
    last = indicators.iloc[-1]
    price = round(last["price"], 6)
    rsi = round(last["rsi"], 2)
    macd = round(last["macd_diff"], 4)
    signal = get_signal(rsi, macd)

    st.markdown(f"""
    <div style="padding: 10px; border: 1px solid #ccc; border-radius: 10px; margin-bottom: 15px;">
        <h3>{name}</h3>
        💰 <b>Çmimi:</b> ${price}  
        <br>📈 <b>RSI:</b> {rsi}  
        <br>📉 <b>MACD diff:</b> {macd}  
        <br>🚨 <b>Sinjal:</b> <span style='color:{signal_color(signal)}'><b>{signal}</b></span>
    </div>
    """, unsafe_allow_html=True)

st.info("🔄 Të dhënat rifreskohen çdo herë që hap aplikacionin. Burimi: CoinGecko")
