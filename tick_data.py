import asyncio
from datetime import datetime
import httpx

ohlc_bars = []

# Helper to convert to 15-min intervals
def get_15min_key():
    now = datetime.utcnow()
    minute_block = (now.minute // 15) * 15
    return now.replace(minute=minute_block, second=0, microsecond=0)

# Main polling + TICK calculation logic
async def start_tick_tracking():
    print("Polling Binance API every 2 seconds...")

    last_price = None
    current_tick_bar = {"open": 0, "high": 0, "low": 0, "close": 0}
    current_bar_key = get_15min_key()

    while True:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get("https://api.binance.com/api/v3/trades?symbol=SOLUSDT&limit=50")
                trades = r.json()

            for trade in trades:
                price = float(trade["price"])
                new_key = get_15min_key()

                if new_key != current_bar_key:
                    # New 15-min bar
                    current_tick_bar["close"] = current_tick_bar["open"] + current_tick_bar["high"] + current_tick_bar["low"]
                    ohlc_bars.append({
                        "time": current_bar_key.strftime("%H:%M"),
                        **current_tick_bar
                    })
                    if len(ohlc_bars) > 20:
                        ohlc_bars.pop(0)
                    current_tick_bar = {"open": 0, "high": 0, "low": 0, "close": 0}
                    current_bar_key = new_key
                    last_price = None

                if last_price is not None:
                    tick = 1 if price > last_price else -1 if price < last_price else 0
                    current_tick_bar["high"] = max(current_tick_bar["high"], tick)
                    current_tick_bar["low"] = min(current_tick_bar["low"], tick)
                    current_tick_bar["open"] += tick  # Cumulative tick

                last_price = price

        except Exception as e:
            print("Polling error:", e)

        await asyncio.sleep(2)

def get_ohlc_bars():
    return ohlc_bars