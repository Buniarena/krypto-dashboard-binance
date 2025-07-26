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

# Funksioni për marrjen e detajeve për një coin
@st.cache_data(ttl=300)
def fetch_coin_details(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Ngjyrosja e ndryshimeve
def highlight_changes(val):
    try:
        number = float(str(val).split('%')[0])
        color = 'lightgreen' if number > 0 else 'salmon'
        return f'background-color: {color}'
    except:
        return ''

# Paraqitja e të dhënave
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
                "Coin": symbol,
                "Price ($)": round(price, 6),
                "24h Change": f"{round(change, 2)}% {emoji}",
                "Comment": comment
            })
    df = pd.DataFrame(rows)
    st.dataframe(df.style.applymap(highlight_changes, subset=["24h Change"]), use_container_width=True)

    # Klik për të zgjedhur një coin
    selected = st.selectbox("🔎 Zgjidh një monedhë për të parë detaje:", list(coins.keys()))
    coin_id = coins[selected]
    coin_detail = fetch_coin_details(coin_id)

    if coin_detail:
        st.subheader(f"📘 Detaje për {selected}")
        st.write(f"**Emri i plotë:** {coin_detail.get('name')}")
        st.write(f"**Simboli:** {coin_detail.get('symbol').upper()}")
        st.write(f"**Renditja në treg:** #{coin_detail.get('market_cap_rank')}")
        st.write(f"**Website:** [{coin_detail['links']['homepage'][0]}]({coin_detail['links']['homepage'][0]})")
        st.write("**Përshkrimi:**", coin_detail.get("description", {}).get("en", "")[:400] + "...")


# Rifreskim çdo 15 sekonda
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
