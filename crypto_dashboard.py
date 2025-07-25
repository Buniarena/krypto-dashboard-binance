import streamlit as st
import requests

# Lista e kriptove dhe ID-të e tyre në CoinGecko
coins = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Dogecoin (DOGE)": "dogecoin",
    "XRP (XRP)": "ripple",
    "Pepe (PEPE)": "pepe",
    "Verge (XVG)": "verge"
}

st.set_page_config(page_title="Krypto Live Monitor", layout="wide")
st.title("🚀 Krypto Monitor Real-Time")

# Funksion për të marrë të dhënat nga CoinGecko
def get_market_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": coin_id,
        "price_change_percentage": "1h,24h"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()[0]
    else:
        return None

# Loop për secilën kriptomonedhë
for name, cg_id in coins.items():
    data = get_market_data(cg_id)

    if data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label=f"💰 {name}", value=f"${data['current_price']:.4f}")
        with col2:
            st.metric(label="⏱ 1 Minutë", value="—", delta="—")  # S’ofrohet nga CoinGecko
        with col3:
            delta_1h = data.get("price_change_percentage_1h_in_currency")
            if delta_1h:
                st.metric(label="🕐 1 Orë", value=f"{delta_1h:.2f}%", delta=f"{delta_1h:.2f}%")
            else:
                st.metric(label="🕐 1 Orë", value="—
