import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go
import ta
from datetime import datetime, timedelta

st.set_page_config(page_title="📉 Krypto 2 Orë", layout="wide")
st.title("⏱️ Krypto: Çmimi për 2 orët e fundit")

# Coin-et që do të shfaqim
coins = {
    "Bitcoin": "bitcoin",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

# Funksioni për të marrë të dhëna historike nga CoinGecko
def fetch_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minutely"}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        # Filtro vetëm të dhënat për 2 orët e fundit
        now = datetime.utcnow()
        two_hours_ago = now - timedelta(hours=2)
        df = df[df.index >= two_hours_ago]
        return df
    else:
        return None

# RSI & sinjal
def calculate_rsi(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['price'], window=14).rsi()
    return df

def signal_from_rsi(rsi):
    if rsi < 30:
        return "📈 BLI"
    elif rsi > 70:
        return "📉 SHIT"
    else:
        return "⏳ PRIT"

# Dashboard për çdo coin
for name, coin_id in coins.items():
    st.subheader(f"{name} ({coin_id.upper()})")
    df = fetch_data(coin_id)

    if df is not None and not df.empty:
        df = calculate_rsi(df)
        latest_price = df["price"].iloc[-1]
        start_price = df["price"].iloc[0]
        change = latest_price - start_price
        percent = (change / start_price) * 100

        col1, col2 = st.columns(2)
        col1.metric("💰 Çmimi aktual", f"${latest_price:,.4f}")
        col2.metric("⏱️ 2 Orët e fundit", f"{change:+.4f} $", f"{percent:+.2f}%")

        latest_rsi = df["rsi"].iloc[-1]
        st.markdown(f"**RSI:** `{latest_rsi:.2f}` → **{signal_from_rsi(latest_rsi)}**")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi"))
        fig.update_layout(title="Grafik i Çmimit për 2 orë", xaxis_title="Ora", yaxis_title="Çmimi ($)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
    else:
        st.error(f"Nuk u morën të dhëna për {name}. Kontrollo lidhjen.")
