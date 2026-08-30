import json
import websockets

DERIV_URL = "wss://ws.binaryws.com/websockets/v3"


async def deriv_request(request):
    try:
        async with websockets.connect(
            DERIV_URL,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=10
        ) as ws:

            await ws.send(json.dumps(request))

            while True:
                raw = await ws.recv()
                response = json.loads(raw)

                if "error" in response:
                    error = response["error"]

                    raise RuntimeError(
                        error.get(
                            "message",
                            "Unknown Deriv API error"
                        )
                    )

                return response

    except Exception as error:
        raise RuntimeError(
            f"Deriv connection error: {error}"
        )


async def get_active_symbols():

    response = await deriv_request({
        "active_symbols": "brief",
        "req_id": 1
    })

    symbols = response.get(
        "active_symbols",
        []
    )

    result = []

    for item in symbols:

        symbol = item.get(
            "underlying_symbol"
        )

        name = item.get(
            "underlying_symbol_name"
        )

        if symbol:

            result.append({
                "symbol": symbol,
                "name": name,
                "type": item.get(
                    "underlying_symbol_type"
                ),
                "market": item.get(
                    "market"
                ),
                "submarket": item.get(
                    "submarket"
                )
            })

    return result


async def get_tick(symbol):

    response = await deriv_request({
        "ticks": symbol,
        "subscribe": 0,
        "req_id": 2
    })

    tick = response.get("tick")

    if not tick:
        raise RuntimeError(
            f"No tick returned for {symbol}"
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

    response = await deriv_request({
        "ticks_history": symbol,
        "end": "latest",
        "count": count,
        "style": "candles",
        "granularity": granularity,
        "req_id": 3
    })

    candles = response.get(
        "candles",
        []
    )

    if not candles:

        raise RuntimeError(
            f"No candles returned for {symbol}"
        )

    return [
        {
            "epoch": int(candle["epoch"]),
            "open": float(candle["open"]),
            "high": float(candle["high"]),
            "low": float(candle["low"]),
            "close": float(candle["close"])
        }
        for candle in candles
    ]