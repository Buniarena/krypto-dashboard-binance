import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
REFRESH_INTERVAL = 180
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

coins = {
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

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

def calculate_rsi(prices, period=14):
    if prices is None or len(prices) < period + 1:
        return pd.Series([None] * len(prices), index=prices.index if hasattr(prices, "index") else None)
    delta = prices.diff().fillna(0)
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    initial_gain = gain.iloc[:period].mean()
    initial_loss = loss.iloc[:period].mean()
    avg_gain = pd.Series(index=prices.index, dtype=float)
    avg_loss = pd.Series(index=prices.index, dtype=float)
    avg_gain.iloc[period-1] = initial_gain
    avg_loss.iloc[period-1] = initial_loss
    for i in range(period, len(prices)):
        gain_i = gain.iloc[i]
        loss_i = loss.iloc[i]
        prev_gain = avg_gain.iloc[i-1]
        prev_loss = avg_loss.iloc[i-1]
        avg_gain.iloc[i] = (prev_gain * (period - 1) + gain_i) / period
        avg_loss.iloc[i] = (prev_loss * (period - 1) + loss_i) / period
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi[:period-1] = None
    return rsi

st.image(HEADER_IMAGE_URL, width="stretch")
st.title("Monedhat Kripto dhe RSI me Sinjal Ngjyre")

selected_coin = st.selectbox("Zgjidh monedhën", list(coins.keys()))
coin_id = coins[selected_coin]

current_data = get_current_data(coin_id)
if current_data is None:
    st.error("Nuk u mund të merren të dhënat për monedhën e zgjedhur.")
elif "error" in current_data:
    st.error(f"Gabim API: {current_data['error']}")
else:
    st.metric(label=f"Çmimi aktual i {selected_coin}", value=f"${current_data['current_price']:.6f}")

historical_prices = get_historical_prices(coin_id)
if historical_prices.empty:
    st.warning("Nuk u gjetën çmime historike.")
else:
    historical_prices = historical_prices.sort_values("timestamp")
    historical_prices["rsi"] = calculate_rsi(historical_prices["price"])

    # Gjenero sinjal bazuar në RSI
    def signal_from_rsi(rsi):
        if rsi is None:
            return 0
        elif rsi < 35:
            return 1   # blej
        elif rsi > 65:
            return -1  # shit
        else:
            return 0   # neutral

    historical_prices["signal"] = historical_prices["rsi"].apply(signal_from_rsi)

    # Hapësira kohore në format legjibil më të mirë
    historical_prices['timestamp'] = pd.to_datetime(historical_prices['timestamp'], unit='ms')

    # Ngjyrat sipas sinjalit
    color_map = {1: 'green', -1: 'red', 0: 'yellow'}
    colors = historical_prices["signal"].map(color_map)

    # Krijo grafik me plotly
    fig = go.Figure()

    # Linja e çmimeve
    fig.add_trace(go.Scatter(
        x=historical_prices['timestamp'],
        y=historical_prices['price'],
        mode='lines',
        name='Çmimi'
    ))

    # Pikët e sinjaleve me ngjyra
    fig.add_trace(go.Scatter(
        x=historical_prices['timestamp'],
        y=historical_prices['price'],
        mode='markers',
        name='Sinjali',
        marker=dict(color=colors, size=10)
    ))

    fig.update_layout(title=f'Çmimi dhe Sinjalet RSI për {selected_coin}',
                      xaxis_title='Data',
                      yaxis_title='Çmimi (USD)',
                      legend_title='Seritë')

    st.plotly_chart(fig, use_container_width=True)