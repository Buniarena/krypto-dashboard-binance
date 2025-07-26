import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Konfigurimi i faqes
st.set_page_config(page_title="RSI & MACD Numrat", layout="centered")
st.title("📊 Numrat RSI dhe MACD për Coin-et")

# Coinet dhe ID-të e tyre në CoinGecko
coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepecoin-community",
    "Doge": "dogecoin",
    "Shiba": "shiba",
    "Bonk": "bonk",
}

# Marrja e çmimeve aktuale
@st.cache_data(ttl=300)
def fetch_prices():
    ids = ",".join(coins.values())
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': ids, 'vs_currencies': 'usd'}
    res = requests.get(url, params=params)
    return res.json()

# Marrja e të dhënave historike për llogaritje
def fetch_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': 7, 'interval': 'hourly'}
    res = requests.get(url, params=params)
    data = res.json().get("prices", [])
    df = pd.DataFrame(data, columns=["time", "price"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return df

# Llogaritja e RSI dhe MACD
def calculate_indicators(df):
    if len(df) < 50:
        return None, None
    rsi = RSIIndicator(df["price"]).rsi().iloc[-1]
    macd = MACD(df["price"]).macd_diff().iloc[-1]
    return round(rsi, 2), round(macd, 6)

# Marrja e çmimeve
prices = fetch_prices()

# Për çdo coin llogarit dhe shfaq
for name, cid in coins.items():
    df = fetch_history(cid)
    rsi, macd = calculate_indicators(df)
    price = prices.get(cid, {}).get("usd", "N/A")

    st.subheader(f"💰 {name}")
    st.write(f"Çmimi: ${price}")
    st.write(f"RSI: `{rsi}`")   # thjesht numër
    st.write(f"MACD: `{macd}`") # thjesht numër
    st.markdown("---")
