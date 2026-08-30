from deriv_api import get_candles
from pro_analysis_engine import pro_analysis


async def scan_single_market(symbol: str, name: str = ""):

    symbol = symbol.upper()

    try:
        m5 = await get_candles(symbol, "M5", 200)
        m15 = await get_candles(symbol, "M15", 200)
        h1 = await get_candles(symbol, "H1", 200)

        analysis = pro_analysis(
            m5,
            m15,
            h1
        )

        return {
            "status": "success",
            "name": name,
            "symbol": symbol,
            "candles": {
                "M5": len(m5),
                "M15": len(m15),
                "H1": len(h1)
            },
            "signal": analysis["signal"],
            "confidence": analysis["confidence"],
            "setup_quality": analysis["setup_quality"],
            "overall_score": analysis["overall_score"],
            "trend_score": analysis["trend_score"],
            "structure_score": analysis["structure_score"],
            "momentum_score": analysis["momentum_score"],
            "timeframe_alignment": analysis["timeframe_alignment"],
            "analysis": analysis
        }

    except Exception as error:

        return {
            "status": "error",
            "name": name,
            "symbol": symbol,
            "error_type": type(error).__name__,
            "message": str(error)
        }


async def scan_markets(markets):

    results = []

    for market in markets:

        if isinstance(market, dict):

            symbol = market.get("symbol")
            name = market.get(
                "name",
                symbol
            )

        else:

            symbol = str(market)
            name = symbol

        if not symbol:
            continue

        result = await scan_single_market(
            symbol,
            name
        )

        results.append(result)

    # Put successful analyses first.
    successful = [
        r for r in results
        if r.get("status") == "success"
    ]

    failed = [
        r for r in results
        if r.get("status") != "success"
    ]

    successful.sort(
        key=lambda x: x.get(
            "confidence",
            0
        ),
        reverse=True
    )

    return successful + failed