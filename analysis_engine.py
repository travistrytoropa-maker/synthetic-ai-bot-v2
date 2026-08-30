from statistics import mean


# ============================================================
# SYNTHETIC AI ANALYSIS ENGINE
# ============================================================

MIN_CANDLES = 30


def candle_direction(candle):
    if candle["close"] > candle["open"]:
        return "BULLISH"

    if candle["close"] < candle["open"]:
        return "BEARISH"

    return "NEUTRAL"


def candle_body(candle):
    return abs(
        candle["close"] - candle["open"]
    )


def candle_range(candle):
    return max(
        candle["high"] - candle["low"],
        0.00000001
    )


def body_strength(candle):

    return (
        candle_body(candle)
        / candle_range(candle)
    )


# ============================================================
# CANDLE PATTERNS
# ============================================================

def detect_patterns(candles):

    if len(candles) < 3:
        return []

    patterns = []

    previous = candles[-2]
    current = candles[-1]


    # --------------------------------------------------------
    # Bullish engulfing
    # --------------------------------------------------------

    if (
        previous["close"] < previous["open"]
        and current["close"] > current["open"]
        and current["open"] <= previous["close"]
        and current["close"] >= previous["open"]
    ):

        patterns.append(
            "BULLISH_ENGULFING"
        )


    # --------------------------------------------------------
    # Bearish engulfing
    # --------------------------------------------------------

    if (
        previous["close"] > previous["open"]
        and current["close"] < current["open"]
        and current["open"] >= previous["close"]
        and current["close"] <= previous["open"]
    ):

        patterns.append(
            "BEARISH_ENGULFING"
        )


    # --------------------------------------------------------
    # Pin bars
    # --------------------------------------------------------

    body = candle_body(current)
    rng = candle_range(current)

    upper_wick = (
        current["high"]
        - max(
            current["open"],
            current["close"]
        )
    )

    lower_wick = (
        min(
            current["open"],
            current["close"]
        )
        - current["low"]
    )


    if (
        lower_wick > body * 2
        and lower_wick > upper_wick * 1.5
        and rng > 0
    ):

        patterns.append(
            "BULLISH_PIN_BAR"
        )


    if (
        upper_wick > body * 2
        and upper_wick > lower_wick * 1.5
        and rng > 0
    ):

        patterns.append(
            "BEARISH_PIN_BAR"
        )


    # --------------------------------------------------------
    # Inside bar
    # --------------------------------------------------------

    if (
        current["high"] <= previous["high"]
        and current["low"] >= previous["low"]
    ):

        patterns.append(
            "INSIDE_BAR"
        )


    return patterns


# ============================================================
# MOMENTUM
# ============================================================

def momentum_score(candles):

    if len(candles) < 10:
        return 50.0


    recent = candles[-10:]

    bullish = 0
    bearish = 0
    strengths = []


    for candle in recent:

        direction = candle_direction(
            candle
        )

        if direction == "BULLISH":
            bullish += 1

        elif direction == "BEARISH":
            bearish += 1

        strengths.append(
            body_strength(candle)
        )


    total = bullish + bearish

    if total == 0:
        return 50.0


    directional_balance = (
        bullish - bearish
    ) / total


    average_strength = mean(
        strengths
    )


    score = 50 + (
        directional_balance * 35
    )


    score += (
        average_strength * 15
    )


    return round(
        max(0, min(100, score)),
        2
    )


# ============================================================
# MARKET STRUCTURE
# ============================================================

def structure_analysis(candles):

    if len(candles) < 10:

        return {
            "structure": "UNKNOWN",
            "score": 50
        }


    recent = candles[-10:]


    midpoint = len(recent) // 2

    first_half = recent[:midpoint]
    second_half = recent[midpoint:]


    first_high = max(
        c["high"]
        for c in first_half
    )

    second_high = max(
        c["high"]
        for c in second_half
    )


    first_low = min(
        c["low"]
        for c in first_half
    )

    second_low = min(
        c["low"]
        for c in second_half
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
            "score": 80
        }


    if lower_high and lower_low:

        return {
            "structure": "BEARISH",
            "score": 20
        }


    return {
        "structure": "RANGING",
        "score": 50
    }


# ============================================================
# TREND
# ============================================================

