from deriv_api import get_candles
from analysis_engine import multi_timeframe_analysis


async def analyze_market(symbol: str):

    symbol = symbol.upper()

    # Get the three timeframes independently.
    m5 = await get_candles(
        symbol,
        "M5",
        200
    )

    m15 = await get_candles(
        symbol,
        "M15",
        200
    )

    h1 = await get_candles(
        symbol,
        "H1",
        200
    )

    # Run the historical analysis engine.
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