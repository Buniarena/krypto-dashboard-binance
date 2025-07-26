import streamlit as st
import requests
import pandas as pd
import time

# Lista e coin-ave me ID nga CoinGecko
coins = {
    "BTC 🟠": "bitcoin",
    "XVG 🧿": "verge",
    "FLOKI 🐶": "floki",
    "PEPE 🐸": "pepecoin-community",
    "VET 🔗": "vechain",
    "BONK 🦴": "bonk",
    "DOGE 🐕": "dogecoin",
    "SHIB 🦊": "shiba",
    "WIN 🎯": "wink",
    "BTT 📡": "bittorrent-2"
}

# Konfigurimi i faqes
st.set_page_config(page_title="📊 Live Crypto Dashboard", layout="wide")
st.title("📈 Live Crypto Dashboard (CoinGecko)")

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

# Funksioni për marrjen e të dhënave historike për një coin të vetëm
@st.cache_data(ttl=300)
def fetch_coin_details(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '7',
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    return response.json()

# Funksioni për ngjyrosjen e ndryshimeve
def highlight_changes(val):
    if isinstance(val, str) and "%" in val:
        try:
            number = float(val.replace('% 🔴','').replace('% 🟢','').strip())
            color = 'lightgreen' if number > 0 else 'salmon'
            return f'background-color: {color}'
        except:
            return ''
    return ''

# Shfaqja e tabelës
def display_data(data):
    rows = []
    for symbol, coingecko_id in coins.items():
        coin_data = data.get(coingecko_id)
        if coin_data:
            price = coin_data.get("usd")
            change = coin_data.get("usd_24h_change")
            emoji = "🟢" if change and change > 0 else "🔴"
            comment = "📈 Rritje" if change and change > 0 else "📉 Rënie"
            rows.append({
                "Symbol": symbol,
                "Price ($)": round(price, 6),
                "24h Change (%)": f"{round(change, 2)}% {emoji}",
                "Comment": comment
            })
    df = pd.DataFrame(rows)
    st.dataframe(df.style.applymap(highlight_changes, subset=["24h Change (%)"]), use_container_width=True)

# Rifreskimi çdo 15 sekonda
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()

if time.time() - st.session_state.last_run > 15:
    st.session_state.last_run = time.time()
    st.rerun()

# Marrja e çmimeve
data = fetch_prices()

if data:
    display_data(data)
    st.divider()

    # Përzgjedhja e një coini për detaje
    coin_name = st.selectbox("🔍 Zgjidh një kriptomonedhë për më shumë detaje", list(coins.keys()))
    coin_id = coins[coin_name]
    coin_detail = fetch_coin_details(coin