def trend_analysis(candles):

    if len(candles) < MIN_CANDLES:

        return {
            "trend": "INSUFFICIENT_DATA",
            "score": 50
        }


    recent = candles[-20:]


    bullish = 0
    bearish = 0


    for candle in recent:

        direction = candle_direction(
            candle
        )

        if direction == "BULLISH":
            bullish += 1

        elif direction == "BEARISH":
            bearish += 1


    if bullish > bearish:

        difference = (
            bullish - bearish
        )

        score = min(
            100,
            50 + difference * 5
        )

        return {
            "trend": "BULLISH",
            "score": score
        }


    if bearish > bullish:

        difference = (
            bearish - bullish
        )

        score = max(
            0,
            50 - difference * 5
        )

        return {
            "trend": "BEARISH",
            "score": score
        }


    return {
        "trend": "RANGING",
        "score": 50
    }


# ============================================================
# SINGLE TIMEFRAME ANALYSIS
# ============================================================

def analyze_timeframe(
    candles,
    timeframe
):

    if not candles:

        return {
            "timeframe": timeframe,
            "trend": "NO_DATA",
            "trend_score": 50,
            "momentum_score": 50,
            "structure": "UNKNOWN",
            "structure_score": 50,
            "patterns": []
        }


    trend = trend_analysis(
        candles
    )

    momentum = momentum_score(
        candles
    )

    structure = structure_analysis(
        candles
    )

    patterns = detect_patterns(
        candles
    )


    return {
        "timeframe": timeframe,

        "trend":
            trend["trend"],

        "trend_score":
            trend["score"],

        "momentum_score":
            momentum,

        "structure":
            structure["structure"],

        "structure_score":
            structure["score"],

        "patterns":
            patterns
    }


# ============================================================
# MULTI-TIMEFRAME ENGINE
# ============================================================

def multi_timeframe_analysis(
    m5,
    m15,
    h1
):

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
    # Weighted trend
    #
    # H1 = 40%
    # M15 = 35%
    # M5 = 25%
    # --------------------------------------------------------

    weighted_score = (
        h1_result["trend_score"] * 0.40
        + m15_result["trend_score"] * 0.35
        + m5_result["trend_score"] * 0.25
    )


    # --------------------------------------------------------
    # Signal direction
    # --------------------------------------------------------

    if weighted_score >= 65:

        direction = "BUY"

    elif weighted_score <= 35:

        direction = "SELL"

    else:

        direction = "WAIT"


    # --------------------------------------------------------
    # Pattern confirmation
    # --------------------------------------------------------

    bullish_patterns = {
        "BULLISH_ENGULFING",
        "BULLISH_PIN_BAR"
    }

    bearish_patterns = {
        "BEARISH_ENGULFING",
        "BEARISH_PIN_BAR"
    }


    bullish_confirmation = 0
    bearish_confirmation = 0


    for result in [
        m5_result,
        m15_result,
        h1_result
    ]:

        for pattern in result["patterns"]:

            if pattern in bullish_patterns:

                bullish_confirmation += 1

            if pattern in bearish_patterns:

                bearish_confirmation += 1


    # --------------------------------------------------------
    # Final confidence
    # --------------------------------------------------------

    confidence = abs(
        weighted_score - 50
    ) * 2


    if direction == "BUY":

        confidence += (
            bullish_confirmation * 3
        )


    elif direction == "SELL":

        confidence += (
            bearish_confirmation * 3
        )


    confidence = round(
        max(0, min(100, confidence)),
        2
    )


    # --------------------------------------------------------
    # Safety filter
    #
    # We don't want a trade signal simply
    # because one timeframe looks good.
    # --------------------------------------------------------

    aligned = (
        m5_result["trend"]
        == m15_result["trend"]
        == h1_result["trend"]
    )


    if not aligned:

        direction = "WAIT"

        confidence = min(
            confidence,
            60
        )


    return {

        "signal":
            direction,

        "confidence":
            confidence,

        "timeframes": {

            "M5":
                m5_result,

            "M15":
                m15_result,

            "H1":
                h1_result
        },

        "weighted_trend_score":
            round(
                weighted_score,
                2
            ),

        "bullish_pattern_count":
            bullish_confirmation,

        "bearish_pattern_count":
            bearish_confirmation,

        "timeframes_aligned":
            aligned
    }