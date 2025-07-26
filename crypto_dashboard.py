import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go

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

@st.cache_data(ttl=300)
def fetch_coin_chart(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': '1', 'interval': 'hourly'}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return {}

def get_signal(change):
    if change is None:
        return "❓"
    elif change > 5:
        return "🟢 BLIJ"
    elif change < -5:
        return "🔴 SHIT"
    else:
        return "🟡 MBAJ"

def display_data(data):
    for symbol, coin_id in coins.items():
        coin_data = data.get(coin_id)
        if not coin_data:
            continue

        price = coin_data.get("usd", 0)
        change = coin_data.get("usd_24h_change", 0)
        emoji = "🟢" if change > 0 else "🔴"
        signal = get_signal(change)

        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown(f"### {symbol}")
            st.metric(label="Çmimi", value=f"${price:.6f}", delta=f"{change:.2f}%")
            st.markdown(f"💬 Koment: **{signal}**")

        with col2:
            chart_data = fetch_coin_chart(coin_id)
            if "prices" in chart_data:
                prices = chart_data["prices"]
                times = [pd.to_datetime(p[0], unit='ms') for p in prices]
                values = [p[1] for p in prices]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=times, y=values, mode='lines', line=dict(color='cyan')))
                fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Nuk ka grafik për momentin")

# Rifreskimi automatik
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()
if time.time() - st.session_state.last_run > 15:
    st.session_state.last_run = time.time()
    st.rerun()

data = fetch_prices()
if data:
    display_data(data)
else:
    st.warning("⚠️ Të dhënat nuk janë të disponueshme tani.")

st.caption("📡 Marrë nga CoinGecko • Rifreskim çdo 15 sekonda • Përditësim grafik & sinjal")
