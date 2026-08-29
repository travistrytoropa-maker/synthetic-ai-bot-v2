from deriv_api import get_candles


TIMEFRAMES = {
    "M5": 300,
    "M15": 900,
    "H1": 3600
}


def clean_candle(candle):
    return {
        "epoch": int(candle["epoch"]),
        "open": float(candle["open"]),
        "high": float(candle["high"]),
        "low": float(candle["low"]),
        "close": float(candle["close"])
    }


async def get_historical_candles(
    symbol,
    timeframe,
    count=500
):
    if timeframe not in TIMEFRAMES:
        raise ValueError(
            "Invalid timeframe. Use M5, M15 or H1."
        )

    granularity = TIMEFRAMES[timeframe]

    candles = await get_candles(
        symbol=symbol,
        granularity=granularity,
        count=count
    )

    return [
        clean_candle(candle)
        for candle in candles
    ]


async def get_multi_timeframe_data(
    symbol,
    count=500
):
    result = {}

    for timeframe in TIMEFRAMES:

        result[timeframe] = await get_historical_candles(
            symbol,
            timeframe,
            count
        )

    return result