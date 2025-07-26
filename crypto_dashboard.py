import streamlit as st
import requests
import pandas as pd
import ta

# Liste der Coins mit CoinGecko-IDs
coins = {
  "XRP": "ripple",
  "BTC": "bitcoin",
  "ETH": "ethereum",
  "VECHAIN": "vechain",
  "DOGE": "dogecoin",
  "FLOKI": "floki",
  "PEPE": "pepecoin-community"  # ID für die Community-Variante von PepeCoin
}

st.set_page_config(page_title="Krypto Trend & Kauf Dashboard", page_icon="📈", layout="wide")
st.title("📈 Krypto Trend & Kauf Dashboard")

# Funktion: Live-Preise holen
def fetch_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Fehler beim Laden der Preise")
        return None
    return res.json()

# Funktion: Chartdaten inklusive RSI, MA50, MA200 berechnen
@st.cache_data(ttl=300)
def fetch_market_data(coin_id, days=60):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    data = requests.get(url).json()
    prices = data.get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["rsi"] = ta.momentum.rsi(df["price"], window=14)
    df["ma50"] = df["price"].rolling(window=50).mean()
    df["ma200"] = df["price"].rolling(window=200).mean()
    return df.dropna()

prices = fetch_prices()

if not prices:
    st.warning("Keine Preisdaten verfügbar.")
else:
    for sym, cid in coins.items():
        eur_price = prices.get(cid, {}).get("eur")
        if eur_price is None:
            st.write(f"⚠️ {sym}: Preis nicht gefunden")
            continue

        df = fetch_market_data(cid, days=60)
        if df.empty:
            st.write(f"⚠️ {sym}: Marktdaten nicht verfügbar")
            continue

        latest_rsi = df["rsi"].iloc[-1]
        ma50 = df["ma50"].iloc[-1]
        ma200 = df["ma200"].iloc[-1]
        trend = "Bullish 📈" if ma50 > ma200 else "Bearish 📉"

        if latest_rsi < 30 and trend == "Bullish 📈":
            signal = "🚀 Kauf empfohlen!"
        elif latest_rsi > 70 and trend == "Bearish 📉":
            signal = "⚠️ Verkauf empfohlen!"
        else:
            signal = "➡️ Halten"

        st.subheader(f"{sym}: €{eur_price:.6f} | {trend} | RSI: {latest_rsi:.1f} | {signal}")
        st.line_chart(df[["price", "ma50", "ma200"]], height=250)

st.caption("Daten via CoinGecko • RSI & MA • Auto-Refresh Deck 15 s • Cache 5 Min")
