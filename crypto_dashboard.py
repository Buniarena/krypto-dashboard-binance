import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import time

st.set_page_config(page_title="Paneli i Kriptovalutave", layout="wide")
st.title("📈 Çmimet dhe RSI / MA për BTC, ETH & XRP")

@st.cache_data(ttl=300)
def merr_te_dhena(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "1",
            "interval": "minute"
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()["prices"]
        df = pd.DataFrame(data, columns=["koha", "cmimi"])
        df["koha"] = pd.to_datetime(df["koha"], unit="ms")
        df.set_index("koha", inplace=True)
        return df
    except:
        return None

def analiz_monede(emri_shfaqur, coin_id):
    st.subheader(emri_shfaqur)
    df = merr_te_dhena(coin_id)
    if df is None or df.empty:
        st.error(f"Nuk u morën të dhëna për {emri_shfaqur}")
        return

    cmimi = df["cmimi"].iloc[-1]
    rsi = RSIIndicator(df["cmimi"]).rsi().iloc[-1]
    ma = SMAIndicator(df["cmimi"], window=20).sma_indicator().iloc[-1]

    kol1, kol2, kol3 = st.columns(3)
    kol1.metric("💰 Çmimi", f"${cmimi:,.2f}")
    kol2.metric("📊 RSI", f"{rsi:.2f}")
    kol3.metric("📉 MA (20)", f"${ma:,.2f}")

    if rsi > 70:
        st.warning("⚠️ RSI: Mbiblerje")
    elif rsi < 30:
        st.success("✅ RSI: Nënçmim")
    else:
        st.info("ℹ️ RSI: Neutral")

    st.line_chart(df["cmimi"])

# Thirrja për analizë të tre kriptove
analiz_monede("Bitcoin (BTC)", "bitcoin")
analiz_monede("Ethereum (ETH)", "ethereum")
analiz_monede("Ripple (XRP)", "ripple")

st.caption("⏱️ Rifreskim automatik çdo 15 sekonda. Cache: 5 minuta.")
time.sleep(15)
st.experimental_rerun()
