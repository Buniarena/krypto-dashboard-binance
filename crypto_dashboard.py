import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Lista e monedhave dhe CoinGecko ID
coins = {
    "Bitcoin": "bitcoin",
    "Dogecoin": "dogecoin",
    "XRP": "ripple"
}

st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📊 Krypto Dashboard me Analizë Teknike")

for name, cg_id in coins.items():
    st.subheader(f"{name} ({cg_id.upper()})")

    # Marrim të dhënat nga CoinGecko
    url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "30",
        "interval": "daily"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200 or "prices" not in response.json():
        st
