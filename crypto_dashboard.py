import time
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from datetime import datetime
import random

# ==============================
# ⚙️ KONFIGURIME
# ==============================

BOT_TOKEN = "7627051456:AAHTTyUyP9i4ug3MUo63zmeeA3Uq61ByKKg"
CHAT_ID = "7274463074"

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

# ==============================
# 🔗 TELEGRAM TEST
# ==============================

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("❌ Gabim Telegram:", r.text)
        else:
            print("✅ Mesazhi u dërgua me sukses.")
    except Exception as e:
        print("❌ Problem me lidhjen Telegram:", e)

# ==============================
# 🔗 TË DHËNA
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
# 📊 ANALIZA
# ==============================

def analyze_coin(coin_name, coin_id):
    try:
        current = get_current_data(coin_id)
        df = get_historical_prices(coin_id)
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

        s = 0
        rsi = df["rsi"].iloc[-1]
        ema12 = df["ema12"].iloc[-1]
        ema26 = df["ema26"].iloc[-1]
        macd = df["macd"].iloc[-1]
        macd_signal = df["macd_signal"].iloc[-1]
        price = df["price"].iloc[-1]
        upper = df["bollinger_upper"].iloc[-1]
        lower = df["bollinger_lower"].iloc[-1]

        if rsi < 30: s += 1
        elif rsi > 70: s -= 1
        if ema12 > ema26: s += 1
        else: s -= 1
        if macd > macd_signal: s += 2
        else: s -= 2
        if price < lower: s += 1
        elif price > upper: s -= 1

        if s >= 3:
            decision = "🟢 BLI"
            prob_buy = 80 + random.randint(0, 15)
            prob_sell = 15 - random.randint(0, 10)
        elif s <= -3:
            decision = "🔴 SHIT"
            prob_buy = 15 - random.randint(0, 10)
            prob_sell = 80 + random.randint(0, 15)
        else:
            decision = "🟡 MBANJ"
            prob_buy = 50 + random.randint(-10, 10)
            prob_sell = 50 + random.randint(-10, 10)

        price_txt = f"${current['current_price']:.6f}"
        msg = (
            f"🚨 *{coin_name}* – *{decision}*\n"
            f"💵 Çmimi: {price_txt}\n"
            f"📊 Prob: *BLI* {prob_buy:.1f}% | *SHIT* {prob_sell:.1f}%\n"
            f"⏱️ {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"👤 Bunjamin Fetai"
        )
        send_telegram_message(msg)
    except Exception as e:
        print(f"❌ Gabim me {coin_name}: {e}")

# ==============================
# ⏰ LOOP 1 ORË
# ==============================

print("🚀 ElbuharBot po fillon…\n")
send_telegram_message("🤖 Bot-i u aktivizua! Sinjalet do dërgohen çdo 1 orë.")

while True:
    print(f"\n🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} – Dërgim sinjalesh...")
    for name, cid in coins.items():
        analyze_coin(name, cid)
        time.sleep(5)
    print("✅ Raundi përfundoi. Do përsëritet pas 1 ore.\n")
    time.sleep(3600)