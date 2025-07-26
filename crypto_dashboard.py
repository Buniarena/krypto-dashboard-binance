import streamlit as st import requests import pandas as pd from ta.momentum import RSIIndicator import time

REFRESH_INTERVAL = 180  # 180 sekonda = 3 minuta

if "start_time" not in st.session_state: st.session_state.start_time = time.time() if "last_signal" not in st.session_state: st.session_state.last_signal = {}

def seconds_remaining(): elapsed = time.time() - st.session_state.start_time remaining = REFRESH_INTERVAL - elapsed return max(0, int(remaining))

def refresh_if_needed(): if seconds_remaining() <= 0: st.session_state.start_time = time.time() st.experimental_rerun()

st.markdown("<h3 style='margin-bottom: 0.5em;'>\ud83d\udcca Dashboard: \u00c7mimi, RSI dhe % Ndryshim 24h p\u00ebr Coinet</h3>", unsafe_allow_html=True) countdown_placeholder = st.empty() refresh_if_needed()

coins = { "Bitcoin": "bitcoin", "PEPE": "pepe", "Doge": "dogecoin", "Shiba": "shiba-inu", "Bonk": "bonk", "XVG (Verge)": "verge" }

@st.cache_data(ttl=REFRESH_INTERVAL) def get_prices_and_change(coin_ids): url = "https://api.coingecko.com/api/v3/simple/price" params = { "ids": ",".join(coin_ids), "vs_currencies": "usd", "include_24hr_change": "true" } response = requests.get(url, params=params, timeout=10) response.raise_for_status() return response.json()

@st.cache_data(ttl=REFRESH_INTERVAL) def get_historical_prices(coin_id): url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart" params = { "vs_currency": "usd", "days": "30", "interval": "daily" } response = requests.get(url, params=params, timeout=10) response.raise_for_status() prices = response.json()["prices"] df = pd.DataFrame(prices, columns=["timestamp", "price"]) df["price"] = df["price"].astype(float) return df

def get_signal(rsi): if isinstance(rsi, float): if rsi < 30: return "\ud83d\udfe2 Bli" elif rsi > 70: return "\ud83d\udd34 Shit" else: return "\ud83d\udfe1 Mbaj" else: return "\u2753 N/A"

def signal_color(signal): return { "\ud83d\udfe2 Bli": "green", "\ud83d\udd34 Shit": "red", "\ud83d\udfe1 Mbaj": "orange" }.get(signal, "gray")

def play_alert_sound(signal): if signal == "\ud83d\udfe2 Bli": sound_url = "https://actions.google.com/sounds/v1/alarms/bugle_tune.ogg" elif signal == "\ud83d\udd34 Shit": sound_url = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg" else: return st.components.v1.html(f""" <audio autoplay

