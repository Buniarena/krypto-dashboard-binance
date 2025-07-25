import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Titulli
st.set_page_config(layout="wide")
st.title("📊 Krypto Dashboard - Binance Live Signals")

# Lista e simboleve që do të analizohen
symbols = {
    "Bitcoin (BTC)": "BTCUSDT",
    "Pepe (PEPE)": "PEPEUSDT",
    "Verge (XVG)": "XVGUSDT"
}

# Funksion për të marrë të dhëna historike nga Binance
def get_binance_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1h",  # më i qëndrueshëm se 15m
        "limit": 200
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if not data or not isinstance(data, list) or 'code' in data:
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
    except Exception as e:
        st.error(f"Gabim gjatë marrjes së të dhënave për {symbol}: {e}")
        return pd.DataFrame()

# Funksion për të llogaritur indikatorët teknikë dhe sinjalet
def calculate_signals(df):
    if df.empty or len(df) < 50:
        return None

    close = df['close']

    # RSI
    rsi = RSIIndicator(close=close, window=14).rsi()
    df['RSI'] = rsi

    # MACD
    macd = MACD(close=close)
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()

    # Gjenerimi i sinjalit
    latest = df.iloc[-1]
    signal = "❓ Neutral"

    if latest['RSI'] < 30 and latest['MACD'] > latest['Signal']:
        signal = "🟢 Buy"
    elif latest['RSI'] > 70 and latest['MACD'] < latest['Signal']:
        signal = "🔴 Sell"

    return signal, df

# Loop nëpër simbolet
for name, symbol in symbols.items():
    st.subheader(name)

    df = get_binance_data(symbol)
    if df.empty:
        st.warning(f"Nuk u morën të dhëna për {name}.")
        continue

    result = calculate_signals(df)
    if not result:
        st.warning(f"Të dhënat për {name} janë të pamjaftueshme.")
        continue

    signal, df = result
    st.write(f"**Sinjali aktual:** {signal}")

    # Grafik interaktiv
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Çmimi"
    ))
    fig.update_layout(height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
