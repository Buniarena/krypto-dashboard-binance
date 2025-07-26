import streamlit as st
import requests

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk"
}

st.title("📊 Çmimi Aktual për Coinet")

def get_current_price(coin_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        price = data.get(coin_id, {}).get("usd", None)
        return price
    except:
        return None

for name, coin_id in coins.items():
    st.markdown(f"### {name}")
    price = get_current_price(coin_id)
    if price is not None:
        st.write(f"💰 **Çmimi aktual:** ${price}")
    else:
        st.warning("⚠️ Nuk u morën të dhënat. CoinGecko mund të jetë offline ose ka problem lidhjeje.")

st.caption("🔄 Të dhënat rifreskohen çdo herë që hap aplikacionin. Burimi: CoinGecko")
