from statistics import mean


# ============================================================
# PRO SYNTHETIC MARKET ANALYSIS ENGINE
# Version 1.0
#
# Purpose:
# - Multi-timeframe trend analysis
# - Market structure
# - Candle pattern detection
# - Momentum
# - Support/resistance
# - Confluence scoring
# - BUY / SELL / WAIT decision
#
# This engine DOES NOT place trades.
# ============================================================


MIN_CANDLES = 30


# ============================================================
# BASIC CANDLE FUNCTIONS
# ============================================================

def body(c):
    return abs(c["close"] - c["open"])


def candle_range(c):
    return max(c["high"] - c["low"], 1e-12)


def upper_wick(c):
    return c["high"] - max(c["open"], c["close"])


def lower_wick(c):
    return min(c["open"], c["close"]) - c["low"]


def bullish(c):
    return c["close"] > c["open"]


def bearish(c):
    return c["close"] < c["open"]


def body_ratio(c):
    return body(c) / candle_range(c)


# ============================================================
# CANDLE STRENGTH
# ============================================================

def candle_strength(c):

    ratio = body_ratio(c)

    if ratio >= 0.75:
        return "STRONG"

    if ratio >= 0.50:
        return "MODERATE"

    if ratio >= 0.25:
        return "WEAK"

    return "VERY_WEAK"


# ============================================================
# CANDLE PATTERNS
# ============================================================

def detect_patterns(candles):

    if len(candles) < 3:
        return []

    patterns = []

    current = candles[-1]
    previous = candles[-2]

    # --------------------------------------------------------
    # Bullish engulfing
    # --------------------------------------------------------

    if (
        bearish(previous)
        and bullish(current)
        and current["open"] <= previous["close"]
        and current["close"] >= previous["open"]
    ):
        patterns.append("BULLISH_ENGULFING")


    # --------------------------------------------------------
    # Bearish engulfing
    # --------------------------------------------------------

    if (
        bullish(previous)
        and bearish(current)
        and current["open"] >= previous["close"]
        and current["close"] <= previous["open"]
    ):
        patterns.append("BEARISH_ENGULFING")


    # --------------------------------------------------------
    # Pin bars
    # --------------------------------------------------------

    b = body(current)

    if (
        lower_wick(current) > b * 2
        and lower_wick(current) > upper_wick(current) * 1.5
    ):
        patterns.append("BULLISH_PIN_BAR")


    if (
        upper_wick(current) > b * 2
        and upper_wick(current) > lower_wick(current) * 1.5
    ):
        patterns.append("BEARISH_PIN_BAR")


    # --------------------------------------------------------
    # Inside bar
    # --------------------------------------------------------

    if (
        current["high"] <= previous["high"]
        and current["low"] >= previous["low"]
    ):
        patterns.append("INSIDE_BAR")


    # --------------------------------------------------------
    # Strong momentum candle
    # --------------------------------------------------------

    if (
        body_ratio(current) >= 0.75
    ):
        if bullish(current):
            patterns.append("STRONG_BULLISH_CANDLE")

        elif bearish(current):
            patterns.append("STRONG_BEARISH_CANDLE")


    return patterns


# ============================================================
# RECENT CANDLE MOMENTUM
# ============================================================

def momentum_analysis(candles):

    if len(candles) < 10:

        return {
            "direction": "UNKNOWN",
            "score": 50.0
        }


    recent = candles[-10:]

    bullish_count = 0
    bearish_count = 0

    strengths = []

    for c in recent:

        if bullish(c):
            bullish_count += 1

        elif bearish(c):
            bearish_count += 1

        strengths.append(
            body_ratio(c)
        )


    total = bullish_count + bearish_count

    if total == 0:

        return {
            "direction": "NEUTRAL",
            "score": 50.0
        }


    balance = (
        bullish_count - bearish_count
    ) / total


    strength = mean(strengths)


    score = 50 + (
        balance * 35
    ) + (
        strength * 15
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
        "score": round(score, 2),
        "bullish_candles": bullish_count,
        "bearish_candles": bearish_count,
        "average_body_strength": round(
            strength * 100,
            2
        )
    }


# ============================================================
# MARKET STRUCTURE
# ============================================================

