import streamlit as st
import requests
import pandas as pd
import time

# Audio alert URL
AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"

# Settings
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

# Funksion për llogaritjen e RSI-së
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    delta = delta[1:]
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()[:period+1]
    avg_loss = loss.rolling(window=period, min_periods=period).mean()[:period+1]

    avg_gain = avg_gain.append(gain[period+1:])
    avg_loss = avg_loss.append(loss[period+1:])

    for i in range(period + 1, len(prices)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi[:period] = None  # Nuk ka vlera për periudhën fillestare
    return rsi

# Streamlit UI
st.image(HEADER_IMAGE_URL, use_column_width=True)
st.title("Monedhat Kripto dhe RSI")

selected_coin = st.selectbox("Zgjidh monedhën", list(coins.keys()))
coin_id = coins[selected_coin]

current_data = get_current_data(coin_id)
if current_data is None:
    st.error("Nuk u mund të merren të dhënat.")
else:
    st.write(f"Çmimi aktual i {selected_coin}: ${current_data['current_price']:.4f}")

historical_prices = get_historical_prices(coin_id)
if historical_prices.empty:
    st.warning("Nuk u gjetën çmime historike.")
else:
    historical_prices['rsi'] = calculate_rsi(historical_prices['price'])
    st.line_chart(historical_prices.set_index('timestamp')[['price', 'rsi']])