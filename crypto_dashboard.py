import streamlit as st
import requests
import pandas as pd
import time

# Lista e coin-ave me ID nga CoinGecko
coins = {
    "BTC": "bitcoin",
    "XVG": "verge",
    "FLOKI": "floki",
    "PEPE": "pepecoin-community",
    "VET": "vechain",
    "BONK": "bonk",
    "DOGE": "dogecoin",
    "SHIB": "shiba",
    "WIN": "wink",
    "BTT": "bittorrent-2"
}

# Konfigurimi i faqes
st.set_page_config(page_title="Live Crypto Dashboard", layout="wide")
st.title("📊 Live Crypto Dashboard (CoinGecko)")

# Funksioni për marrjen e çmimeve
@st.cache_data(ttl=300)  # cache për 5 minuta
def fetch_prices():
    ids = ','.join(coins.values())
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ids,
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error("❌ Gabim gjatë marrjes së të dhënave")
        return {}
    return response.json()

# Funksioni për shfaqjen e të dhënave
def display_data(data):
    rows = []
    for symbol, coingecko_id in coins.items():
        coin_data = data.get(coingecko_id)
        if coin_data:
            price = coin_data.get("usd")
            change = coin_data.get("usd_24h_change")
            rows.append({
                "Symbol": symbol,
                "Price ($)": round(price, 6),
                "24h Change (%)": round(change, 2)
            })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

# Rifreskimi çdo 15 sekonda
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()

if time.time() - st.session_state.last_run > 15:
    st.session_state.last_run = time.time()
    st.rerun()

data = fetch_prices()
display_data(data)

st.caption("💡 Të dhënat përditësohen automatikisht çdo 15 sekonda • Burimi: CoinGecko")
