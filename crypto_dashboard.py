# main.py — ElbuharBot (pa Telegram, me sinjale të reja në çdo refresh)

import time
import requests
import pandas as pd
from datetime import datetime, timezone

# =============== SETTINGS ===============

INTERVAL_SEC = 3600  # çdo 1 orë
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

# ruan sinjalet e fundit
last_signals = {}

# ============ HTTP me retry/backoff ============

def http_get_json(url, params=None):
    delay = 1
    for attempt in range(1, MAX_RETRY + 1):
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                print(f"⏳ HTTP {r.status_code} retry {attempt}/{MAX_RETRY} pas {delay}s …")
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            print("❌ HTTP error:", r.status_code, r.text[:200])
            return None
        except Exception as e:
            print(f"❌ Network error (attempt {attempt}): {e}")
            time.sleep(delay)
            delay = min(delay * 2, 30)
    return None

# ============ COINGECKO DATA ============

def get_current_price_row(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    js = http_get_json(url, {"vs_currency": "usd", "ids": coin_id})
    if not js:
        raise RuntimeError("S'ka current data")
    return js[0]

def get_hist_df(coin_id, days=HIST_DAYS):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    js = http_get_json(url, {"vs_currency":"usd", "days": str(days), "interval": "daily"})
    if not js or "prices" not in js:
        raise RuntimeError("S'ka historik")
    df = pd.DataFrame(js["prices"], columns=["ts", "price"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df.set_index("ts", inplace=True)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return df.dropna()

# ============ INDICATORS (pa libra të jashtëm) ============

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    for i in range(period, len(series)):
        avg_gain.iat[i] = (avg_gain.iat[i-1]*(period-1) + gain.iat[i]) / period
        avg_loss.iat[i] = (avg_loss.iat[i-1]*(period-1) + loss.iat[i]) / period
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))

def macd(series, fast=12, slow=26, signal=9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line, macd_line - signal_line

def bollinger(series, window=20, num_std=2):
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    return sma, sma + num_std * std, sma - num_std * std

# ============ LOGJIKA E SINJALEVE ============

def score_row(p, rsi_v, ema12, ema26, macd_v, macd_sig, upper, lower):
    s = 0
    if pd.notna(rsi_v):
        if rsi_v < 30: s += 1
        elif rsi_v > 70: s -= 1
    if pd.notna(ema12) and pd.notna(ema26):
        s += 1 if ema12 > ema26 else -1
    if pd.notna(macd_v) and pd.notna(macd_sig):
        s += 2 if macd_v > macd_sig else -2
    if pd.notna(p) and pd.notna(upper) and pd.notna(lower):
        if p < lower: s += 1
        elif p > upper: s -= 1
    return s

def classify(s):
    if s >= 3: return "🟢 BLI"
    if s <= -3: return "🔴 SHIT"
    return "🟡 MBANJ"

def probs(s):
    if s >= 3: return 90.0, 10.0
    if s <= -3: return 10.0, 90.0
    scale = (s + 2) / 4
    buy = 35 + scale * 30
    return round(buy, 1), round(100 - buy, 1)

# ============ ANALIZIMI DHE PRINTIMI ============

def analyze_and_print(name, coin_id):
    cur = get_current_price_row(coin_id)
    df = get_hist_df(coin_id)
    df["ema12"] = ema(df["price"], 12)
    df["ema26"] = ema(df["price"], 26)
    df["rsi"] = rsi(df["price"])
    df["macd"], df["macd_sig"], df["macd_hist"] = macd(df["price"])
    df["sma20"], df["bb_up"], df["bb_lo"] = bollinger(df["price"])

    last = df.iloc[-1]
    s = score_row(
        last["price"], last["rsi"], last["ema12"], last["ema26"],
        last["macd"], last["macd_sig"], last["bb_up"], last["bb_lo"]
    )
    decision = classify(s)
    pb, ps = probs(s)
    price_txt = f"${cur['current_price']:.6f}"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    msg = f"\n🚨 {name} – {decision}\n💵 {price_txt}\n📊 BLI {pb:.1f}% | SHIT {ps:.1f}%\n⏱️ {ts}"

    # kontrollo nëse ka ndryshim nga hera e fundit
    old = last_signals.get(name)
    if old != decision:
        print("⚡ SINJAL I RI!", msg)
        last_signals[name] = decision
    else:
        print(msg)

# ============ MAIN LOOP ============

if __name__ == "__main__":
    print("🚀 Start ElbuharBot (auto refresh çdo orë)…")

    def one_round():
        print(f"\n🕒 Raund {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
        for name, cid in COINS.items():
            try:
                analyze_and_print(name, cid)
                time.sleep(3)
            except Exception as e:
                print(f"❌ {name}:", e)

    # Raundi i parë
    one_round()

    # Përsërit çdo orë
    while True:
        print("\n⏳ Prit për raundin tjetër...")
        time.sleep(INTERVAL_SEC)
        one_round()