import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time

AUDIO_URL = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
REFRESH_INTERVAL = 300 # Rritur në 5 minuta për refresh më të ngadalshëm
HEADER_IMAGE_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

coins = {
 "PEPE": "pepe",
 "Shiba": "shiba-inu",
 "XVG (Verge)": "verge"
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

@st.cache_data(ttl=120) # Rritur në 2 minuta për refresh më të ngadalshëm
def get_short_term_data(coin_id):
 url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
 params = {"vs_currency": "usd", "days": "1", "interval": "minutely"}
 try:
 response = requests.get(url, params=params, timeout=10)
 if response.status_code == 429:
 return pd.DataFrame()
 response.raise_for_status()
 prices = response.json().get("prices", [])
 df = pd.DataFrame(prices, columns=["timestamp", "price"])
 df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
 df.set_index("timestamp", inplace=True)
 df["price"] = df["price"].astype(float)
 return df
 except Exception:
 return pd.DataFrame()

def calculate_rsi(prices, period=14):
 if len(prices) < period + 1:
 return pd.Series(np.nan, index=prices.index)
 delta = prices.diff()
 gain = delta.where(delta > 0, 0).fillna(0)
 loss = (-delta.where(delta < 0, 0)).fillna(0)
 avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
 avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
 rs = avg_gain / avg_loss
 rsi = 100 - 100 / (1 + rs)
 rsi.iloc[:period-1] = np.nan
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

def calculate_probabilities(short_term_df, interval_min=5):
 if short_term_df.empty or len(short_term_df) < 2:
 return 50, 50 # Default 50/50 nëse nuk ka të dhëna
 # Resample në intervalin e specifikuar
 resampled = short_term_df["price"].resample(f'{interval_min}T').last().dropna()
 changes = resampled.diff().dropna()
 up_prob = (changes > 0).mean() * 100 if len(changes) > 0 else 50
 down_prob = 100 - up_prob
 return up_prob, down_prob

st.image(HEADER_IMAGE_URL, use_container_width=True)
st.title("Analizë Kriptovalutash: RSI, EMA, MACD (me Sinjale më të Forta), Bollinger Bands dhe Sinjale")

selected_coin = st.selectbox("Zgjidh monedhën", list(coins.keys()))
coin_id = coins[selected_coin]

days = st.slider("Numri i ditëve historike", min_value=30, max_value=365, value=90, step=30)

with st.spinner('Duke ngarkuar të dhënat aktuale...'):
 time.sleep(1) # Shtuar delay për shfaqje më të ngadalshme
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

# Merr të dhëna afatshkurtra për probabilitete
with st.spinner('Duke ngarkuar të dhëna afatshkurtra...'):
 time.sleep(1) # Shtuar delay
 short_term_prices = get_short_term_data(coin_id)

if not short_term_prices.empty:
 st.subheader("Probabilitetet për Lëvizjen e Ardhshme (bazuar në 24 orët e fundit)")
 up_5, down_5 = calculate_probabilities(short_term_prices, 5)
 up_15, down_15 = calculate_probabilities(short_term_prices, 15)
 up_30, down_30 = calculate_probabilities(short_term_prices, 30)
 up_60, down_60 = calculate_probabilities(short_term_prices, 60)
 
 col_prob1, col_prob2, col_prob3, col_prob4 = st.columns(4)
 with col_prob1:
 st.metric("Shansi për Rritje në 5 Min", f"{up_5:.1f}%")
 st.metric("Shansi për Rënie në 5 Min", f"{down_5:.1f}%")
 with col_prob2:
 st.metric("Shansi për Rritje në 15 Min", f"{up_15:.1f}%")
 st.metric("Shansi për Rënie në 15 Min", f"{down_15:.1f}%")
 with col_prob3:
 st.metric("Shansi për Rritje në 30 Min", f"{up_30:.1f}%")
 st.metric("Shansi për Rënie në 30 Min", f"{down_30:.1f}%")
 with col_prob4:
 st.metric("Shansi për Rritje në 1 Orë", f"{up_60:.1f}%")
 st.metric("Shansi për Rënie në 1 Orë", f"{down_60:.1f}%")
else:
 st.warning("Nuk u gjetën të dhëna afatshkurtra për probabilitete.")

with st.spinner('Duke ngarkuar të dhëna historike...'):
 time.sleep(1) # Shtuar delay
 historical_prices = get_historical_prices(coin_id, days=days)

if historical_prices.empty:
 st.warning("Nuk u gjetën çmime historike.")
else:
 historical_prices = historical_prices.sort_values("timestamp")
 historical_prices['timestamp'] = pd.to_datetime(historical_prices['timestamp'], unit='ms')
 historical_prices.set_index('timestamp', inplace=True)

 # Llogarit indikatorët (të gjitha vektoriale)
 prices = historical_prices["price"]
 historical_prices["rsi"] = calculate_rsi(prices)
 historical_prices["ema12"] = calculate_ema(prices, 12)
 historical_prices["ema26"] = calculate_ema(prices, 26)
 historical_prices["macd"], historical_prices["macd_signal"], historical_prices["macd_histogram"] = calculate_macd(prices)
 historical_prices["sma20"], historical_prices["bollinger_upper"], historical_prices["bollinger_lower"] = calculate_bollinger_bands(prices)

 # Gjenero sinjale në mënyrë vektoriale
 rsi = historical_prices["rsi"]
 ema12 = historical_prices["ema12"]
 ema26 = historical_prices["ema26"]
 macd = historical_prices["macd"]
 macd_signal = historical_prices["macd_signal"]
 histogram = historical_prices["macd_histogram"]
 price = historical_prices["price"]
 upper = historical_prices["bollinger_upper"]
 lower = historical_prices["bollinger_lower"]

 # Mask për të shmangur NaN
 valid = rsi.notna() & ema12.notna() & macd.notna() & upper.notna()

 signal = pd.Series(0, index=historical_prices.index)

 # RSI sinjal (ndryshuar në 65/30)
 signal[valid & (rsi < 30)] += 1
 signal[valid & (rsi > 65)] -= 1

 # EMA crossover
 ema_buy = (ema12 > ema26) & (ema12.shift(1) <= ema26.shift(1))
 ema_sell = (ema12 < ema26) & (ema12.shift(1) >= ema26.shift(1))
 signal[valid & ema _buy] += 1
 signal[valid & ema_sell] -= 1

 # MACD crossover me peshë më të lartë
 macd_buy = (macd > macd_signal) & (macd.shift(1) <= macd_signal.shift(1))
 macd_sell = (macd < macd_signal) & (macd.shift(1) >= macd_signal.shift(1))
 signal[valid & macd_buy] += 2
 signal[valid & macd_sell] -= 2

 # Përforcim MACD zero line dhe histogram
 macd_positive = (macd > 0) & (histogram > 0)
 macd_negative = (macd < 0) & (histogram < 0)
 signal[valid & macd_positive] += 1
 signal[valid & macd_negative] -= 1

 # Bollinger Bands
 signal[valid & (price < lower)] += 1
 signal[valid & (price > upper)] -= 1

 historical_prices["signal"] = signal
 
 # Ngjyrat sipas sinjalit
 def get_color(signal):
 if signal > 3:
 return 'darkgreen'
 elif signal > 1:
 return 'green'
 elif signal < -3:
 return 'darkred'
 elif signal < -1:
 return 'red'
 else:
 return 'yellow'

 colors = historical_prices["signal"].map(get_color)

 # Krijo grafik me subplots
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

 # Row 2: RSI (ndryshuar në 65/30)
 fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['rsi'], mode='lines', name='RSI', line=dict(color='teal')), row=2, col=1)
 fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Overbought (65)", row=2, col=1)
 fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)", row=2, col=1)

 # Row 3: MACD
 fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['macd'], mode='lines', name='MACD', line=dict(color='blue')), row=3, col=1)
 fig.add_trace(go.Scatter(x=historical_prices.index, y=historical_prices['macd_signal'], mode='lines', name='MACD Signal', line=dict(color='orange')), row=3, col=1)
 fig.add_trace(go.Bar(x=historical_prices.index, y=historical_prices['macd_histogram'], name='MACD Histogram', marker_color='gray'), row=3, col=1)
 fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=1)

 fig.update_layout(height=1200, title_text=f'Analizë e Plotë për {selected_coin}', # Rritur lartësinë për shfaqje më të mirë
 xaxis_title='Data',
 yaxis_title='Çmimi (USD)',
 yaxis2_title='RSI',
 yaxis3_title='MACD',
 legend_title='Indikatorët')

 with st.spinner('Duke gjeneruar grafikun...'):
 time.sleep(2) # Shtuar delay më të gjatë për shfaqje të ngadalshme të grafikës
 st.plotly_chart(fig, use_container_width=True)

 # Shfaq tabelën me të dhëna të fundit
 st.subheader("Të Dhëna Historike të Fundit (10 ditët e fundit)")
 st.dataframe(historical_prices.tail( 10)[['price', 'rsi', 'ema12', 'ema26', 'macd', 'macd_signal', 'macd_histogram', 'bollinger_upper', 'bollinger_lower', 'signal']])
``` 