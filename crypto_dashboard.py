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

st.title("📊 Çmimi Aktual për Coinet (CoinGecko me Cache)")

@st.cache_data(ttl=600)  # ruaj për 10 minuta për të shmangur limitet
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
except Exception as e:
    st.error(f"Gabim API: {e}")
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
