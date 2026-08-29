import json
import websockets

DERIV_WS_URL = "wss://api.derivws.com/trading/v1/options/ws/public"


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