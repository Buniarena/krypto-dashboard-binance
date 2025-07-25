import streamlit as st
import requests

st.title("📈 Çmimet Live të Kriptomonedhave")

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

for name, coin_id in coins.items():
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if coin_id in data:
            price = data[coin_id]["usd"]
            st.metric(label=f"{name}", value=f"${price}")
        else:
            st.warning(f"Nuk u morën të dhëna për {name}.")
    except Exception as e:
        st.warning(f"Gabim te {name}: {e}")
