import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

st.set_page_config(page_title="Krypto Dashboard - CoinGecko", layout="wide")
st.title("📈 Krypto Dashboard me CoinGecko API")

# CoinGecko IDs për monedhat
coins = {
    "Bitcoin (BTC)": "bitcoin",
    "Pepe (PEPE)": "pepecoin",
    "Verge (XVG)": "verge"
}

def get_coin_gecko_data(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "hourly"
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = data.get("prices", [])
    if not prices:
        return pd.DataFrame()
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["close"] = df["price"]
    df.drop(columns=["price"], inplace=True)
    return df

def add_indicators(df):
    df['RSI'] = RSIIndicator(df['close'], window=14).rsi()
    macd = MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    return df

def get_signal(row):
    if row['RSI'] < 30 and row['MACD'] > row['MACD_signal']:
        return "🟢 BUY"
    elif row['RSI'] > 70 and row['MACD'] < row['MACD_signal']:
        return "🔴 SELL"
    else:
        return "🟡 HOLD"

cols = st.columns(len(coins))

for i, (name, coin_id) in enumerate(coins.items()):
    with cols[i]:
        df = get_coin_gecko_data(coin_id)
        if df.empty:
            st.error(f"Nuk u morën të dhëna për {name}")
            continue
        df = add_indicators(df)
        latest = df.iloc[-1]
        signal = get_signal(latest)
        st.subheader(name)
        st.metric("Çmimi aktual", f"${latest['close']:.6f}")
        st.write(f"RSI: {latest['RSI']:.2f}")
        st.write(f"MACD: {latest['MACD']:.4f}, Signal: {latest['MACD_signal']:.4f}")
        st.markdown(f"### {signal}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Çmimi'))
        fig.update_layout(height=400, xaxis_title="Koha", yaxis_title="Çmimi (USD)")
        st.plotly_chart(fig, use_container_width=True)
