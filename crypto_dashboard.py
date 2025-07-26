import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go

# Coin list me emoji dhe CoinGecko ID
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
    try:
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

@st.cache_data(ttl=300)
def fetch_chart_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': '1', 'interval': 'hourly'}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
    except:
        pass
    return pd.DataFrame()

def get_signal(change):
    if change is None:
        return "❓"
    elif change > 5:
        return "🟢 BLIJ"
    elif change < -5:
        return "🔴 SHIT"
    else:
        return "🟡 MBAJ"

def display_dashboard(data):
    for name, coin_id in coins.items():
        coin = data.get(coin_id)
        if not coin:
            continue
        price = coin.get("usd", 0)
        change = coin.get("usd_24h_change", 0)

        signal = get_signal(change)

        st.markdown(f"### {name}")
        col1, col2 = st.columns([2, 5])
        with col1:
            st.metric("Çmimi (USD)", f"${price:.6f}", f"{change:.2f}%")
            st.markdown(f"💬 Koment: **{signal}**")

        with col2:
            df = fetch_chart_data(coin_id)
            if not df.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'], y=df['price'],
                    mode='lines', line=dict(color='deepskyblue')
                ))
                fig.update_layout(
                    height=200,
                    margin=dict(l=10, r=10, t=20, b=20),
                    xaxis_title=None, yaxis_title=None,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Grafiku nuk mund të ngarkohet.")

# Rifreskimi çdo 15 sekonda
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()
if time.time() - st.session_state.last_run > 15:
    st.session_state.last_run = time.time()
    st.rerun()

data = fetch_prices()
if data:
    display_dashboard(data)
else:
    st.error("Nuk mund të marrim të dhënat nga CoinGecko.")

st.caption("⏱️ Rifreskim çdo 15 sekonda • Burimi: CoinGecko")
