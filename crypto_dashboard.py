import streamlit as st
import requests
import pandas as pd
import ta
import plotly.graph_objs as go

# Titulli i aplikacionit
st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📈 Krypto Dashboard me Binance")

# Funksioni për të marrë të dhëna nga Binance
def get_binance_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "15m",
        "limit": 200
    }
    response = requests.get(url, params=params)
    try:
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
    except Exception as e:
        st.error(f"Gabim gjatë marrjes së të dhënave për {symbol}: {e}")
        return pd.DataFrame()

# Funksioni për të shtuar indikatorët teknikë
def add_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    return df

# Funksioni për të gjeneruar sinjal
def get_signal(latest):
    rsi = latest['RSI']
    macd = latest['MACD']
    signal = latest['MACD_signal']
    if rsi < 30 and macd > signal:
        return "🟢 **Sinjal Blerjeje**"
    elif rsi > 70 and macd < signal:
        return "🔴 **Sinjal Shitjeje**"
    else:
        return "🟡 **Mbaj / Pa sinjal të qartë**"

# Funksioni për të vizualizuar grafikun
def plot_chart(df, name):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlesticks'
    ))
    fig.update_layout(title=f"{name} - Grafiku i Çmimit", xaxis_title="Koha", yaxis_title="Çmimi (USDT)", height=400)
    st.plotly_chart(fig, use_container_width=True)

# Lista e monedhave
symbols = {
    "Bitcoin (BTC)": "BTCUSDT",
    "Pepe (PEPE)": "PEPEUSDT",
    "Verge (XVG)": "XVGUSDT"
}

# Rreshtimi në tre kolona
cols = st.columns(len(symbols))

# Loop për çdo monedhë
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
        st.metric("Aktualisht", f"{latest['close']:.6f} USDT")
        st.write(f"**RSI:** {latest['RSI']:.2f}")
        st.write(f"**MACD:** {latest['MACD']:.4f} | Signal: {latest['MACD_signal']:.4f}")
        st.markdown(f"### {signal}")
        plot_chart(df, name)
