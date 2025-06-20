import asyncio
import websockets
import json
from datetime import datetime, timedelta

ohlc_bars = []
tick_data = {
    "last_price": None,
    "cumulative_tick": 0,
    "current_bar": {
        "open": 0,
        "high": 0,
        "low": 0,
        "close": 0,
        "start_time": None
    }
}

def get_ohlc_bars():
    return [
        {"time": "12:00", "open": 1, "high": 3, "low": 0, "close": 2},
        {"time": "12:15", "open": 2, "high": 4, "low": 1, "close": 3},
        {"time": "12:30", "open": 3, "high": 5, "low": 2, "close": 1}
    ]
def reset_bar():
    bar = tick_data["current_bar"]
    ohlc_bars.append({
        "time": bar["start_time"].strftime("%H:%M"),
        "open": bar["open"],
        "high": bar["high"],
        "low": bar["low"],
        "close": bar["close"]
    })
    tick_data["current_bar"] = {
        "open": tick_data["cumulative_tick"],
        "high": tick_data["cumulative_tick"],
        "low": tick_data["cumulative_tick"],
        "close": tick_data["cumulative_tick"],
        "start_time": datetime.utcnow()
    }

async def start_tick_tracking():
    uri = "wss://stream.binance.com:9443/ws/solusdt@trade"
    async with websockets.connect(uri) as websocket:
        tick_data["current_bar"]["start_time"] = datetime.utcnow()
        tick_data["current_bar"]["open"] = tick_data["cumulative_tick"]

        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            price = float(data["p"])

            last = tick_data["last_price"]
            if last is not None:
                if price > last:
                    tick_data["cumulative_tick"] += 1
                elif price < last:
                    tick_data["cumulative_tick"] -= 1

            tick_data["last_price"] = price
            current = tick_data["cumulative_tick"]
            bar = tick_data["current_bar"]

            bar["high"] = max(bar["high"], current)
            bar["low"] = min(bar["low"], current)
            bar["close"] = current

            # New 15-min bar?
            if datetime.utcnow() - bar["start_time"] >= timedelta(minutes=15):
                reset_bar()

            await asyncio.sleep(0.5)