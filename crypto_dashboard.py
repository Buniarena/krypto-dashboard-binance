import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk",
    "XVG (Verge)": "verge"
}

st.title("📊 Çmimi Aktual dhe RSI për Coinet")

@st.cache_data(ttl=3600)  # cache për 1 orë
def get_prices(coin_ids):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=3600)
def get_hourly_prices_1day(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "1",
        "interval": "hourly"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    prices = response.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["price"] = df["price"].astype(float)
    return df

def get_signal(rsi):
    if isinstance(rsi, float):
        if rsi < 30:
            return "🟢 Bli"
        elif rsi > 70:
            return "🔴 Shit"
        else:
            return "🟡 Mbaj"
    else:
        return "❓ N/A"

if st.button("🔄 Rifresko të dhënat"):
    st.cache_data.clear()  # fshin cache për të detyruar kërkesë të re

try:
    current_prices = get_prices(list(coins.values()))
except requests.exceptions.RequestException as e:
    st.error(f"Gabim API: {e}")
    current_prices = {}

rows = []
for name, coin_id in coins.items():
    price = current_prices.get(coin_id, {}).get("usd")

    # Llogaritim RSI vetëm për Bitcoin për të shmangur kërkesa të shumta
    if coin_id == "bitcoin" and price is not None:
        try:
            hist_df = get_hourly_prices_1day(coin_id)
            rsi = RSIIndicator(close=hist_df["price"]).rsi().iloc[-1]
            rsi_value = round(rsi, 2)
        except Exception:
            rsi_value = "Nuk u llogarit"
    else:
        rsi_value = "N/A"

    signal = get_signal(rsi_value if isinstance(rsi_value, float) else None)

    if price is not None:
        rows.append({
            "Coin": name,
            "Çmimi aktual (USD)": f"${price}",
            "RSI (1 orë, 1 ditë)": rsi_value,
            "Sinjali": signal
        })
    else:
        rows.append({
            "Coin": name,
            "Çmimi aktual (USD)": "Nuk u morën të dhënat",
            "RSI (1 orë, 1 ditë)": rsi_value,
            "Sinjali": signal
        })

df = pd.DataFrame(rows)
st.table(df)
st.caption("🔄 Kliko 'Rifresko të dhënat' për të marrë të dhëna të reja nga CoinGecko.")
