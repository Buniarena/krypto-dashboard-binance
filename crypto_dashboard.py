import streamlit as st
import requests
import pandas as pd

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk"
}

st.title("📊 Çmimi Aktual për Coinet")

@st.cache_data(ttl=600)  # ruan përgjigjen për 10 minuta
def get_prices(coin_ids):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

try:
    data = get_prices(list(coins.values()))
except requests.exceptions.HTTPError as err:
    st.error(f"Gabim API: {err}")
    data = {}

rows = []
for name, coin_id in coins.items():
    price = data.get(coin_id, {}).get("usd", None)
    if price is not None:
        rows.append({"Coin": name, "Çmimi aktual (USD)": f"${price}"})
    else:
        rows.append({"Coin": name, "Çmimi aktual (USD)": "Nuk u morën të dhënat"})

df = pd.DataFrame(rows)
st.table(df)
st.caption("🔄 Të dhënat rifreskohen çdo 10 minuta. Burimi: CoinGecko")
