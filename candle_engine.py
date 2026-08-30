from deriv_api import get_candles


TIMEFRAMES = {
    "M5": 300,
    "M15": 900,
    "H1": 3600
}


def clean_candle(candle):

    try:

        return {
            "epoch": int(candle.get("epoch", 0)),
            "open": float(candle.get("open", 0)),
            "high": float(candle.get("high", 0)),
            "low": float(candle.get("low", 0)),
            "close": float(candle.get("close", 0))
        }

    except (TypeError, ValueError):

        return None


async def get_historical_candles(
    symbol,
    timeframe,
    count=200
):

    timeframe = timeframe.upper()

    if timeframe not in TIMEFRAMES:

        raise ValueError(
            "Invalid timeframe. Use M5, M15 or H1."
        )

    symbol = symbol.upper()

    granularity = TIMEFRAMES[timeframe]

    raw_candles = await get_candles(
        symbol=symbol,
        granularity=granularity,
        count=count
    )

    cleaned_candles = []

    for candle in raw_candles:

        cleaned = clean_candle(candle)

        if cleaned is not None:

            cleaned_candles.append(cleaned)

    if not cleaned_candles:

        raise RuntimeError(
            f"Could not process candles for {symbol}"
        )

    return cleaned_candles


async def get_multi_timeframe_data(
    symbol,
    count=200
):

    result = {}

    for timeframe in TIMEFRAMES:

        try:

            candles = await get_historical_candles(
                symbol=symbol,
                timeframe=timeframe,
                count=count
            )

            result[timeframe] = {
                "status": "success",
                "count": len(candles),
                "candles": candles
            }

        except Exception as error:

            result[timeframe] = {
                "status": "error",
                "message": str(error),
                "count": 0,
                "candles": []
            }

    return result