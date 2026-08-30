def calculate_sma(values, period):

    if len(values) < period:
        return None

    return sum(
        values[-period:]
    ) / period


def analyze(candles):

    if not isinstance(candles, list):
        raise ValueError("Candles must be a list")

    if len(candles) < 20:
        raise ValueError(
            "At least 20 candles are required"
        )

    closes = []

    for candle in candles:

        if not isinstance(candle, dict):
            continue

        closes.append(
            float(candle["close"])
        )

    if len(closes) < 20:
        raise ValueError(
            "Not enough valid candles"
        )

    sma10 = calculate_sma(
        closes,
        10
    )

    sma20 = calculate_sma(
        closes,
        20
    )

    price = closes[-1]

    if sma10 > sma20:
        trend = "BULLISH"

    elif sma10 < sma20:
        trend = "BEARISH"

    else:
        trend = "NEUTRAL"

    return {
        "price": price,
        "sma10": sma10,
        "sma20": sma20,
        "trend": trend
    }


def multi_timeframe_analysis(
    m5,
    m15,
    h1
):

    result_m5 = analyze(m5)
    result_m15 = analyze(m15)
    result_h1 = analyze(h1)

    directions = [
        result_m5["trend"],
        result_m15["trend"],
        result_h1["trend"]
    ]

    bullish = directions.count(
        "BULLISH"
    )

    bearish = directions.count(
        "BEARISH"
    )

    if bullish == 3:

        signal = "BUY"

    elif bearish == 3:

        signal = "SELL"

    else:

        signal = "WAIT"

    return {
        "signal": signal,

        "M5": result_m5,

        "M15": result_m15,

        "H1": result_h1,

        "alignment": (
            bullish == 3
            or bearish == 3
        )
    }