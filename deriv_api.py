import json
import websockets


# ============================================================
# DERIV API CONNECTION
# ============================================================

DERIV_WS_URL = (
    "wss://ws.derivws.com/websockets/v3"
    "?app_id=1089"
)


# ============================================================
# SUPPORTED TIMEFRAMES
# ============================================================

TIMEFRAME_SECONDS = {
    "M5": 300,
    "M15": 900,
    "H1": 3600
}


# ============================================================
# DERIV REQUEST
# ============================================================

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

            raw_message = await websocket.recv()

            data = json.loads(raw_message)

            # --------------------------------------------
            # Deriv API error
            # --------------------------------------------

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

            # --------------------------------------------
            # Ignore ping messages
            # --------------------------------------------

            if data.get("msg_type") == "ping":
                continue

            return data


# ============================================================
# MARKET DISCOVERY
# ============================================================

async def get_markets():

    response = await deriv_request({

        "active_symbols": "brief"

    })

    symbols = response.get(
        "active_symbols",
        []
    )

    if not isinstance(symbols, list):

        raise RuntimeError(
            "Deriv returned an invalid active_symbols response"
        )

    markets = []

    for item in symbols:

        if not isinstance(item, dict):
            continue

        # ----------------------------------------------------
        # Support current Deriv format AND older format
        # ----------------------------------------------------

        symbol = (
            item.get("underlying_symbol")
            or item.get("symbol")
        )

        name = (
            item.get("underlying_symbol_name")
            or item.get("display_name")
            or item.get("name")
            or symbol
        )

        if not symbol:
            continue

        market = item.get(
            "market",
            ""
        )

        submarket = item.get(
            "submarket",
            ""
        )

        symbol_type = (
            item.get("underlying_symbol_type")
            or item.get("symbol_type")
            or ""
        )

        markets.append({

            "symbol": str(symbol),

            "name": str(name),

            "market": str(market),

            "submarket": str(submarket),

            "type": str(symbol_type)

        })

    return markets


# ============================================================
# CANDLE DATA
# ============================================================

async def get_candles(
    symbol,
    timeframe="M5",
    count=200
):

    symbol = str(
        symbol
    ).strip()

    timeframe = str(
        timeframe
    ).upper()

    # --------------------------------------------------------
    # Check timeframe
    # --------------------------------------------------------

    if timeframe not in TIMEFRAME_SECONDS:

        raise ValueError(
            "Unsupported timeframe: "
            + timeframe
        )

    granularity = TIMEFRAME_SECONDS[
        timeframe
    ]

    # --------------------------------------------------------
    # Request candles
    # --------------------------------------------------------

    response = await deriv_request({

        "ticks_history": symbol,

        "style": "candles",

        "granularity": granularity,

        "count": int(count),

        "end": "latest"

    })

    # --------------------------------------------------------
    # Get candles
    # --------------------------------------------------------

    candles = response.get(
        "candles",
        []
    )

    if not isinstance(candles, list):

        raise RuntimeError(
            "Deriv returned an invalid candle response for "
            + symbol
            + " "
            + timeframe
        )

    normalized = []

    # --------------------------------------------------------
    # Normalize candles
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Make sure we actually received candles
    # --------------------------------------------------------

    if not normalized:

        raise RuntimeError(
            "No valid candles returned for "
            + symbol
            + " "
            + timeframe
        )

    return normalized


# ============================================================
# TEST DERIV CONNECTION
# ============================================================

async def test_connection():

    response = await deriv_request({

        "time": 1

    })

    return {

        "connected": True,

        "server_time":
            response.get(
                "time"
            )

    }