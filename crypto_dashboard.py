import streamlit as st import requests import pandas as pd

Konfigurimi i faqes

st.set_page_config(page_title="Crypto Dashboard", layout="wide") st.title("📊 Crypto Dashboard - BTC, ETH, XRP dhe më shumë")

Lista e monedhave

coins = { "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "BONK": "bonk", "WIN": "wink", "VET": "vechain", "BTT": "bittorrent-2", "XVG": "verge", "FLOKI": "floki" }

Funksion për marrjen e çmimeve nga CoinGecko

@st.cache_data(ttl=300)  # ruaj të dhënat për 5 minuta def fetch_prices(): try: ids = ",".join(coins.values()) url = f"https://api.coingecko.com/api/v3/simple/price" params = { "ids": ids, "vs_currencies": "usd", "include_24hr_change": "true" } res = requests.get(url, params=params) res.raise_for_status() return res.json() except requests.RequestException as e: st.error(f"Gabim gjatë marrjes së të dhënave: {e}") return {}

Shfaqja e të dhënave

data = fetch_prices() if data: rows = [] for symbol, coin_id in coins.items(): if coin_id in data: price = data[coin_id].get("usd", "N/A") change = data[coin_id].get("usd_24h_change", 0) rows.append({ "Monedha": symbol, "Çmimi ($)": price, "Ndryshim 24h (%)": round(change, 2) })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)

Opsion për rifreskim manual

if st.button("🔁 Rifresko të dhënat"): st.cache_data.clear() st.experimental_rerun()

st.caption("Burimi: CoinGecko • Rifreskim automatik çdo 5 minuta ose manual me buton")

