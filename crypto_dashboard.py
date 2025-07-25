import streamlit as st
import requests

st.title("Çmimet Live nga CoinGecko")

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
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
            st.write(f"{name}: ${price}")
        else:
            st.write(f"Nuk u morën të dhëna për {name}.")
    except Exception as e:
        st.write(f"Gabim për {name}: {e}")
