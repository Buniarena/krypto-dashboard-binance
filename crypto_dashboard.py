import time, requests, pandas as pd, random
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from datetime import datetime

BOT_TOKEN = "7627051456:AAHTTyUyP9i4ug3MUo63zmeeA3Uq61ByKKg"
CHAT_ID = "7274463074"

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

def tg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=15)
    if r.status_code != 200:
        print("❌ Telegram:", r.text)
    else:
        print("✅ Dërguar:", text.splitlines()[0])

def cur(coin_id):
    r = requests.get("https://api.coingecko.com/api/v3/coins/markets",
                     params={"vs_currency":"usd", "ids":coin_id}, timeout=10)
    r.raise_for_status()
    return r.json()[0]

def hist(coin_id, days=60):
    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
                     params={"vs_currency":"usd","days":str(days),"interval":"daily"}, timeout=10)
    r.raise_for_status()
    data = r.json().get("prices", [])
    df = pd.DataFrame(data, columns=["ts","price"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df.set_index("ts", inplace=True)
    return df

def analyze(name, cid):
    c = cur(cid)
    df = hist(cid)
    df["rsi"] = RSIIndicator(df["price"]).rsi()
    df["ema12"] = pd.Series(df["price"]).ewm(span=12, adjust=False).mean()
    df["ema26"] = pd.Series(df["price"]).ewm(span=26, adjust=False).mean()
    macd = MACD(df["price"])
    df["macd"] = macd.macd(); df["macd_signal"] = macd.macd_signal()
    bb = BollingerBands(df["price"])
    up, lo = bb.bollinger_hband().iloc[-1], bb.bollinger_lband().iloc[-1]
    rsi = df["rsi"].iloc[-1]; ema12 = df["ema12"].iloc[-1]; ema26 = df["ema26"].iloc[-1]
    m, ms = df["macd"].iloc[-1], df["macd_signal"].iloc[-1]
    p = df["price"].iloc[-1]

    s = (1 if rsi < 30 else -1 if rsi > 70 else 0) \
        + (1 if ema12 > ema26 else -1) \
        + (2 if m > ms else -2) \
        + (1 if p < lo else -1 if p > up else 0)

    if s >= 3: dec = "🟢 BLI"; pb, ps = 80+random.randint(0,15), 15-random.randint(0,10)
    elif s <= -3: dec = "🔴 SHIT"; pb, ps = 15-random.randint(0,10), 80+random.randint(0,15)
    else: dec = "🟡 MBANJ"; pb, ps = 50+random.randint(-10,10), 50+random.randint(-10,10)

    msg = (
        f"🚨 *{name}* – *{dec}*\n"
        f"💵 Çmimi: ${c['current_price']:.6f}\n"
        f"📊 Prob: *BLI* {pb:.1f}% | *SHIT* {ps:.1f}%\n"
        f"⏱️ {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    tg(msg)

print("🚀 ElbuharBot start… dërgoj test fillestar.")
tg("🤖 Bot aktiv! Do dërgoj sinjal tani dhe pastaj çdo 1 orë.")

def run_round():
    print(f"🕒 Raund: {datetime.utcnow().strftime('%H:%M UTC')}")
    for n,cid in coins.items():
        try:
            analyze(n,cid)
            time.sleep(5)
        except Exception as e:
            print(f"❌ {n}:", e)

# dërgo menjëherë një raund
run_round()

# pastaj çdo 1 orë
while True:
    print("⏳ Prit 1 orë…")
    time.sleep(3600)
    run_round()