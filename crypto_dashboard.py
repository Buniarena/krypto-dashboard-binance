import streamlit as st import requests import pandas as pd import time import ta

Lista e coin-ave me ID nga CoinGecko

coins = { "BTC 🟠": "bitcoin", "XVG 🧿": "verge", "FLOKI 🐶": "floki", "PEPE 🐸": "pepecoin-community", "VET 🔗": "vechain", "BONK 🦴": "bonk", "DOGE 🐕": "dogecoin", "SHIB 🦊": "shiba", "WIN 🎯": "wink", "BTT 📡": "bittorrent-2" }

st.set_page_config(page_title="📊 Live Crypto Dashboard", layout="wide") st.title("📈 Live Crypto Dashboard (CoinGecko)")

@st.cache_data(ttl=300) def fetch_prices(): ids = ','.join(coins.values()) url = "https://api.coingecko.com/api/v3/simple/price" params = { 'ids': ids, 'vs_currencies': 'usd', 'include_24hr_change': 'true' } response = requests.get(url, params=params) if response.status_code != 200: st.error("❌ Gabim gjatë marrjes së të dhënave") return {} return response.json()

@st.cache_data(ttl=900) def fetch_price_history(coin_id): url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart" params = { 'vs_currency': 'usd', 'days': '30', 'interval': 'daily' } response = requests.get(url, params=params) if response.status_code != 200: return None prices = response.json().get("prices", []) df = pd.DataFrame(prices, columns=["Timestamp", "Price"]) df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms") df.set_index("Date", inplace=True) df = df.drop(columns=["Timestamp"]) return df

def calculate_indicators(df): df = df.copy() df['MA7'] = df['Price'].rolling(window=7).mean() df['RSI'] = ta.momentum.RSIIndicator(df['Price'], window=14).rsi() return df

def display_data(data): for symbol, coingecko_id in coins.items(): coin_data = data.get(coingecko_id) if coin_data: price = coin_data.get("usd") change = coin_data.get("usd_24h_change") emoji = "🟢" if change and change > 0 else "🔴"

if change is not None:
            if change > 5:
                signal = "SHIT (fitim)"
            elif change < -5:
                signal = "BLIJ (zbritje)"
            else:
                signal = "MBAJ"
        else:
            signal = "?"

        comment = f"{emoji} {'📈 Rritje' if change and change > 0 else '📉 Rënie'} • 💡 {signal}"

        with st.expander(f"{symbol} - ${round(price, 6)} • {round(change, 2)}%"):
            st.write(comment)
            hist = fetch_price_history(coingecko_id)
            if hist is not None:
                hist = calculate_indicators(hist)
                st.line_chart(hist[["Price", "MA7"]])
                st.line_chart(hist[["RSI"]])
            else:
                st.write("⚠️ Nuk ka të dhëna për grafikun.")

if 'last_run' not in st.session_state: st.session_state.last_run = time.time() if time.time() - st.session_state.last_run > 15: st.session_state.last_run = time.time() st.rerun()

data = fetch_prices() if data: display_data(data) else: st.warning("⚠️ Të dhënat nuk janë të disponueshme tani.")

st.caption("📡 Marrë nga CoinGecko • Rifreskim automatik çdo 15 sekonda")

