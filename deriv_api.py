import json
import asyncio
import websockets


DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3"


async def connect_deriv():
    try:
        websocket = await websockets.connect(
            DERIV_WS_URL,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=10,
            open_timeout=20
        )

        return websocket

    except Exception as error:
        raise RuntimeError(
            f"Could not connect to Deriv: {str(error)}"
        )


async def send_request(request):
    websocket = None

    try:
        websocket = await connect_deriv()

        await websocket.send(
            json.dumps(request)
        )

        while True:

            response = await asyncio.wait_for(
                websocket.recv(),
                timeout=30
            )

            data = json.loads(response)

            if "error" in data:

                error_message = data["error"].get(
                    "message",
                    "Unknown Deriv API error"
                )

                raise RuntimeError(error_message)

            return data

    except asyncio.TimeoutError:

        raise RuntimeError(
            "Deriv request timed out"
        )

    except Exception as error:

        raise RuntimeError(str(error))

    finally:

        if websocket is not None:

            try:
                await websocket.close()

            except Exception:
                pass


async def get_active_symbols():

    data = await send_request({
        "active_symbols": "brief",
        "req_id": 1
    })

    return data.get(
        "active_symbols",
        []
    )


async def get_tick(symbol):

    data = await send_request({
        "ticks": symbol,
        "subscribe": 0,
        "req_id": 2
    })

    tick = data.get("tick")

    if not tick:

        raise RuntimeError(
            f"No tick data received for {symbol}"
        )

    return {
        "symbol": tick.get("symbol"),
        "price": tick.get("quote"),
        "epoch": tick.get("epoch")
    }


async def get_candles(
    symbol,
    granularity,
    count=200
):

    if count < 10:
        count = 10

    if count > 1000:
        count = 1000

    data = await send_request({
        "ticks_history": symbol,
        "style": "candles",
        "granularity": granularity,
        "count": count,
        "end": "latest",
        "req_id": 3
    })

    candles = data.get("candles", [])

    if not candles:

        raise RuntimeError(
            f"No candle data received for {symbol}"
        )

    return candles