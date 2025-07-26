import streamlit as st
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import time

# Konfigurimi i faqes
st.set_page_config(page_title="Paneli i Kriptovalutave", layout="wide")
st.title("📈 Çmimet & RSI / MA për BTC, ETH & XRP")

# Marrja e të dhënave me cache 5 minuta
@st.cache_data(ttl=300)
def merr_te_dhena(emri_monedit):
    url = f"https://api.coingecko.com/api/v3/coins/{emri_monedit}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minute"}
    headers = {"User-Agent": "Mozilla/5.0"}
    pergjigje = requests.get(url, params=params, headers=headers)
    pergjigje.raise_for_status()
    cmimet = pergjigje.json()["prices"]
    df = pd.DataFrame(cmimet, columns=["koha", "cmimi"])
    df["koha"] = pd.to_datetime(df["koha"], unit="ms")
    df.set_index("koha", inplace=True)
    return df

# Funksioni për analizë të monedhës
def analiz_monede(emri_shfaqur, emri_api):
    st.subheader(emri_shfaqur)
    try:
        df = merr_te_dhena(emri_api)
        cmimi = df["cmimi"].iloc[-1]
        rsi = RSIIndicator(df["cmimi"]).rsi().iloc[-1]
        ma = SMAIndicator(df["cmimi"], window=20).sma_indicator().iloc[-1]

        kol1, kol2, kol3 = st.columns(3)
        kol1.metric("💰 Çmimi", f"${cmimi:,.2f}")
        kol2.metric("📊 RSI", f"{rsi:.2f}")
        kol3.metric("📉 Mesatare Lëvizëse (20)", f"${ma:,.2f}")

        if rsi > 70:
            st.warning("⚠️ RSI: MBIBLEBLER")
        elif rsi < 30:
            st.success("✅ RSI: NËNÇMIM")
        else:
            st.info("ℹ️ RSI: NEUTRAL")

        st.line_chart(df["cmimi"])
    except Exception as e:
        st.error(f"Nuk u morën të dhëna për {emri_shfaqur}: {e}")

# Thirrja për çdo kriptomonedhë
analiz_monede("Bitcoin", "bitcoin")
analiz_monede("Ethereum", "ethereum")
analiz_monede("XRP", "ripple")

st.caption("⏱️ Rifreskim automatik çdo 15 sekonda. Cache: 5 minuta.")
time.sleep(15)
st.experimental_rerun()
