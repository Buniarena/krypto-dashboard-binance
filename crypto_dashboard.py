import streamlit as st
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import time

API_KEY = "KETU_VENDOS_API_CMC"  # API key nga CoinMarketCap (falas)
HEADERS = {"X-CMC_PRO_API_KEY": API_KEY}
REFRESH_INTERVAL = 180

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    return max(0, int(REFRESH_INTERVAL - (time.time() - st.session_state.start_time)))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()
        st.experimental_rerun()

st.set_page_config(page_title="📊 RSI & MACD (CMC)", layout="centered")
st.title("Crypto Dashboard me CoinMarketCap API")

coins = ["BTC","XRP","ETH","DOGE","BONK"]  # simbolë CoinMarketCap

@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_prices(symbols):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {"symbol":",".join(symbols), "convert":"USD"}
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()["data"]

@st.cache_data(ttl=3600)
def fetch_history(coin_id):  # coin_id si "BTC"
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
    params = {"symbol": coin_id, "convert":"USD", "time_period":"daily", "count":30}
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    items = r.json()["data"]["quotes"]
    prices = [item["quote"]["USD"]["close"] for item in items]
    return pd.DataFrame(prices, columns=["price"])

def get_signal(rsi, macd_diff):
    if rsi < 30 and macd_diff > 0:
        return "🟢 Bli"
    elif rsi > 70 and macd_diff < 0:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

def sig_color(s):
    return "green" if "Bli" in s else ("red" if "Shit" in s else "orange")

refresh_if_needed()

try:
    price_data = fetch_prices(coins)
except Exception as e:
    st.error(f"Error fetch price: {e}")
    price_data = {}

for sym in coins:
    rec = price_data.get(sym)
    if not rec:
        st.warning(f"{sym}: të dhëna mungojnë")
        continue

    price = rec["quote"]["USD"]["price"]
    change24 = rec["quote"]["USD"]["percent_change_24h"]
    hist = fetch_history(sym)
    if len(hist)>=15:
        rsi = round(RSIIndicator(hist["price"], window=14).rsi().iloc[-1],2)
        macd_diff = round(MACD(hist["price"]).macd_diff().iloc[-1],4)
    else:
        rsi = None
        macd_diff = None

    signal = get_signal(rsi or 50, macd_diff or 0)
    st.markdown(f"""
**{sym}**  
💰 Çmimi: ${price:.6f}  \n
📊 Ndryshimi 24h: {change24:.2f}%  \n
📈 RSI: {rsi if rsi is not None else 'N/A'}   📉 MACD diff: {macd_diff if macd_diff is not None else 'N/A'}  \n
🚨 Sinjali: <span style='color:{sig_color(signal)}'>{signal}</span>
""", unsafe_allow_html=True)

st.caption(f"🔄 Rifreskim automatik çdo {REFRESH_INTERVAL//60} min • CoinMarketCap API (falas)")
