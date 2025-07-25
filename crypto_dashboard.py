import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Vendos titullin
st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📈 Krypto Dashboard – BTC, PEPE, XVG")

# Funksioni për të marrë të dhënat nga Binance
def get_binance_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    end_time = int(datetime.datetime.now().timestamp() * 1000)
    start_time = end_time - 1000 * 60 * 60 * 24 * 30  # 30 ditë më parë
    params = {
        "symbol": symbol,
        "interval": "1h",
        "startTime": start_time,
        "endTime": end_time,
        "limit": 500
    }
    response = requests.get(url, params=params)
    data = response.json()
    if not data or not isinstance(data, list):
        return pd.DataFrame()
    df = pd.DataFrame(data, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

# Shto indikatorët RSI dhe MACD
def add_indicators(df):
    df['RSI'] = RSIIndicator(close=df['close'], window=14).rsi()
    macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    return df

# Gjenero sinjal blerje/shitje
def get_signal(df):
    if df['RSI'] < 30 and df['MACD'] > df['MACD_signal']:
        return "🟢 BUY"
    elif df['RSI'] > 70 and df['MACD'] < df['MACD_signal']:
        return "🔴 SELL"
    else:
        return "🟡 HOLD"

# Grafikët
def plot_chart(df, coin_name):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlestick'
    ))
    fig.update_layout(title=f"{coin_name} Chart", xaxis_title='Time', yaxis_title='Price')
    st.plotly_chart(fig, use_container_width=True)

# Lista e monedhave
symbols = {
    "Bitcoin (BTC)": "BTCUSDT",
    "Pepe (PEPE)": "PEPEUSDT",
    "Verge (XVG)": "XVGUSDT"
}

cols = st.columns(len(symbols))

# Shfaq për secilën monedhë
for i, (name, symbol) in enumerate(symbols.items()):
    with cols[i]:
        df = get_binance_data(symbol)

        if df.empty:
            st.error(f"Nuk u morën të dhëna për {name}.")
            continue

        df = add_indicators(df)
        latest = df.iloc[-1]
        signal = get_signal(latest)

        st.subheader(f"{name}")
        st.metric("Aktueller Preis", f"{latest['close']:.6f}")
        st.write(f"**RSI:** {latest['RSI']:.2f}")
        st.write(f"**MACD:** {latest['MACD']:.2f}, Signal: {latest['MACD_signal']:.2f}")
        st.markdown(f"### {signal}")
        plot_chart(df, name)
