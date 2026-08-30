import asyncio
import json
import websockets


DERIV_WS = "wss://api.derivws.com/trading/v1/options/ws/public"


TIMEFRAMES = {
    "M5": 300,
    "M15": 900,
    "H1": 3600
}


async def get_candles(symbol, timeframe, count=200):

    timeframe = timeframe.upper()

    if timeframe not in TIMEFRAMES:
        raise ValueError(
            "Timeframe must be M5, M15 or H1"
        )

    request = {
        "ticks_history": symbol,
        "style": "candles",
        "granularity": TIMEFRAMES[timeframe],
        "count": count,
        "end": "latest",
        "req_id": 1001
    }

    try:

        async with websockets.connect(
            DERIV_WS,
            origin=None,
            ping_interval=20,
            ping_timeout=20,
            open_timeout=30
        ) as websocket:

            await websocket.send(
                json.dumps(request)
            )

            while True:

                raw = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=30
                )

                data = json.loads(raw)

                if "error" in data:

                    raise RuntimeError(
                        data["error"].get(
                            "message",
                            "Deriv returned an error"
                        )
                    )

                if (
                    data.get("msg_type")
                    == "candles"
                ):

                    candles = []

                    for candle in data.get(
                        "candles",
                        []
                    ):

                        candles.append({
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

                    return candles

    except Exception as error:

        raise RuntimeError(
            f"Historical candle error: {error}"
        )


def candle_stats(candles):

    if not candles:
        return {}

    latest = candles[-1]

    bullish = 0
    bearish = 0

    for candle in candles:

        if candle["close"] > candle["open"]:
            bullish += 1

        elif candle["close"] < candle["open"]:
            bearish += 1

    return {
        "total": len(candles),
        "bullish": bullish,
        "bearish": bearish,
        "latest_close": latest["close"]
    }