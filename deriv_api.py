import json
import websockets

DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3"


async def connect():
    return await websockets.connect(
        DERIV_WS_URL,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10
    )


async def get_active_symbols():
    ws = await connect()

    try:
        await ws.send(json.dumps({
            "active_symbols": "brief",
            "req_id": 1
        }))

        while True:
            message = json.loads(await ws.recv())

            if message.get("msg_type") == "active_symbols":
                return message.get("active_symbols", [])

            if "error" in message:
                raise RuntimeError(
                    message["error"].get(
                        "message",
                        "Deriv API error"
                    )
                )

    finally:
        await ws.close()


async def get_tick(symbol):
    ws = await connect()

    try:
        await ws.send(json.dumps({
            "ticks": symbol,
            "subscribe": 0,
            "req_id": 2
        }))

        while True:
            message = json.loads(await ws.recv())

            if message.get("msg_type") == "tick":
                tick = message["tick"]

                return {
                    "symbol": tick.get("symbol"),
                    "price": tick.get("quote"),
                    "epoch": tick.get("epoch")
                }

            if "error" in message:
                raise RuntimeError(
                    message["error"].get(
                        "message",
                        "Deriv API error"
                    )
                )

    finally:
        await ws.close()


async def get_candles(symbol, granularity, count=500):
    ws = await connect()

    try:
        request = {
            "ticks_history": symbol,
            "style": "candles",
            "granularity": granularity,
            "count": count,
            "end": "latest",
            "req_id": 10
        }

        await ws.send(json.dumps(request))

        while True:
            message = json.loads(await ws.recv())

            if message.get("msg_type") == "candles":
                return message.get("candles", [])

            if "error" in message:
                raise RuntimeError(
                    message["error"].get(
                        "message",
                        "Deriv candle API error"
                    )
                )

    finally:
        await ws.close()