def structure_analysis(candles):

    if len(candles) < 20:

        return {
            "structure": "UNKNOWN",
            "score": 50,
            "higher_high": False,
            "higher_low": False,
            "lower_high": False,
            "lower_low": False
        }


    recent = candles[-20:]

    first = recent[:10]
    second = recent[10:]


    first_high = max(
        c["high"] for c in first
    )

    second_high = max(
        c["high"] for c in second
    )


    first_low = min(
        c["low"] for c in first
    )

    second_low = min(
        c["low"] for c in second
    )


    higher_high = (
        second_high > first_high
    )

    higher_low = (
        second_low > first_low
    )

    lower_high = (
        second_high < first_high
    )

    lower_low = (
        second_low < first_low
    )


    if higher_high and higher_low:

        return {
            "structure": "BULLISH",
            "score": 85,
            "higher_high": True,
            "higher_low": True,
            "lower_high": False,
            "lower_low": False
        }


    if lower_high and lower_low:

        return {
            "structure": "BEARISH",
            "score": 15,
            "higher_high": False,
            "higher_low": False,
            "lower_high": True,
            "lower_low": True
        }


    return {
        "structure": "RANGING",
        "score": 50,
        "higher_high": higher_high,
        "higher_low": higher_low,
        "lower_high": lower_high,
        "lower_low": lower_low
    }


# ============================================================
# TREND ANALYSIS
# ============================================================

