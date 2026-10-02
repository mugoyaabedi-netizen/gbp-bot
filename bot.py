import requests, time, os
from datetime import datetime
from collections import deque
from flask import Flask
import threading
app = Flask(__name__)
prices = deque(maxlen=100)
def get_price():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/GBP", timeout=10).json()
        return float(r['rates']['USD'])
    except:
        return None
def rsi_calc(data, period=14):
    if len(data) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, period+1):
        diff = data[-i] - data[-i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))
    avg_g = sum(gains)/period if gains else 0.01
    avg_l = sum(losses)/period if losses else 0.01
    if avg_l == 0:
        return 70
    rs = avg_g / avg_l
    return round(100 - (100 / (1 + rs)), 2)
def ema_calc(data, period):
    if len(data) < period:
        return sum(data)/len(data)
    k = 2/(period+1)
    ema = sum(list(data)[:period])/period
    for p in list(data)[period:]:
        ema = p * k + ema * (1 - k)
    return ema
def bot_loop():
    while True:
        price = get_price()
        if price:
            prices.append(price)
            if len(prices) >= 30:
                p = list(prices)
                ema20 = ema_calc(p, 20)
                ema50 = ema_calc(p, 50)
                rsi = rsi_calc(p)
                print(f"P:{price} RSI:{rsi}")
        time.sleep(60)
@app.route('/')
def home():
    last = list(prices)[-1] if prices else 'waiting'
    return f"Bot running! {len(prices)}/30 Price: {last}"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
