import json
import websockets


DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"


TIMEFRAME_SECONDS = {
    "M5": 300,
    "M15": 900,
    "H1": 3600
}


async def deriv_request(request):

    async with websockets.connect(
        DERIV_WS_URL,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10
    ) as ws:

        await ws.send(json.dumps(request))

        while True:

            message = await ws.recv()

            data = json.loads(message)

            if "error" in data:

                error = data["error"]

                if isinstance(error, dict):

                    raise RuntimeError(
                        error.get(
                            "message",
                            "Deriv API error"
                        )
                    )

                raise RuntimeError(
                    str(error)
                )

            if data.get("msg_type") == "ping":
                continue

            return data

async def get_markets():

    response = await deriv_request({
        "active_symbols": "full",
        "product_type": "basic"
    })

    print("===== DERIV MARKET RESPONSE =====")
    print(response)
    print("=================================")

    symbols = response.get("active_symbols")

    if symbols is None:

        raise RuntimeError(
            "Deriv response does not contain active_symbols"
        )

    if not isinstance(symbols, list):

        raise RuntimeError(
            "active_symbols is not a list. "
            + str(type(symbols))
        )

    markets = []

    for item in symbols:

        if not isinstance(item, dict):
            continue

        symbol = item.get("symbol")

        if not symbol:
            continue

        name = (
            item.get("display_name")
            or item.get("name")
            or symbol
        )

        markets.append({
            "symbol": str(symbol),
            "name": str(name)
        })

    print(
        "DERIV SYMBOLS FOUND:",
        len(markets)
    )

    return markets

async def get_candles(
    symbol,
    timeframe="M5",
    count=200
):

    symbol = str(symbol).strip()

    timeframe = str(
        timeframe
    ).upper()

    if timeframe not in TIMEFRAME_SECONDS:

        raise ValueError(
            "Unsupported timeframe: "
            + timeframe
        )

    response = await deriv_request({

        "ticks_history": symbol,

        "style": "candles",

        "granularity":
            TIMEFRAME_SECONDS[
                timeframe
            ],

        "count": int(count),

        "end": "latest"

    })

    candles = response.get(
        "candles"
    )

    if not isinstance(candles, list):

        raise RuntimeError(
            "Deriv returned no candle list"
        )

    result = []

    for item in candles:

        if not isinstance(item, dict):
            continue

        try:

            result.append({

                "epoch": int(
                    item["epoch"]
                ),

                "open": float(
                    item["open"]
                ),

                "high": float(
                    item["high"]
                ),

                "low": float(
                    item["low"]
                ),

                "close": float(
                    item["close"]
                )

            })

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            continue

    if not result:

        raise RuntimeError(
            "No valid candles returned for "
            + symbol
            + " "
            + timeframe
        )

    return result