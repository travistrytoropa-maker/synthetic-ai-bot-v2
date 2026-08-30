import asyncio
import json
import websockets


DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"


TIMEFRAME_SECONDS = {
    "M5": 300,
    "M15": 900,
    "H1": 3600
}


async def deriv_request(request):
    """
    Send one request to Deriv and return the response.
    """

    async with websockets.connect(
        DERIV_WS_URL,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10
    ) as websocket:

        await websocket.send(
            json.dumps(request)
        )

        while True:

            raw = await websocket.recv()

            data = json.loads(raw)

            if "error" in data:

                raise RuntimeError(
                    data["error"].get(
                        "message",
                        "Deriv API error"
                    )
                )

            if data.get("msg_type") == "ping":
                continue

            return data


async def get_markets():

    response = await deriv_request({
        "active_symbols": "brief",
        "product_type": "basic"
    })

    markets = []

    symbols = response.get(
        "active_symbols",
        []
    )

    for item in symbols:

        if not isinstance(item, dict):
            continue

        symbol = item.get("symbol")

        name = (
            item.get("display_name")
            or item.get("name")
            or symbol
        )

        if not symbol:
            continue

        markets.append({
            "symbol": symbol,
            "name": name
        })

    return markets


async def get_candles(
    symbol,
    timeframe="M5",
    count=200
):

    timeframe = timeframe.upper()

    if timeframe not in TIMEFRAME_SECONDS:

        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    granularity = TIMEFRAME_SECONDS[
        timeframe
    ]

    response = await deriv_request({

        "ticks_history": symbol,

        "style": "candles",

        "granularity": granularity,

        "count": int(count),

        "end": "latest"

    })

    candles = response.get(
        "candles",
        []
    )

    if not isinstance(candles, list):

        raise ValueError(
            "Deriv returned invalid candle data"
        )

    normalized = []

    for candle in candles:

        if not isinstance(candle, dict):
            continue

        try:

            normalized.append({
                "epoch": int(
                    candle["epoch"]
                ),

                "open": float(
                    candle["open"]
                ),

                "high": float(
                    candle["high"]
                ),

                "low": float(
                    candle["low"]
                ),

                "close": float(
                    candle["close"]
                )
            })

        except (
            KeyError,
            TypeError,
            ValueError
        ):
            continue

    if len(normalized) == 0:

        raise ValueError(
            f"No candles returned for {symbol} {timeframe}"
        )

    return normalized