import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
import plotly.graph_objects as go
from requests.adapters import HTTPAdapter, Retry

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "Bonk": "bonk"
}

st.set_page_config(page_title="📈 RSI Dashboard", layout="centered")
st.title("📊 RSI dhe Çmimi për Coinet me Grafikë")

# Setup për requests me retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

@st.cache_data(ttl=600)
def get_price_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "2",
        "interval": "hourly"
    }
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = data.get("prices", [])
        if not prices:
            st.error(f"Nuk u gjetën të dhëna për {coin_id}")
            return None
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Gabim në kërkesë për {coin_id}: {e}")
        return None

def calculate_rsi(df, window=14):
    if df is None or len(df) < window:
        return None
    rsi_indicator = RSIIndicator(close=df["price"], window=window)
    rsi_series = rsi_indicator.rsi()
    return round(rsi_series.iloc[-1], 2)

def plot_price_and_rsi(df, coin_name):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["price"], mode="lines", name="Çmimi (USD)"))

    rsi_indicator = RSIIndicator(close=df["price"])
    df["RSI"] = rsi_indicator.rsi()

    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["RSI"],
        mode="lines",
        name="RSI",
        yaxis="y2"
    ))

    # Dy y-aksione: njëri për çmim dhe njëri për RSI
    fig.update_layout(
        title=f"{coin_name} - Çmimi dhe RSI",
        xaxis_title="Data",
        yaxis=dict(title="Çmimi (USD)", side="left"),
        yaxis2=dict(title="RSI", overlaying="y", side="right", range=[0, 100]),
        legend=dict(x=0, y=1),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def get_signal(rsi):
    if rsi is None:
        return "❓ Nuk ka të dhëna"
    elif rsi < 30:
        return "🟢 Bli"
    elif rsi > 70:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

for name, coin_id in coins.items():
    with st.expander(f"🔍 {name}"):
        df = get_price_history(coin_id)
        if df is not None:
            current_price = round(df["price"].iloc[-1], 6)
            rsi = calculate_rsi(df)
            signal = get_signal(rsi)

            st.write(f"💰 **Çmimi aktual:** ${current_price}")
            st.write(f"📈 **RSI:** {rsi if rsi is not None else 'N/A'}")
            st.write(f"📊 **Sinjali:** {signal}")

            plot_price_and_rsi(df, name)
        else:
            st.warning(f"Nuk u morën të dhënat për {name}. CoinGecko mund të jetë offline ose ka problem lidhjeje.")

st.caption("🔄 Të dhënat rifreskohen çdo 10 minuta. Burimi: CoinGecko")
