import streamlit as st import requests import pandas as pd import time import ta

Lista e coin-ave me ID nga CoinGecko

coins = { "BTC 🟠": "bitcoin", "XVG 🧿": "verge", "FLOKI 🐶": "floki", "PEPE 🐸": "pepecoin-community", "VET 🔗": "vechain", "BONK 🦴": "bonk", "DOGE 🐕": "dogecoin", "SHIB 🦊": "shiba", "WIN 🎯": "wink", "BTT 📡": "bittorrent-2" }

st.set_page_config(page_title="📊 Live Crypto Dashboard", layout="wide") st.title("📈 Live Crypto Dashboard (CoinGecko)")

@st.cache_data(ttl=300) def fetch_prices(): ids = ','.join(coins.values()) url = "https://api.coingecko.com/api/v3/simple/price" params = { 'ids': ids, 'vs_currencies': 'usd', 'include_24hr_change': 'true' } response = requests.get(url, params=params) if response.status_code != 200: st.error("❌ Gabim gjatë marrjes së të dhënave") return {} return response.json()

@st.cache_data(ttl=900) def fetch_price_history(coin_id): url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart" params = { 'vs_currency': 'usd', 'days': '30', 'interval': 'daily' } response = requests.get(url, params=params) if response.status_code != 200: return None

