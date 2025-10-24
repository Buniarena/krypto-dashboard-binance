import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time

# ðŸ”” Zile audio (opsionale pÃ«r pÃ«rdorim tÃ« ardhshÃ«m)
AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"

# Konfigurime
REFRESH_INTERVAL = 300  # 5 minutes for slower refresh
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

# Lista e monedhave
coins = {
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

# -----------------------------
# Helpers pÃ«r tÃ« dhÃ«na nga API
# -----------------------------
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_current_data(coin_id: str):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    retries = 0
    max_retries = 5

    while retries < max_retries:
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 429:
                time.sleep(2 ** retries + 10)  # Exponential backoff + base wait
                retries += 1
                continue
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data:
                return data[0]
            return None
        except requests.exceptions.RequestException as e:
            # nÃ«se Ã«shtÃ« 429 i kapur nga raise_for_status
            if "429" in str(e):
                time.sleep(2 ** retries + 10)
                retries += 1
            else:
                return None
    return {"error": "429 after retries"}


@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id: str, days: int = 90) -> pd.DataFrame:
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days), "interval": "daily"}
    retries = 0
    max_retries = 5

    while retries < max_retries:
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 429:
                time.sleep(2 ** retries + 10)
                retries += 1
                continue
            response.raise_for_status()
            prices = response.json().get("prices", [])
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            if df.empty:
                return pd.DataFrame()
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["price"] = df["price"].astype(float)
            df = df.sort_values("timestamp").set_index("timestamp")
            return df
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                time.sleep(2 ** retries + 10)
                retries += 1
            else:
                return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=120)  # 2 minutes for short-term
def get_short_term_data(coin_id: str) -> pd.DataFrame:
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minutely"}
    retries = 0
    max_retries = 5

    while retries < max_retries:
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 429:
                time.sleep(2 ** retries + 10)
                retries += 1
                continue
            response.raise_for_status()
            prices = response.json().get("prices", [])
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            if df.empty:
                return pd.DataFrame()
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df["price"] = df["price"].astype(float)
            return df
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                time.sleep(2 ** retries + 10)
                retries += 1
            else:
                return pd.DataFrame()
    return pd.DataFrame()


