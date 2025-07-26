import streamlit as st
import requests
import pandas as pd
import time
from ta.momentum import RSIIndicator

# Konfigurime
REFRESH_INTERVAL = 180  # sekonda (3 minuta)
REQUEST_DELAY = 1.5  # sekonda vonesë midis kërkesave për të shmangur 429

HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

coins = {
    "Bitcoin": "bitcoin",
    "PEPE": "pepe",
    "Doge": "dogecoin",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

API_KEY = ""  # Nëse ke, vendos këtu
headers = {"x-cg-pro-api-key": API_KEY} if API_KEY else {}

@st.cache_data(ttl=REFRESH_INTERVAL)
def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 429:
            # Kthejmë një mesazh specifik për kufizim
            return {"error": "429"}
        response.raise_for_status()
        return response.json()[0]
    except Exception:
        return None

@st.cache_data(ttl=REFRESH_INTERVAL)
def get_historical_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "60", "interval": "daily"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 429:
            return pd.DataFrame()  # Kthe bosh për 429
        response.raise_for_status()
        prices = response.json().get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["price"] = df["price"].astype(float)
        return df
    except Exception:
        return pd.DataFrame()

def calculate_rsi(df):
    if df.empty or len(df) < 14:
        return None
    try:
        rsi = RSIIndicator(close=df["price"]).rsi().iloc[-1]
        return round(rsi, 2)
    except Exception:
        return None

def generate_signal(rsi):
    if rsi is None:
        return "❓ N/A"
    if rsi < 30:
        return "🟢 Bli"
    elif rsi > 70:
        return "🔴 Shit"
    else:
        return "🟡 Mbaj"

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

def seconds_remaining():
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(REFRESH_INTERVAL - elapsed))

def refresh_if_needed():
    if seconds_remaining() <= 0:
        st.session_state.start_time = time.time()

header_style = f"""
    <style>
    .header-image {{
        position: relative;
        width: 100%;
        height: 180px;
        background-image: url('{HEADER_IMAGE_URL}');
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        margin-bottom: 25px;
    }}
    .header-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 4rem;
        font-weight: 900;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.7);
        letter-spacing: 8px;
    }}
    </style>
"""

st.markdown(header_style, unsafe_allow_html=True)
st.markdown(f"""
    <div class="header-image">
        <div class="header-text">Bitcoin B</div>
    </div>
""", unsafe_allow_html=True)

st.title("📊 Dashboard: RSI, Çmimi dhe Sinjale")
st.caption(f"⏳ Rifreskimi automatik në: {seconds_remaining()} sekonda")

refresh_if_needed()

for idx, (name, coin_id) in enumerate(coins.items()):
    st.subheader(name)

    data = get_current_data(coin_id)

    # Nëse po marrim error 429 nga API
    if data == {"error": "429"}:
        st.warning(f"Kufizim API (429) për '{coin_id}'. Nuk mund të marrim të dhëna aktuale.")
        continue
    elif data is None:
        st.warning(f"Gabim gjatë marrjes së të dhënave për '{coin_id}'.")
        continue

    # Vonesë për të shmangur kërkesat shumë të shpeshta
    if idx < len(coins) - 1:
        time.sleep(REQUEST_DELAY)

    historical = get_historical_prices(coin_id)
    rsi = calculate_rsi(historical)
    signal = generate_signal(rsi)

    price = data.get("current_price", "N/A")
    change_24h = data.get("price_change_percentage_24h", "N/A")
    price_str = f"${price:,.8f}" if isinstance(price, float) and price < 1 else f"${price:,.2f}"

    st.markdown(f"""
    💰 **Çmimi:** {price_str}  
    📊 **Ndryshimi 24h:** {change_24h:.2f}%  
    📈 **RSI:** {rsi if rsi is not None else "N/A"}  
    💡 **Sinjal:** {signal}
    """)

st.info("🔄 Të dhënat rifreskohen automatikisht çdo 3 minuta. Burimi: CoinGecko")
