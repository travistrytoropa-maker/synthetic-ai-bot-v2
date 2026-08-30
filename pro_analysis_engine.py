from statistics import mean


MIN_CANDLES = 30


def body(c):
    return abs(
        c["close"] - c["open"]
    )


def candle_range(c):
    return max(
        c["high"] - c["low"],
        0.00000001
    )


def upper_wick(c):
    return (
        c["high"]
        - max(c["open"], c["close"])
    )


def lower_wick(c):
    return (
        min(c["open"], c["close"])
        - c["low"]
    )


def bullish(c):
    return c["close"] > c["open"]


def bearish(c):
    return c["close"] < c["open"]


def body_ratio(c):

    return body(c) / candle_range(c)


def trend(candles):

    recent = candles[-20:]

    bullish_count = sum(
        bullish(c)
        for c in recent
    )

    bearish_count = sum(
        bearish(c)
        for c in recent
    )

    score = 50 + (
        (bullish_count - bearish_count)
        * 5
    )

    score = max(
        0,
        min(100, score)
    )

    if score >= 60:
        direction = "BULLISH"

    elif score <= 40:
        direction = "BEARISH"

    else:
        direction = "RANGING"

    return {
        "direction": direction,
        "score": round(score, 2),
        "bullish_candles": bullish_count,
        "bearish_candles": bearish_count
    }


def momentum(candles):

    recent = candles[-10:]

    scores = []

    for candle in recent:

        direction = (
            1 if bullish(candle)
            else -1
            if bearish(candle)
            else 0
        )

        strength = body_ratio(
            candle
        )

        scores.append(
            direction * strength
        )

    value = mean(scores)

    score = 50 + (
        value * 50
    )

    score = max(
        0,
        min(100, score)
    )

    if score >= 60:
        direction = "BULLISH"

    elif score <= 40:
        direction = "BEARISH"

    else:
        direction = "NEUTRAL"

    return {
        "direction": direction,
        "score": round(score, 2)
    }


def structure(candles):

    recent = candles[-20:]

    first = recent[:10]
    second = recent[10:]

    high1 = max(
        c["high"] for c in first
    )

    high2 = max(
        c["high"] for c in second
    )

    low1 = min(
        c["low"] for c in first
    )

    low2 = min(
        c["low"] for c in second
    )

    if (
        high2 > high1
        and low2 > low1
    ):

        return {
            "direction": "BULLISH",
            "score": 85,
            "pattern": "HIGHER_HIGH_HIGHER_LOW"
        }

    if (
        high2 < high1
        and low2 < low1
    ):

        return {
            "direction": "BEARISH",
            "score": 15,
            "pattern": "LOWER_HIGH_LOWER_LOW"
        }

    return {
        "direction": "RANGING",
        "score": 50,
        "pattern": "MIXED_STRUCTURE"
    }


def candle_patterns(candles):

    patterns = []

    if len(candles) < 2:
        return patterns

    current = candles[-1]
    previous = candles[-2]

    if (
        bearish(previous)
        and bullish(current)
        and current["open"]
        <= previous["close"]
        and current["close"]
        >= previous["open"]
    ):

        patterns.append(
            "BULLISH_ENGULFING"
        )

    if (
        bullish(previous)
        and bearish(current)
        and current["open"]
        >= previous["close"]
        and current["close"]
        <= previous["open"]
    ):

        patterns.append(
            "BEARISH_ENGULFING"
        )

    if (
        lower_wick(current)
        > body(current) * 2
    ):

        patterns.append(
            "BULLISH_REJECTION"
        )

    if (
        upper_wick(current)
        > body(current) * 2
    ):

        patterns.append(
            "BEARISH_REJECTION"
        )

    return patterns


def support_resistance(candles):

    recent = candles[-20:]

    support = min(
        c["low"] for c in recent
    )

    resistance = max(
        c["high"] for c in recent
    )

    price = recent[-1]["close"]

    return {
        "support": support,
        "resistance": resistance,
        "price": price
    }


def analyze_timeframe(
    candles,
    timeframe
):

    if not isinstance(candles, list):

        raise ValueError(
            f"{timeframe}: candles must be a list"
        )

    if len(candles) < MIN_CANDLES:

        raise ValueError(
            f"{timeframe}: insufficient candles"
        )

    return {
        "timeframe": timeframe,

        "trend": trend(candles),

        "momentum": momentum(
            candles
        ),

        "structure": structure(
            candles
        ),

        "patterns": candle_patterns(
            candles
        ),

        "levels": support_resistance(
            candles
        ),

        "price": candles[-1]["close"]
    }


def pro_analysis(
    m5,
    m15,
    h1
):

    a5 = analyze_timeframe(
        m5,
        "M5"
    )

    a15 = analyze_timeframe(
        m15,
        "M15"
    )

    a1 = analyze_timeframe(
        h1,
        "H1"
    )

    trend_score = (
        a1["trend"]["score"] * 0.40
        + a15["trend"]["score"] * 0.35
        + a5["trend"]["score"] * 0.25
    )

    structure_score = (
        a1["structure"]["score"] * 0.40
        + a15["structure"]["score"] * 0.35
        + a5["structure"]["score"] * 0.25
    )

    momentum_score = (
        a1["momentum"]["score"] * 0.40
        + a15["momentum"]["score"] * 0.35
        + a5["momentum"]["score"] * 0.25
    )

    overall = (
        trend_score * 0.45
        + structure_score * 0.30
        + momentum_score * 0.25
    )

    overall = round(
        max(0, min(100, overall)),
        2
    )

    directions = [
        a1["trend"]["direction"],
        a15["trend"]["direction"],
        a5["trend"]["direction"]
    ]

    if all(
        x == "BULLISH"
        for x in directions
    ) and overall >= 70:

        signal = "BUY"

        confidence = overall

    elif all(
        x == "BEARISH"
        for x in directions
    ) and overall <= 30:

        signal = "SELL"

        confidence = 100 - overall

    else:

        signal = "WAIT"

        confidence = (
            100
            - abs(overall - 50) * 2
        )

    confidence = round(
        max(0, min(100, confidence)),
        2
    )

    if signal == "BUY" or signal == "SELL":

        if confidence >= 85:
            quality = "A+"

        elif confidence >= 75:
            quality = "A"

        elif confidence >= 70:
            quality = "B"

        else:
            quality = "C"

    else:

        quality = "NO_TRADE"

    return {
        "engine": "PRO",
        "version": "1.0",

        "signal": signal,

        "confidence": confidence,

        "setup_quality": quality,

        "overall_score": overall,

        "trend_score": round(
            trend_score,
            2
        ),

        "structure_score": round(
            structure_score,
            2
        ),

        "momentum_score": round(
            momentum_score,
            2
        ),

        "timeframe_alignment": {
            "H1": directions[0],
            "M15": directions[1],
            "M5": directions[2]
        },

        "timeframes": {
            "H1": a1,
            "M15": a15,
            "M5": a5
        }
    }