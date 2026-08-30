from deriv_api import get_candles
from analysis_engine import multi_timeframe_analysis


def clean_candles(data):
    """
    Make sure the analysis engine receives:
    [
        {
            "epoch": ...,
            "open": ...,
            "high": ...,
            "low": ...,
            "close": ...
        }
    ]
    """

    if not isinstance(data, list):
        raise ValueError(
            f"Expected candle list, got {type(data).__name__}"
        )

    cleaned = []

    for candle in data:

        if not isinstance(candle, dict):
            continue

        required = [
            "epoch",
            "open",
            "high",
            "low",
            "close"
        ]

        if not all(
            key in candle
            for key in required
        ):
            continue

        try:

            cleaned.append({
                "epoch": int(candle["epoch"]),
                "open": float(candle["open"]),
                "high": float(candle["high"]),
                "low": float(candle["low"]),
                "close": float(candle["close"])
            })

        except (ValueError, TypeError):
            continue

    if len(cleaned) < 30:
        raise ValueError(
            f"Only {len(cleaned)} valid candles received. "
            "At least 30 are required."
        )

    return cleaned


async def analyze_market(symbol: str):

    symbol = symbol.upper()

    print(
        f"Starting analysis for {symbol}"
    )


    # --------------------------------------------------------
    # Download historical candles
    # --------------------------------------------------------

    raw_m5 = await get_candles(
        symbol,
        "M5",
        200
    )

    raw_m15 = await get_candles(
        symbol,
        "M15",
        200
    )

    raw_h1 = await get_candles(
        symbol,
        "H1",
        200
    )


    # --------------------------------------------------------
    # Normalize candle data
    # --------------------------------------------------------

    m5 = clean_candles(
        raw_m5
    )

    m15 = clean_candles(
        raw_m15
    )

    h1 = clean_candles(
        raw_h1
    )


    print(
        f"{symbol}: "
        f"M5={len(m5)}, "
        f"M15={len(m15)}, "
        f"H1={len(h1)}"
    )


    # --------------------------------------------------------
    # Run AI analysis
    # --------------------------------------------------------

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