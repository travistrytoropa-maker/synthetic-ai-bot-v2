from deriv_api import get_candles
from pro_analysis_engine import pro_analysis


async def scan_market(symbol: str):

    symbol = symbol.upper()

    m5 = await get_candles(symbol, "M5", 200)
    m15 = await get_candles(symbol, "M15", 200)
    h1 = await get_candles(symbol, "H1", 200)

    result = pro_analysis(
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
        "analysis": result
    }