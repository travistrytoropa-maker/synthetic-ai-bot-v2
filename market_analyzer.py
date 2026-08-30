from deriv_api import get_candles
from analysis_engine import multi_timeframe_analysis


def normalize_candles(data):

    # Some API wrappers return:
    # {"candles": [...]}
    if isinstance(data, dict):
        data = data.get("candles", data)

    if not isinstance(data, list):
        raise ValueError(
            f"Candle response must be a list, "
            f"but received {type(data).__name__}: {str(data)[:300]}"
        )

    result = []

    for item in data:

        # Normal dictionary format
        if isinstance(item, dict):

            try:
                result.append({
                    "epoch": int(item["epoch"]),
                    "open": float(item["open"]),
                    "high": float(item["high"]),
                    "low": float(item["low"]),
                    "close": float(item["close"])
                })

            except (KeyError, TypeError, ValueError):
                continue

        # Array format:
        # [epoch, open, high, low, close]
        elif isinstance(item, (list, tuple)):

            if len(item) >= 5:

                try:
                    result.append({
                        "epoch": int(item[0]),
                        "open": float(item[1]),
                        "high": float(item[2]),
                        "low": float(item[3]),
                        "close": float(item[4])
                    })

                except (TypeError, ValueError):
                    continue

    if len(result) < 30:
        raise ValueError(
            f"Only {len(result)} valid candles were received."
        )

    return result


async def analyze_market(symbol: str):

    symbol = symbol.upper()

    # Get historical data
    raw_m5 = await get_candles(symbol, "M5", 200)
    raw_m15 = await get_candles(symbol, "M15", 200)
    raw_h1 = await get_candles(symbol, "H1", 200)

    # Normalize everything
    m5 = normalize_candles(raw_m5)
    m15 = normalize_candles(raw_m15)
    h1 = normalize_candles(raw_h1)

    # Run analysis
    analysis = multi_timeframe_analysis(
        m5,
        m15,
        h1
    )

    return {
        "symbol": symbol,
        "candles": {
            "M5": len(m5),
            "M15": len(m15),
            "H1": len(h1)
        },
        "analysis": analysis
    }