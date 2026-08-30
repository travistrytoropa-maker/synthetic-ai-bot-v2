from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import (
    get_active_symbols,
    get_tick,
    get_candles
)


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="2.2.0"
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
        "message": "Synthetic AI Signal Engine is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.get("/markets")
async def markets():

    try:
        symbols = await get_active_symbols()

        return {
            "status": "success",
            "count": len(symbols),
            "markets": symbols
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/tick/{symbol}")
async def tick(symbol: str):

    try:
        data = await get_tick(symbol.upper())

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/candles/{symbol}/{timeframe}")
async def candles(symbol: str, timeframe: str):

    timeframes = {
        "M5": 300,
        "M15": 900,
        "H1": 3600
    }

    timeframe = timeframe.upper()

    if timeframe not in timeframes:

        return {
            "status": "error",
            "message": "Timeframe must be M5, M15 or H1"
        }

    try:

        candles = await get_candles(
            symbol.upper(),
            timeframes[timeframe],
            100
        )

        cleaned = []

        for candle in candles:

            cleaned.append({
                "epoch": candle["epoch"],
                "open": candle["open"],
                "high": candle["high"],
                "low": candle["low"],
                "close": candle["close"]
            })

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "count": len(cleaned),
            "candles": cleaned
        }

    except Exception as e:

        return {
            "status": "error",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "message": str(e)
        }