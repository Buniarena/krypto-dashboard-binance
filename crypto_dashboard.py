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

st.title("📊 Çmimi Aktual për Coinet (Tabela)")

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

data = []
for name, coin_id in coins.items():
    price = get_current_price(coin_id)
    if price is not None:
        data.append({"Coin": name, "Çmimi aktual (USD)": f"${price}"})
    else:
        data.append({"Coin": name, "Çmimi aktual (USD)": "Nuk u morën të dhënat"})

df = pd.DataFrame(data)

st.table(df)

st.caption("🔄 Të dhënat rifreskohen çdo herë që hap aplikacionin. Burimi: CoinGecko")
