# main_debug.py — ElbuharBot (me debug aktiv, pa Telegram)

import time
import requests
import pandas as pd
from datetime import datetime, timezone

# ================= SETTINGS =================
INTERVAL_SEC = 60 * 60   # çdo 1 orë
COINS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}
HIST_DAYS = 60
TIMEOUT = 15
MAX_RETRY = 5
last_signals = {}

# ============ HTTP helper ============
def http_get_json(url, params=None):
    delay = 1
    for attempt in range(1, MAX_RETRY + 1):
        try:
            print(f"🌐 GET {url.split('/')[-1]} (attempt {attempt})")
            r = requests.get(url, params=params, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            print(f"⚠️ HTTP {r.status_code}, retry pas {delay}s")
            time.sleep(delay)
            delay = min(delay * 2, 30)
        except Exception as e:
            print(f"❌ Network error {attempt}: {e}")
            time.sleep(delay)
    return None

# ============ DATA ============
def get_current_price_row(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    js = http_get_json(url, {"vs_currency": "usd", "ids": coin_id})
    if not js:
        raise RuntimeError("❌ S'ka current data për " + coin_id)
    return js[0]

def get_hist_df(coin_id, days=HIST_DAYS):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    js = http_get_json(url, {"vs_currency": "usd", "days": str(days), "interval": "daily"})
    if not js or "prices" not in js:
        raise RuntimeError("❌ S'ka historik për " + coin_id)
    df = pd.DataFrame(js["prices"], columns=["ts", "price"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df.set_index("ts", inplace=True)
    return df.dropna()

# ============ INDICATORS ============
def ema(s, span): return s.ewm(span=span, adjust=False).mean()

def rsi(s, period=14):
    delta = s.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    for i in range(period, len(s)):
        avg_gain.iat[i] = (avg_gain.iat[i-1]*(period-1)+gain.iat[i])/period
        avg_loss.iat[i] = (avg_loss.iat[i-1]*(period-1)+loss.iat[i])/period
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))

def macd(s, fast=12, slow=26, signal=9):
    macd_line = ema(s, fast) - ema(s, slow)
    sig = ema(macd_line, signal)
    return macd_line, sig, macd_line - sig

def bollinger(s, window=20, num_std=2):
    sma = s.rolling(window).mean()
    std = s.rolling(window).std()
    return sma, sma + num_std * std, sma - num_std * std

# ============ LOGJIKA ============
def score(p, rsi_v, e12, e26, m, ms, up, low):
    s = 0
    if pd.notna(rsi_v):
        if rsi_v < 30: s += 1
        elif rsi_v > 70: s -= 1
    if pd.notna(e12) and pd.notna(e26):
        s += 1 if e12 > e26 else -1
    if pd.notna(m) and pd.notna(ms):
        s += 2 if m > ms else -2
    if pd.notna(p) and pd.notna(up) and pd.notna(low):
        if p < low: s += 1
        elif p > up: s -= 1
    return s

def classify(s):
    if s >= 3: return "🟢 BLI"
    if s <= -3: return "🔴 SHIT"
    return "🟡 MBANJ"

def probs(s):
    if s >= 3: return 90, 10
    if s <= -3: return 10, 90
    scale = (s + 2) / 4
    b = 35 + scale * 30
    return round(b, 1), round(100 - b, 1)

# ============ ANALYZE ============
def analyze(coin, cid):
    print(f"📈 Analizë për {coin}")
    cur = get_current_price_row(cid)
    df = get_hist_df(cid)
    df["ema12"], df["ema26"] = ema(df["price"], 12), ema(df["price"], 26)
    df["rsi"] = rsi(df["price"])
    df["macd"], df["macd_sig"], _ = macd(df["price"])
    df["sma20"], df["bb_up"], df["bb_lo"] = bollinger(df["price"])
    last = df.iloc[-1]
    s = score(last["price"], last["rsi"], last["ema12"], last["ema26"],
              last["macd"], last["macd_sig"], last["bb_up"], last["bb_lo"])
    d = classify(s)
    pb, ps = probs(s)
    txt = f"{coin}: {d} | Çmim ${cur['current_price']:.6f} | BLI {pb}% / SHIT {ps}%"
    if last_signals.get(coin) != d:
        print("⚡ SINJAL I RI:", txt)
        last_signals[coin] = d
    else:
        print(txt)

# ============ LOOP ============
def run_once():
    print(f"\n🕒 Raund {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
    for coin, cid in COINS.items():
        try:
            analyze(coin, cid)
            time.sleep(2)
        except Exception as e:
            print(f"❌ Gabim tek {coin}: {e}")

if __name__ == "__main__":
    print("🚀 Start ElbuharBot debug mode…")
    run_once()
    while True:
        print("\n⏳ Prit 1 orë për raundin tjetër…")
        time.sleep(INTERVAL_SEC)
        run_once()