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

# Marrja e çmimeve momentale
@st.cache_data(ttl=300)
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

# Marrja e të dhënave historike për mini-grafikë
@st.cache_data(ttl=900)
def fetch_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '7',
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    prices = response.json().get("prices", [])
    df = pd.DataFrame(prices, columns=["Timestamp", "Price"])
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms").dt.date
    df.set_index("Date", inplace=True)
    return df[["Price"]]

# Funksioni për ngjyrosjen e ndryshimeve
def highlight_changes(val):
    if isinstance(val, str) and "%" in val:
        try:
            num = float(val.replace("%", "").split()[0])
            color = 'lightgreen' if num > 0 else 'salmon'
            return f'background-color: {color}'
        except:
            return ''
    return ''

# Funksioni për shfaqjen e të dhënave me sinjal & mini-grafik
def display_data(data):
    for symbol, coingecko_id in coins.items():
        coin_data = data.get(coingecko_id)
        if coin_data:
            price = coin_data.get("usd")
            change = coin_data.get("usd_24h_change")
            emoji = "🟢" if change and change > 0 else "🔴"

            if change is not None:
                if change > 5:
                    signal = "SHIT (fitim)"
                elif change < -5:
                    signal = "BLIJ (zbritje)"
                else:
                    signal = "MBAJ"
            else:
                signal = "?"

            comment = f"{emoji} {'📈 Rritje' if change and change > 0 else '📉 Rënie'} • 💡 {signal}"

            # Shfaqja në kolonë me mini grafik
            with st.expander(f"{symbol} - ${round(price, 6)} • {round(change, 2)}%"):
                st.write(comment)
                hist = fetch_price_history(coingecko_id)
                if hist is not None:
                    st.line_chart(hist)
                else:
                    st.write("⚠️ Nuk ka të dhëna për grafikun.")

# Rifreskimi automatik çdo 15 sekonda
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()
if time.time() - st.session_state.last_run > 15:
    st.session_state.last_run = time.time()
    st.rerun()

# Marrja dhe shfaqja e të dhënave
data = fetch_prices()
if data:
    display_data(data)
else:
    st.warning("⚠️ Të dhënat nuk janë të disponueshme tani.")

st.caption("📡 Marrë nga CoinGecko • Rifreskim automatik çdo 15 sekonda")
