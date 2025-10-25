import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
REFRESH_INTERVAL = 180
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

coins = {
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge",
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum"
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
def get_historical_prices(coin_id, days=90):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days), "interval": "daily"}
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

def calculate_ema(prices, span):
    return prices.ewm(span=span, adjust=False).mean()

def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd = ema_fast - ema_slow
    macd_signal = calculate_ema(macd, signal)
    histogram = macd - macd_signal
    return macd, macd_signal, histogram

def calculate_bollinger_bands(prices, window=20, num_std=2):
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return sma, upper, lower

st.image(HEADER_IMAGE_URL, use_column_width="always")
st.title("Analizë Kriptovalutash: RSI, EMA, MACD (me Sinjale më të Forta), Bollinger Bands dhe Sinjale")

selected_coin = st.selectbox("Zgjidh monedhën", list(coins.keys()))
coin_id = coins[selected_coin]

days = st.slider("Numri i ditëve historike", min_value=30, max_value=365, value=90, step=30)

current_data = get_current_data(coin_id)
if current_data is None:
    st.error("Nuk u mund të merren të dhënat për monedhën e zgjedhur.")
elif "error" in current_data:
    st.error(f"Gabim API: {current_data['error']}")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"Çmimi aktual i {selected_coin}", value=f"${current_data['current_price']:.6f}")
    with col2:
        st.metric(label="Kapitalizimi i Tregut", value=f"${current_data['market_cap']:,.0f}")
    with col3:
        st.metric(label="Vëllimi 24h", value=f"${current_data['total_volume']:,.0f}")

historical_prices = get_historical_prices(coin_id, days=days)
if historical_prices.empty:
    st.warning("Nuk u gjetën çmime historike.")
else:
    historical_prices = historical_prices.sort_values("timestamp")
    historical_prices['timestamp'] = pd.to_datetime(historical_prices['timestamp'], unit='ms')
    historical_prices.set_index('timestamp', inplace=True)

    # Llogarit indikatorët
    historical_prices["rsi"] = calculate_rsi(historical_prices["price"])
    historical_prices["ema12"] = calculate_ema(historical_prices["price"], 12)
    historical_prices["ema26"] = calculate_ema(historical_prices["price"], 26)
    historical_prices["macd"], historical_prices["macd_signal"], historical_prices["macd_histogram"] = calculate_macd(historical_prices["price"])
    historical_prices["sma20"], historical_prices["bollinger_upper"], historical_prices["bollinger_lower"] = calculate_bollinger_bands(historical_prices["price"])

    # Gjenero sinjale bazuar në RSI, EMA crossover, MACD crossover (me peshë më të lartë), dhe Bollinger
    def generate_signals(df):
        signals = []
        for i in range(len(df)):
            rsi = df["rsi"].iloc[i]
            ema12 = df["ema12"].iloc[i]
            ema26 = df["ema26"].iloc[i]
            macd = df["macd"].iloc[i]
            macd_signal = df["macd_signal"].iloc[i]
            price = df["price"].iloc[i]
            upper = df["bollinger_upper"].iloc[i]
            lower = df["bollinger_lower"].iloc[i]
            histogram = df["macd_histogram"].iloc[i]

            signal = 0
            if pd.isna(rsi) or pd.isna(ema12) or pd.isna(macd) or pd.isna(upper):
                signals.append(0)
                continue

            # RSI sinjal
            if rsi < 30:
                signal += 1  # blej
            elif rsi > 70:
                signal -= 1  # shit

            # EMA crossover
            if ema12 > ema26 and (i > 0 and df["ema12"].iloc[i-1] <= df["ema26"].iloc[i-1]):
                signal += 1  # blej
            elif ema12 < ema26 and (i > 0 and df["ema12"].iloc[i-1] >= df["ema26"].iloc[i-1]):
                signal -= 1  # shit

            # MACD crossover me peshë më të lartë (+2/-2) dhe shtim për histogram
            if macd > macd_signal and (i > 0 and df["macd"].iloc[i-1] <= df["macd_signal"].iloc[i-1]):
                signal += 2  # blej më fort
            elif macd < macd_signal and (i > 0 and df["macd"].iloc[i-1] >= df["macd_signal"].iloc[i-1]):
                signal -= 2  # shit më fort

            # Shtim për MACD zero line dhe histogram për sinjale më të forta
            if macd > 0 and histogram > 0:
                signal += 1  # përforcim blej
            elif macd < 0 and histogram < 0:
                signal -= 1  # përforcim shit

            # Bollinger Bands
            if price < lower:
                signal += 1  # blej
            elif price > upper:
                signal -= 1  # shit

            signals.append(signal)
        return signals

    historical_prices["signal"] = generate_signals(historical_prices)
    
    # Ngjyrat sipas sinjalit (përshtatur për sinjale më të forta)
    def get_color(signal):
        if signal > 3:
            return 'darkgreen'  # shumë fort blej
        elif signal > 1:
            return 'green'      # blej
        elif signal < -3:
            return 'darkred'    # shumë fort shit
        elif signal < -1:
            return 'red'        # shit
        else:
            return 'yellow'     # neutral

    colors = historical_prices["signal"].apply(get_color)

    # Krijo grafik me subplots: Çmimi + Indikatorë lart, RSI në mes, MACD poshtë
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, 
                        subplot_titles=(f'Çmimi, EMA, Bollinger Bands për {selected_coin}', 'RSI', 'MACD'),
                        row_heights=[0.5, 0.2, 0.3])

    # Row 1: Çmimi dhe indikatorët
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['price'], mode='lines', name='Çmimi', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['ema12'], mode='lines', name='EMA 12', line=dict(color='orange')), row=1, col=1)
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['ema26'], mode='lines', name='EMA 26', line=dict(color='purple')), row=1, col=1)
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['sma20'], mode='lines', name='SMA 20 (Bollinger Middle)', line=dict(color='black', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['bollinger_upper'], mode='lines', name='Bollinger Upper', line=dict(color='gray')), row=1, col=1)
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['bollinger_lower'], mode='lines', name='Bollinger Lower', line=dict(color='gray')), row=1, col=1)
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['price'], mode='markers', name='Sinjali', marker=dict(color=colors, size=8, symbol='circle')), row=1, col=1)

    # Row 2: RSI
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['rsi'], mode='lines', name='RSI', line=dict(color='teal')), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)", row=2, col=1)

    # Row 3: MACD
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['macd'], mode='lines', name='MACD', line=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['macd_signal'], mode='lines', name='MACD Signal', line=dict(color='orange')), row=3, col=1)
    fig.add_trace(go.Bar(x=historical_prices.index, y=historical_prices['macd_histogram'], name='MACD Histogram', marker_color='gray'), row=3, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=1)

    fig.update_layout(height=1000, title_text=f'Analizë e Plotë për {selected_coin}',
                      xaxis_title='Data',
                      yaxis_title='Çmimi (USD)',
                      yaxis2_title='RSI',
                      yaxis3_title='MACD',
                      legend_title='Indikatorët')

    st.plotly_chart(fig, use_container_width=True)

    # Shfaq tabelën me të dhëna të fundit
    st.subheader("Të Dhëna Historike të Fundit (10 ditët e fundit)")
    st.dataframe(historical_prices.tail(10)[['price', 'rsi', 'ema12', 'ema26', 'macd', 'macd_signal', 'macd_histogram', 'bollinger_upper', 'bollinger_lower', 'signal']])