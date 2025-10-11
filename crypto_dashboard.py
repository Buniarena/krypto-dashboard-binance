import streamlit as st
import requests
import pandas as pd
import time
from ta.momentum import RSIIndicator

# 🔔 Zile audio
AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"

# Konfigurime
REFRESH_INTERVAL = 180  # sekonda (3 min)
REQUEST_DELAY = 1.5
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

# Lista e monedhave
coins = {
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

# Merr të dhëna aktuale
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 429:
            return {"error": "429"}
        response.raise_for_status()
        return response.json()[0]
    except Exception:
        return None

# Merr çmimet historike
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "60", "interval": "daily"}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 429:
            return pd.DataFrame()
        response.raise_for_status()
        prices = response.json().get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["price"] = df["price"].astype(float)
        return df
    except Exception:
        return pd.DataFrame()

# Llogarit RSI
def calculate_rsi(df):
    if df.empty or len(df) <
