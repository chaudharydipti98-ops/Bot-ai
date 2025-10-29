import requests, pandas as pd, pandas_ta as ta, time, math, os
from datetime import datetime

# ====== CONFIG ======
BOT_TOKEN = "your_telegram_bot_token"   # e.g. 1234567890:ABCdefGhijKlmnOpQRsTuVwxYZ
CHAT_ID = "your_chat_id"                # e.g. 123456789
SYMBOLS = ["DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "BONKUSDT", "FLOKIUSDT",
           "WIFUSDT", "BABYDOGEUSDT", "MEMEUSDT", "TURBOUSDT", "BRETTUSDT"]
INTERVAL = "5m"  # timeframe
RISK_REWARD = 1.5
LIMIT = 200

# ====== FUNCTIONS ======
def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram error:", e)

def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['time','o','h','l','c','v','x','qv','nt','tbv','tqv','ignore'])
    df = df.astype(float)
    df["close"] = df["c"]
    return df

def analyze(symbol):
    df = get_klines(symbol)
    df["ema20"] = ta.ema(df["close"], length=20)
    df["ema50"] = ta.ema(df["close"], length=50)
    df["rsi"] = ta.rsi(df["close"], length=14)
    df["atr"] = ta.atr(df["h"], df["l"], df["c"], length=14)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None
    if last["ema20"] > last["ema50"] and last["rsi"] > 55 and last["close"] > prev["close"]:
        signal = "BUY"
    elif last["ema20"] < last["ema50"] and last["rsi"] < 45 and last["close"] < prev["close"]:
        signal = "SELL"

    if signal:
        entry = last["close"]
        sl = entry - last["atr"] if signal == "BUY" else entry + last["atr"]
        tp = entry + (last["atr"] * RISK_REWARD) if signal == "BUY" else entry - (last["atr"] * RISK_REWARD)
        msg = (f"📊 {symbol}\n"
               f"Signal: {signal}\n"
               f"Entry: {entry:.6f}\n"
               f"TP: {tp:.6f}\n"
               f"SL: {sl:.6f}\n"
               f"RSI: {last['rsi']:.2f}\n"
               f"ATR: {last['atr']:.4f}\n"
               f"Time: {datetime.utcnow().strftime('%H:%M:%S')} UTC")
        send_telegram(msg)
        print(msg)

def run():
    while True:
        for s in SYMBOLS:
            analyze(s)
        time.sleep(300)  # runs every 5 minutes

if __name__ == "__main__":
    send_telegram("🚀 MemeCoin Signal Bot Started!")
    run()
