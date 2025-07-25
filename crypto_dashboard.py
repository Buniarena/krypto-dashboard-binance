import streamlit as st
import requests

st.title("Çmimet Live të Kriptove")

coins = {
    "Bitcoin": "bitcoin",
    "Dogecoin": "dogecoin",
    "XRP": "ripple",
    "Pepe": "pepe"
}

for name, coin_id in coins.items():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get(coin_id, {}).get("usd")
        if price is not None:
            st.metric(label=name, value=f"${price:,}")
        else:
            st.warning(f"Nuk u morën të dhëna për {name}.")
    except Exception as e:
        st.error(f"Gabim për {name}: {e}")
