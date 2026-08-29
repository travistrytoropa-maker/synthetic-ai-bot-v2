import json
import websockets

DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3"


async def get_active_symbols():
    async with websockets.connect(DERIV_WS_URL) as ws:
        await ws.send(json.dumps({
            "active_symbols": "brief",
            "req_id": 1
        }))

        while True:
            message = json.loads(await ws.recv())

            if message.get("msg_type") == "active_symbols":
                return message.get("active_symbols", [])

            if "error" in message:
                raise RuntimeError(message["error"].get("message", "Deriv API error"))


async def get_tick(symbol):
    async with websockets.connect(DERIV_WS_URL) as ws:
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
                raise RuntimeError(message["error"].get("message", "Deriv API error"))