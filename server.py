from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import (
    get_candles,
    candle_stats
)


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="6.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def home():

    return {
        "status": "online",
        "service": "Synthetic AI Signal Engine",
        "version": "6.0.0"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.get(
    "/candles/{symbol}/{timeframe}"
)
async def candles(
    symbol: str,
    timeframe: str
):

    timeframe = timeframe.upper()

    if timeframe not in [
        "M5",
        "M15",
        "H1"
    ]:

        return {
            "status": "error",
            "message":
                "Use M5, M15 or H1."
        }

    try:

        data = await get_candles(
            symbol.upper(),
            timeframe,
            200
        )

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "count": len(data),
            "candles": data,
            "statistics":
                candle_stats(data)
        }

    except Exception as error:

        return {
            "status": "error",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "message": str(error)
        }