import json
import websockets

DERIV_WS_URL = (
    "wss://ws.derivws.com/websockets/v3"
    "?app_id=1089"
)

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
    ) as websocket:

        await websocket.send(
            json.dumps(request)
        )

        while True:

            raw = await websocket.recv()

            data = json.loads(raw)

            if "error" in data:

                error = data["error"]

                if isinstance(error, dict):
                    message = error.get(
                        "message",
                        "Deriv API error"
                    )
                else:
                    message = str(error)

                raise RuntimeError(message)

            if data.get("msg_type") == "ping":
                continue

            return data


async def get_markets():

    response = await deriv_request({
        "active_symbols": "full"
    })

    print(
        "DERIV RAW MARKET RESPONSE:",
        repr(response),
        flush=True
    )

    symbols = response.get(
        "active_symbols"
    )

    if symbols is None:

        return {
            "_diagnostic": True,
            "raw_response": response
        }

    if not isinstance(symbols, list):

        return {
            "_diagnostic": True,
            "raw_response": response,
            "reason":
                "active_symbols is not a list"
        }

    markets = []

    for item in symbols:

        if not isinstance(item, dict):
            continue

        # Try every likely symbol field.
        symbol = (
            item.get("underlying_symbol")
            or item.get("symbol")
            or item.get("underlying")
            or item.get("display_symbol")
        )

        name = (
            item.get("underlying_symbol_name")
            or item.get("display_name")
            or item.get("name")
            or item.get("symbol_name")
            or symbol
        )

        if symbol:

            markets.append({
                "symbol": str(symbol),
                "name": str(name),
                "market": str(
                    item.get("market", "")
                ),
                "submarket": str(
                    item.get("submarket", "")
                )
            })

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
            TIMEFRAME_SECONDS[timeframe],

        "count": int(count),

        "end": "latest"

    })

    candles = response.get(
        "candles",
        []
    )

    if not isinstance(candles, list):

        raise RuntimeError(
            "Invalid candle response"
        )

    result = []

    for candle in candles:

        if not isinstance(candle, dict):
            continue

        try:

            result.append({
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

    if not result:

        raise RuntimeError(
            "No valid candles returned for "
            + symbol
            + " "
            + timeframe
        )

    return result


async def test_connection():

    response = await deriv_request({
        "time": 1
    })

    return {
        "connected": True,
        "server_time":
            response.get("time")
    }