def trend_analysis(candles):

    if len(candles) < MIN_CANDLES:

        return {
            "direction": "UNKNOWN",
            "score": 50
        }


    recent = candles[-20:]

    bullish_count = sum(
        1 for c in recent
        if bullish(c)
    )

    bearish_count = sum(
        1 for c in recent
        if bearish(c)
    )


    difference = (
        bullish_count - bearish_count
    )


    score = 50 + (
        difference * 5
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


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def support_resistance(candles):

    if len(candles) < 20:

        return {
            "support": None,
            "resistance": None,
            "position": "UNKNOWN"
        }


    recent = candles[-20:]

    support = min(
        c["low"] for c in recent
    )

    resistance = max(
        c["high"] for c in recent
    )

    price = recent[-1]["close"]


    distance = resistance - support

    if distance <= 0:

        position = "UNKNOWN"

    else:

        relative = (
            price - support
        ) / distance

        if relative <= 0.25:
            position = "NEAR_SUPPORT"

        elif relative >= 0.75:
            position = "NEAR_RESISTANCE"

        else:
            position = "MID_RANGE"


    return {
        "support": support,
        "resistance": resistance,
        "current_price": price,
        "position": position
    }


# ============================================================
# BREAKOUT DETECTION
# ============================================================

def breakout_analysis(candles):

    if len(candles) < 21:

        return {
            "breakout": False,
            "direction": "NONE"
        }


    previous = candles[-21:-1]
    current = candles[-1]


    previous_high = max(
        c["high"] for c in previous
    )

    previous_low = min(
        c["low"] for c in previous
    )


    if current["close"] > previous_high:

        return {
            "breakout": True,
            "direction": "BULLISH"
        }


    if current["close"] < previous_low:

        return {
            "breakout": True,
            "direction": "BEARISH"
        }


    return {
        "breakout": False,
        "direction": "NONE"
    }


# ============================================================
# SINGLE TIMEFRAME PRO ANALYSIS
# ============================================================

def analyze_timeframe(candles, timeframe):

    if not isinstance(candles, list):

        return {
            "timeframe": timeframe,
            "status": "INVALID_DATA"
        }


    if len(candles) < MIN_CANDLES:

        return {
            "timeframe": timeframe,
            "status": "INSUFFICIENT_DATA",
            "candles": len(candles)
        }


    trend = trend_analysis(candles)

    structure = structure_analysis(candles)

    momentum = momentum_analysis(candles)

    patterns = detect_patterns(candles)

    levels = support_resistance(candles)

    breakout = breakout_analysis(candles)


    return {

        "timeframe": timeframe,

        "trend": trend,

        "structure": structure,

        "momentum": momentum,

        "patterns": patterns,

        "support_resistance": levels,

        "breakout": breakout,

        "last_price":
            candles[-1]["close"],

        "last_candle_strength":
            candle_strength(candles[-1])
    }


# ============================================================
# PRO MULTI-TIMEFRAME ENGINE
# ============================================================

def pro_analysis(m5, m15, h1):

    m5_result = analyze_timeframe(
        m5,
        "M5"
    )

    m15_result = analyze_timeframe(
        m15,
        "M15"
    )

    h1_result = analyze_timeframe(
        h1,
        "H1"
    )


    # --------------------------------------------------------
    # Extract scores
    # --------------------------------------------------------

    h1_score = h1_result.get(
        "trend",
        {}
    ).get(
        "score",
        50
    )

    m15_score = m15_result.get(
        "trend",
        {}
    ).get(
        "score",
        50
    )

    m5_score = m5_result.get(
        "trend",
        {}
    ).get(
        "score",
        50
    )


    # --------------------------------------------------------
    # Weighted trend
    #
    # H1  = 40%
    # M15 = 35%
    # M5  = 25%
    # --------------------------------------------------------

    trend_score = (
        h1_score * 0.40
        + m15_score * 0.35
        + m5_score * 0.25
    )


    # --------------------------------------------------------
    # Structure contribution
    # --------------------------------------------------------

    h1_structure = h1_result.get(
        "structure",
        {}
    ).get(
        "score",
        50
    )

    m15_structure = m15_result.get(
        "structure",
        {}
    ).get(
        "score",
        50
    )

    m5_structure = m5_result.get(
        "structure",
        {}
    ).get(
        "score",
        50
    )


    structure_score = (
        h1_structure * 0.40
        + m15_structure * 0.35
        + m5_structure * 0.25
    )


    # --------------------------------------------------------
    # Momentum contribution
    # --------------------------------------------------------

    h1_momentum = h1_result.get(
        "momentum",
        {}
    ).get(
        "score",
        50
    )

    m15_momentum = m15_result.get(
        "momentum",
        {}
    ).get(
        "score",
        50
    )

    m5_momentum = m5_result.get(
        "momentum",
        {}
    ).get(
        "score",
        50
    )


    momentum_score = (
        h1_momentum * 0.40
        + m15_momentum * 0.35
        + m5_momentum * 0.25
    )


    # --------------------------------------------------------
    # Overall confluence score
    # --------------------------------------------------------

    overall_score = (
        trend_score * 0.45
        + structure_score * 0.30
        + momentum_score * 0.25
    )


    overall_score = round(
        max(
            0,
            min(100, overall_score)
        ),
        2
    )


    # --------------------------------------------------------
    # Timeframe directions
    # --------------------------------------------------------

    h1_direction = h1_result.get(
        "trend",
        {}
    ).get(
        "direction",
        "UNKNOWN"
    )

    m15_direction = m15_result.get(
        "trend",
        {}
    ).get(
        "direction",
        "UNKNOWN"
    )

    m5_direction = m5_result.get(
        "trend",
        {}
    ).get(
        "direction",
        "UNKNOWN"
    )


    # --------------------------------------------------------
    # Alignment
    # --------------------------------------------------------

    bullish_alignment = (
        h1_direction == "BULLISH"
        and m15_direction == "BULLISH"
        and m5_direction == "BULLISH"
    )


    bearish_alignment = (
        h1_direction == "BEARISH"
        and m15_direction == "BEARISH"
        and m5_direction == "BEARISH"
    )


    # --------------------------------------------------------
    # Signal decision
    # --------------------------------------------------------

    signal = "WAIT"


    if (
        bullish_alignment
        and overall_score >= 70
    ):

        signal = "BUY"


    elif (
        bearish_alignment
        and overall_score <= 30
    ):

        signal = "SELL"


    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    if signal == "BUY":

        confidence = overall_score

    elif signal == "SELL":

        confidence = 100 - overall_score

    else:

        confidence = (
            100 - abs(
                overall_score - 50
            ) * 2
        )


    confidence = round(
        max(
            0,
            min(100, confidence)
        ),
        2
    )


    # --------------------------------------------------------
    # Setup quality
    # --------------------------------------------------------

    if signal in ("BUY", "SELL"):

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


    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {

        "engine": "PRO",

        "version": "1.0",

        "signal": signal,

        "confidence": confidence,

        "setup_quality": quality,

        "overall_score": overall_score,

        "trend_score":
            round(trend_score, 2),

        "structure_score":
            round(structure_score, 2),

        "momentum_score":
            round(momentum_score, 2),

        "timeframe_alignment": {

            "H1": h1_direction,

            "M15": m15_direction,

            "M5": m5_direction

        },

        "timeframes": {

            "H1": h1_result,

            "M15": m15_result,

            "M5": m5_result

        }

    }