import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go
import ta

st.set_page_config(page_title="📈 Krypto Dashboard", layout="wide")
st.title("💹 Krypto Dashboard – BTC, DOGE, XRP")

# Përcakto coin-et dhe emrat
coins = {
    "Bitcoin": "bitcoin",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

# Merr të dhënat historike për një coin nga CoinGecko
def fetch_market_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "hourly"}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    return None

# Llogarit RSI nga çmimi
def calculate_rsi(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['price'], window=14).rsi()
    return df

# Jep sinjal bazuar në RSI
def signal_from_rsi(rsi):
    if rsi < 30:
        return "📈 BLI"
    elif rsi > 70:
        return "📉 SHIT"
    else:
        return "⏳ PRIT"

# Shfaq info për secilën crypto
for name, coin_id in coins.items():
    st.subheader(f"{name} ({coin_id.upper()})")
    df = fetch_market_data(coin_id)

    if df is not None and not df.empty:
        df = calculate_rsi(df)
        latest_price = df["price"].iloc[-1]
        price_1h_ago = df["price"].iloc[0]
        price_1d_ago = df["price"].iloc[0]  # sepse kemi vetëm 1 ditë të dhëna

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Çmimi aktual", f"${latest_price:,.4f}")
        col2.metric("🕐 1 Orë", f"${price_1h_ago:,.4f}", f"{latest_price - price_1h_ago:+.4f}")
        col3.metric("📅 1 Ditë", f"${price_1d_ago:,.4f}", f"{latest_price - price_1d_ago:+.4f}")

        # RSI dhe sinjal
        latest_rsi = df["rsi"].iloc[-1]
        st.markdown(f"**RSI:** `{latest_rsi:.2f}` → **{signal_from_rsi(latest_rsi)}**")

        # Grafik çmimi
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Çmimi"))
        fig.update_layout(title=f"Ecuria e Çmimit – {name}", xaxis_title="Ora", yaxis_title="Çmimi ($)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
    else:
        st.error(f"Nuk u morën të dhëna për {name}. Kontrollo lidhjen ose CoinGecko API.")
