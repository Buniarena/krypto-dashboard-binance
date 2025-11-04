# main.py  — ElbuharBot (auto every 1h, no external TA libs)
import time
import math
import requests
import pandas as pd
from datetime import datetime, timezone

# =============== SETTINGS ===============

BOT_TOKEN = "7627051456:AAHTTyUyP9i4ug3MUo63zmeeA3Uq61ByKKg"   # Telegram bot token
CHAT_ID   = "7274463074"                                        # your chat id
INTERVAL_SEC = 3600                                             # 1 hour

COINS = {  # name -> coingecko id
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "PEPE": "pepe",
    "Shiba": "shiba-inu",
    "XVG (Verge)": "verge"
}

HIST_DAYS = 60      # historical window
TIMEOUT   = 15      # HTTP timeout seconds
MAX_RETRY = 5       # retries for HTTP

# ============ HELPER: HTTP with retry/backoff ============

def http_get_json(url, params=None):
    delay = 1
    for attempt in range(1, MAX_RETRY + 1):
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            # Too many requests or server errors -> backoff
            if r.status_code in (429, 500, 502, 503, 504):
                print(f"⏳ HTTP {r.status_code} retry {attempt}/{MAX_RETRY} after {delay}s …")
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            # other client error -> break
            print("❌ HTTP error:", r.status_code, r.text[:200])
            return None
        except Exception as e:
            print(f"❌ Network error (attempt {attempt}): {e}")
            time.sleep(delay)
            delay = min(delay * 2, 30)
    return None

# ============ TELEGRAM ============

def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        if r.status_code != 200:
            print("❌ Telegram:", r.status_code, r.text[:200])
        else:
            print("✅ Telegram dërguar:", text.splitlines()[0])
    except Exception as e:
        print("❌ Telegram exception:", e)

# Quick test at start
def tg_selftest():
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=TIMEOUT)
    ok = (r.status_code == 200 and r.json().get("ok"))
    print("🤖 getMe:", r.status_code, r.text[:120])
    if not ok:
        print("⚠️ Kontrollo BOT_TOKEN-in!")
    return ok

# ============ DATA (CoinGecko) ============

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
    df = df.dropna()
    return df

# ============ INDICATORS (no external TA) ============

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    # Wilder smoothing
    for i in range(period, len(series)):
        avg_gain.iat[i] = (avg_gain.iat[i-1]*(period-1) + gain.iat[i]) / period
        avg_loss.iat[i] = (avg_loss.iat[i-1]*(period-1) + loss.iat[i]) / period
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def bollinger(series: pd.Series, window=20, num_std=2):
    sma = series.rolling(window=window, min_periods=window).mean()
    std = series.rolling(window=window, min_periods=window).std()
    upper = sma + num_std*std
    lower = sma - num_std*std
    return sma, upper, lower

# ============ SIGNAL LOGIC ============

def score_row(p, rsi_v, ema12, ema26, macd_v, macd_sig, upper, lower):
    s = 0
    if pd.notna(rsi_v):
        if rsi_v < 30: s += 1
        elif rsi_v > 70: s -= 1
    if pd.notna(ema12) and pd.notna(ema26):
        s += 1 if ema12 > ema26 else -1
    if pd.notna(macd_v) and pd.notna(macd_sig):
        s += 2 if macd_v > macd_sig else -2
    if pd.notna(upper) and pd.notna(lower) and pd.notna(p):
        if p < lower: s += 1
        elif p > upper: s -= 1
    return s

def classify(s):
    if s >= 3: return "🟢 BLI"
    if s <= -3: return "🔴 SHIT"
    return "🟡 MBANJ"

def probs(s):
    # deterministic mapping to avoid randomness on servers
    if s >= 3:
        return 90.0, 10.0
    if s <= -3:
        return 10.0, 90.0
    # map -2..2 to 35..65
    scale = (s + 2) / 4  # 0..1
    buy = 35 + scale * 30  # 35..65
    sell = 100 - buy
    return round(buy,1), round(sell,1)

# ============ ANALYZE & SEND ============

def analyze_and_message(name, coin_id):
    cur = get_current_price_row(coin_id)
    df = get_hist_df(coin_id)

    df["ema12"] = ema(df["price"], 12)
    df["ema26"] = ema(df["price"], 26)
    df["rsi"]   = rsi(df["price"], 14)
    df["macd"], df["macd_sig"], df["macd_hist"] = macd(df["price"])
    df["sma20"], df["bb_up"], df["bb_lo"] = bollinger(df["price"], 20, 2)

    last = df.iloc[-1]
    s = score_row(
        p=last["price"],
        rsi_v=last["rsi"],
        ema12=last["ema12"],
        ema26=last["ema26"],
        macd_v=last["macd"],
        macd_sig=last["macd_sig"],
        upper=last["bb_up"],
        lower=last["bb_lo"]
    )
    decision = classify(s)
    pb, ps = probs(s)
    price_txt = f"${cur['current_price']:.6f}"

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    msg = (
        f"🚨 *{name}* – *{decision}*\n"
        f"💵 Çmimi: {price_txt}\n"
        f"📊 Prob: *BLI* {pb:.1f}% | *SHIT* {ps:.1f}%\n"
        f"⏱️ {ts}"
    )
    tg_send(msg)

# ============ MAIN LOOP ============

if __name__ == "__main__":
    print("🚀 Start ElbuharBot …")
    tg_selftest()
    tg_send("🤖 Bot aktiv! Do dërgoj sinjal tani dhe pastaj çdo 1 orë.")

    def one_round():
        print(f"🕒 Raund {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
        for name, cid in COINS.items():
            try:
                analyze_and_message(name, cid)
                time.sleep(3)  # pak pauzë midis mesazheve
            except Exception as e:
                print(f"❌ {name}:", e)

    # Dërgo menjëherë një raund
    one_round()
    # Pastaj çdo 1 orë
    while True:
        print("⏳ Prit 1 orë …")
        time.sleep(INTERVAL_SEC)
        one_round()