# -----------------------------
# IndikatorÃ«t teknikÃ«
# -----------------------------
def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    if len(prices) < period + 1:
        return pd.Series(np.nan, index=prices.index)
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0).fillna(0.0)
    loss = (-delta.where(delta < 0, 0.0)).fillna(0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    rsi.iloc[:period-1] = np.nan
    return rsi


def calculate_ema(prices: pd.Series, span: int) -> pd.Series:
    return prices.ewm(span=span, adjust=False).mean()


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd = ema_fast - ema_slow
    macd_signal = calculate_ema(macd, signal)
    histogram = macd - macd_signal
    return macd, macd_signal, histogram


def calculate_bollinger_bands(prices: pd.Series, window: int = 20, num_std: int = 2):
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return sma, upper, lower


def calculate_probabilities(short_term_df: pd.DataFrame, interval_min: int = 5):
    if short_term_df.empty or len(short_term_df) < 2:
        return 50.0, 50.0
    # Resample sipas intervalit, marrim Ã§mimin e fundit pÃ«r Ã§do segment
    resampled = short_term_df["price"].resample(f"{interval_min}T").last().dropna()
    changes = resampled.diff().dropna()
    if len(changes) == 0:
        return 50.0, 50.0
    up_prob = float((changes > 0).mean() * 100)
    down_prob = 100.0 - up_prob
    return up_prob, down_prob


# -----------------------------
# UI
# -----------------------------
st.image(HEADER_IMAGE_URL, use_container_width=True)
st.title("AnalizÃ« Kriptovalutash: RSI, EMA, MACD, Bollinger Bands dhe Sinjale")

selected_coin = st.selectbox("Zgjidh monedhÃ«n", list(coins.keys()))
coin_id = coins[selected_coin]

days = st.slider("Numri i ditÃ«ve historike", min_value=30, max_value=365, value=90, step=30)

with st.spinner('Duke ngarkuar tÃ« dhÃ«nat aktuale...'):
    time.sleep(0.5)
    current_data = get_current_data(coin_id)

if current_data is None:
    st.error("Nuk u mund tÃ« merren tÃ« dhÃ«nat pÃ«r monedhÃ«n e zgjedhur. Provoni pÃ«rsÃ«ri mÃ« vonÃ«.")
elif isinstance(current_data, dict) and "error" in current_data:
    st.error(f"Gabim API: {current_data['error']}. Kjo mund tÃ« jetÃ« pÃ«r shkak tÃ« kufizimeve tÃ« normÃ«s. Provoni pÃ«rsÃ«ri pas disa minutash.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"Ã‡mimi aktual i {selected_coin}", value=f"${current_data['current_price']:.6f}")
    with col2:
        st.metric(label="Kapitalizimi i Tregut", value=f"${current_data['market_cap']:,.0f}")
    with col3:
        st.metric(label="VÃ«llimi 24h", value=f"${current_data['total_volume']:,.0f}")

with st.spinner('Duke ngarkuar tÃ« dhÃ«na afatshkurtra...'):
    time.sleep(0.3)
    short_term_prices = get_short_term_data(coin_id)

if not short_term_prices.empty:
    st.subheader("Probabilitetet pÃ«r LÃ«vizjen e AfÃ«rt (bazuar nÃ« 24 orÃ«t e fundit)")
    up_5, down_5 = calculate_probabilities(short_term_prices, 5)
    up_15, down_15 = calculate_probabilities(short_term_prices, 15)
    up_30, down_30 = calculate_probabilities(short_term_prices, 30)
    up_60, down_60 = calculate_probabilities(short_term_prices, 60)

    col_prob1, col_prob2, col_prob3, col_prob4 = st.columns(4)
    with col_prob1:
        st.metric("Shansi pÃ«r Rritje nÃ« 5 Min", f"{up_5:.1f}%")
        st.metric("Shansi pÃ«r RÃ«nie nÃ« 5 Min", f"{down_5:.1f}%")
    with col_prob2:
        st.metric("Shansi pÃ«r Rritje nÃ« 15 Min", f"{up_15:.1f}%")
        st.metric("Shansi pÃ«r RÃ«nie nÃ« 15 Min", f"{down_15:.1f}%")
    with col_prob3:
        st.metric("Shansi pÃ«r Rritje nÃ« 30 Min", f"{up_30:.1f}%")
        st.metric("Shansi pÃ«r RÃ«nie nÃ« 30 Min", f"{down_30:.1f}%")
    with col_prob4:
        st.metric("Shansi pÃ«r Rritje nÃ« 1 OrÃ«", f"{up_60:.1f}%")
        st.metric("Shansi pÃ«r RÃ«nie nÃ« 1 OrÃ«", f"{down_60:.1f}%")
else:
    st.warning("Nuk u gjetÃ«n tÃ« dhÃ«na afatshkurtra pÃ«r probabilitete. Kjo mund tÃ« jetÃ« pÃ«r shkak tÃ« kufizimeve tÃ« API-sÃ«.")

with st.spinner('Duke ngarkuar tÃ« dhÃ«na historike...'):
    time.sleep(0.3)
    historical_prices = get_historical_prices(coin_id, days=days)

if historical_prices.empty:
    st.warning("Nuk u gjetÃ«n Ã§mime historike. Provoni tÃ« rrisni intervalin e kohÃ«s ose provoni mÃ« vonÃ«.")
else:
    # Llogarit indikatorÃ«t
    prices = historical_prices["price"]
    rsi = calculate_rsi(prices)
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    macd, macd_signal, histogram = calculate_macd(prices)
    sma20, upper, lower = calculate_bollinger_bands(prices)

    # Krijo sinjalet e pÃ«rmbledhura
    valid = rsi.notna() & ema12.notna() & ema26.notna() & macd.notna() & sma20.notna() & upper.notna() & lower.notna()

    signal = pd.Series(0, index=historical_prices.index)

    # RSI
    signal.loc[valid & (rsi < 30)] += 1
    signal.loc[valid & (rsi > 65)] -= 1

    # EMA cross
    ema_buy = (ema12 > ema26) & (ema12.shift(1) <= ema26.shift(1))
    ema_sell = (ema12 < ema26) & (ema12.shift(1) >= ema26.shift(1))
    signal.loc[valid & ema_buy] += 1
    signal.loc[valid & ema_sell] -= 1

    # MACD cross + bias
    macd_buy = (macd > macd_signal) & (macd.shift(1) <= macd_signal.shift(1))
    macd_sell = (macd < macd_signal) & (macd.shift(1) >= macd_signal.shift(1))
    signal.loc[valid & macd_buy] += 2
    signal.loc[valid & macd_sell] -= 2

    macd_positive = (macd > 0) & (histogram > 0)
    macd_negative = (macd < 0) & (histogram < 0)
    signal.loc[valid & macd_positive] += 1
    signal.loc[valid & macd_negative] -= 1

    # Bollinger
    signal.loc[valid & (prices < lower)] += 1
    signal.loc[valid & (prices > upper)] -= 1

    # Bashkangjit kolonat pÃ«r vizualizim/tabelÃ«
    df = pd.DataFrame({
        "price": prices,
        "rsi": rsi,
        "ema12": ema12,
        "ema26": ema26,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_histogram": histogram,
        "sma20": sma20,
        "bollinger_upper": upper,
        "bollinger_lower": lower,
        "signal": signal
    })

    def get_color(sig):
        if sig > 3:
            return 'darkgreen'
        elif sig > 1:
            return 'green'
        elif sig < -3:
            return 'darkred'
        elif sig < -1:
            return 'red'
        else:
            return 'yellow'

    colors = df["signal"].map(get_color)

    # GrafikÃ«t
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(f'Ã‡mimi, EMA, Bollinger Bands pÃ«r {selected_coin}', 'RSI', 'MACD'),
        row_heights=[0.5, 0.2, 0.3]
    )

    # Ã‡mimi + EMA + Bollinger + shenjat
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Ã‡mimi', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema12'], mode='lines', name='EMA 12', line=dict(color='orange')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema26'], mode='lines', name='EMA 26', line=dict(color='purple')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['sma20'], mode='lines', name='SMA 20 (Bollinger Middle)', line=dict(color='black', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['bollinger_upper'], mode='lines', name='Bollinger Upper', line=dict(color='gray')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['bollinger_lower'], mode='lines', name='Bollinger Lower', line=dict(color='gray')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='markers', name='Sinjali', marker=dict(color=colors, size=8, symbol='circle')), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], mode='lines', name='RSI', line=dict(color='teal')), row=2, col=1)
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Overbought (65)", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)", row=2, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['macd'], mode='lines', name='MACD', line=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], mode='lines', name='MACD Signal', line=dict(color='orange')), row=3, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['macd_histogram'], name='MACD Histogram', marker_color='gray'), row=3, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=1)

    fig.update_layout(
        height=1200,
        title_text=f'AnalizÃ« e PlotÃ« pÃ«r {selected_coin}',
        xaxis_title='Data',
        yaxis_title='Ã‡mimi (USD)',
        yaxis2_title='RSI',
        yaxis3_title='MACD',
        legend_title='IndikatorÃ«t'
    )

    with st.spinner('Duke gjeneruar grafikun...'):
        time.sleep(0.2)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("TÃ« DhÃ«na Historike tÃ« Fundit (10 ditÃ«t e fundit)")
    st.dataframe(df.tail(10)[['price', 'rsi', 'ema12', 'ema26', 'macd', 'macd_signal', 'macd_histogram', 'bollinger_upper', 'bollinger_lower', 'signal']])