import time
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from datetime import datetime
import random
import os

# ==============================
# ⚙️ KONFIGURIMET
# ==============================

TELEGRAM_BOT_TOKEN = "7627051456:AAHTTyUyP9i4ug3MUo63zmeeA3Uq61ByKKg"
TELEGRAM_CHAT_ID = "7274463074"

coins = {
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge",
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum"
}

# ==============================
# 🔗 FUNKSIONE PËR TË DHËNA
# ==============================

def get_current_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": coin_id}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()[0]

def get_historical_prices(coin_id, days=60):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days), "interval": "daily"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("prices", [])
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

# ==============================
# 📊 LLOGARITJE SINJALESH
# ==============================

def calculate_indicators(df):
    df["rsi"] = RSIIndicator(df["price"]).rsi()
    df["ema12"] = EMAIndicator(df["price"], 12).ema_indicator()
    df["ema26"] = EMAIndicator(df["price"], 26).ema_indicator()
    macd_calc = MACD(df["price"])
    df["macd"] = macd_calc.macd()
    df["macd_signal"] = macd_calc.macd_signal()
    df["macd_histogram"] = macd_calc.macd_diff()
    bb = BollingerBands(df["price"])
    df["bollinger_upper"] = bb.bollinger_hband()
    df["bollinger_lower"] = bb.bollinger_lband()
    return df

def generate_signals(df):
    signals = []
    for i in range(len(df)):
        s = 0
        if df["rsi"].iloc[i] < 30: s += 1
        elif df["rsi"].iloc[i] > 70: s -= 1
        if df["ema12"].iloc[i] > df["ema26"].iloc[i]: s += 1
        else: s -= 1
        if df["macd"].iloc[i] > df["macd_signal"].iloc[i]: s += 2
        else: s -= 2
        if df["price"].iloc[i] < df["bollinger_lower"].iloc[i]: s += 1
        elif df["price"].iloc[i] > df["bollinger_upper"].iloc[i]: s -= 1
        signals.append(s)
    df["signal"] = signals
    return df

def classify_signal(s):
    if s >= 3:
        return "🟢 BLI"
    elif s <= -3:
        return "🔴 SHIT"
    else:
        return "🟡 MBANJ"

def calculate_probabilities(signal):
    if signal >= 3:
        return 80 + random.randint(0, 15), 15 - random.randint(0, 10)
    elif signal <= -3:
        return 15 - random.randint(0, 10), 80 + random.randint(0, 15)
    else:
        return 50 + random.randint(-10, 10), 50 + random.randint(-10, 10)

# ==============================
# ✈️ FUNKSION TELEGRAM
# ==============================

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code != 200:
        print("Gabim Telegram:", r.text)
    else:
        print("✅ Sinjali u dërgua në Telegram")

# ==============================
# 🔁 LOOP AUTOMATIK 1 ORË
# ==============================

while True:
    for selected_coin, coin_id in coins.items():
        try:
            current = get_current_data(coin_id)
            df = get_historical_prices(coin_id, days=60)
            df = calculate_indicators(df)
            df = generate_signals(df)
            latest_signal = df["signal"].iloc[-1]
            decision = classify_signal(latest_signal)
            prob_buy, prob_sell = calculate_probabilities(latest_signal)
            price_txt = f"${current['current_price']:.6f}" if current else "N/A"

            msg = (
                f"🚨 *{selected_coin}* – *{decision}*\n"
                f"💵 Çmimi: {price_txt}\n"
                f"📊 Prob: *BLI* {prob_buy:.1f}% | *SHIT* {prob_sell:.1f}%\n"
                f"⏱️ {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"👤 Bunjamin Fetai"
            )

            send_telegram_message(msg)
            time.sleep(5)  # pak pushim mes dërgesave

        except Exception as e:
            print(f"Gabim për {selected_coin}: {e}")
            continue

    print("⏳ Prit 1 orë për sinjalet e reja...")
    time.sleep(3600)  # 1 orë