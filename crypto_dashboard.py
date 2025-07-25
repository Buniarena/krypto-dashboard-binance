import streamlit as st
import requests

# Titulli i aplikacionit
st.title("📈 Çmimet Live të Kriptomonedhave")

# Lista e kriptove me ID-të e CoinGecko
coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

# Merr të dhënat për çdo kriptomonedhë
for name, coin_id in coins.items():
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        price = data[coin_id]["usd"]
        st.metric(label=f"{name}", value=f"${price}")
    except Exception as e:
        st.warning(f"Nuk u morën të dhëna për {name}.")
