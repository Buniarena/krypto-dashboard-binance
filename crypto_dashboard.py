import streamlit as st import pandas as pd import requests import datetime import plotly.graph_objects as go from ta.momentum import RSIIndicator from ta.trend import MACD

Titulli

def app_title(): st.set_page_config(page_title="Krypto Dashboard", layout="wide") st.title("📈 Krypto Dashboard - BTC, PEPE, XVG")

Merr të dhëna nga Binance

@st.cache_data(ttl=300) def get_binance_data(symbol: str, interval="1h", limit=100): url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}" response = requests.get(url) data = response.json()

df = pd.DataFrame(data, columns=[
    "timestamp", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "number_of_trades",
    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
])

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df["close"] = df["close"].astype(float)
df.set_index("timestamp", inplace=True)
return df[["close"]]

Llogarit RSI dhe MACD

def add_indicators(df): rsi = RSIIndicator(df['close'], window=14) macd = MACD(df['close']) df['RSI'] = rsi.rsi() df['MACD'] = macd.macd() df['MACD_signal'] = macd.macd_signal() return df

Gjenero sinjale blerje/shitje

def get_signal(row): if row['RSI'] < 30 and row['MACD'] > row['MACD_signal']: return "🟢 BUY" elif row['RSI'] > 70 and row['MACD'] < row['MACD_signal']: return "🔴 SELL" else: return "🟡 HOLD"

Vizato grafik me plotly

def plot_chart(df, coin_name): fig = go.Figure() fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Close')) fig.update_layout(title=f"{coin_name} Price", xaxis_title="Date", yaxis_title="Price", height=400) st.plotly_chart(fig, use_container_width=True)

Dashboardi kryesor

app_title()

symbols = { "BTC/USDT": "BTCUSDT", "PEPE/USDT": "PEPEUSDT", "XVG/USDT": "XVGUSDT" }

cols = st.columns(3)

for i, (name, symbol) in enumerate(symbols.items()): with cols[i]: df = get_binance_data(symbol) df = add_indicators(df) latest = df.iloc[-1] signal = get_signal(latest)

st.subheader(f"{name}")
    st.metric("Current Price", f"{latest['close']:.6f}")
    st.write(f"**RSI:** {latest['RSI']:.2f}  ")
    st.write(f"**MACD:** {latest['MACD']:.2f}, Signal: {latest['MACD_signal']:.2f}")
    st.markdown(f"### {signal}")
    plot_chart(df, name)

