import json
import websockets

DERIV_URL = "wss://ws.binaryws.com/websockets/v3"


async def request_deriv(payload):
    try:
        async with websockets.connect(
            DERIV_URL,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=10
        ) as ws:

            await ws.send(json.dumps(payload))

            while True:
                message = json.loads(await ws.recv())

                if "error" in message:
                    error = message["error"]
                    raise RuntimeError(
                        error.get("message", "Deriv API error")
                    )

                return message

    except Exception as e:
        raise RuntimeError(
            f"Deriv connection error: {str(e)}"
        )


async def get_active_symbols():

    response = await request_deriv({
        "active_symbols": "brief",
        "product_type": "basic",
        "req_id": 1
    })

    symbols = response.get("active_symbols")

    if symbols is None:
        raise RuntimeError(
            "Deriv did not return active_symbols"
        )

    return symbols


async def get_tick(symbol):

    response = await request_deriv({
        "ticks": symbol,
        "subscribe": 0,
        "req_id": 2
    })

    tick = response.get("tick")

    if tick is None:
        raise RuntimeError(
            f"Deriv did not return a tick for {symbol}"
        )

    return {
        "symbol": tick.get("symbol"),
        "price": tick.get("quote"),
        "epoch": tick.get("epoch")
    }


async def get_candles(symbol, granularity, count=100):

    response = await request_deriv({
        "ticks_history": symbol,
        "style": "candles",
        "granularity": granularity,
        "count": count,
        "end": "latest",
        "req_id": 3
    })

    candles = response.get("candles")

    if candles is None:
        raise RuntimeError(
            f"Deriv did not return candles for {symbol}"
        )

    return candles