import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go
import ta

st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📊 Krypto Dashboard – BTC, DOGE, XRP")

coins = {
    "Bitcoin": "bitcoin",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

def fetch_market_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=minute"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    else:
        return None

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

for name, coin_id in coins.items():
    st.header(f"{name.upper()}")

    df = fetch_market_data(coin_id)
    
    if df is not None and not df.empty:
        df = calculate_rsi(df)
        latest_price = df["price"].iloc[-1]
        price_1m_ago = df["price"].iloc[-2] if len(df) > 2 else latest_price
        price_1h_ago = df["price"].iloc[-60] if len(df) > 60 else latest_price
        price_1d_ago = df["price"].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Çmimi aktual", f"${latest_price:,.4f}")
        col2.metric("⏱ 1 Minutë", f"${price_1m_ago:,.4f}", f"{latest_price - price_1m_ago:+.4f}")
        col3.metric("🕐 1 Orë", f"${price_1h_ago:,.4f}", f"{latest_price - price_1h_ago:+.4f}")
        col4.metric("📆 1 Ditë", f"${price_1d_ago:,.4f}", f"{latest_price - price_1d_ago:+.4f}")

        # RSI + sinjal
        latest_rsi = df["rsi"].iloc[-1]
        st.write(f"**RSI:** {latest_rsi:.2f} → **{signal_from_rsi(latest_rsi)}**")

        # Grafik
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi"))
        fig.update_layout(title=f"Ecuria e çmimit – {name}", xaxis_title="Koha", yaxis_title="Çmimi ($)")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
    else:
        st.error(f"Nuk u morën të dhëna për {name}.")
