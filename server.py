from market_analyzer import analyze_market
from analysis_engine import multi_timeframe_analysis
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
@app.post("/analyze")
async def analyze_market(payload: dict):

    try:

        m5 = payload.get(
            "M5",
            []
        )

        m15 = payload.get(
            "M15",
            []
        )

        h1 = payload.get(
            "H1",
            []
        )


        result = multi_timeframe_analysis(
            m5,
            m15,
            h1
        )


        return {
            "status": "success",
            "analysis": result
        }


    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }
@app.get("/analyze-test")
async def analyze_test():

    candles = []

    price = 100.0

    for i in range(50):

        candles.append({
            "epoch": i,
            "open": price,
            "high": price + 1.0,
            "low": price - 0.3,
            "close": price + 0.8
        })

        price += 0.8


    result = multi_timeframe_analysis(
        candles,
        candles,
        candles
    )


    return {
        "status": "success",
        "test": True,
        "analysis": result
    }