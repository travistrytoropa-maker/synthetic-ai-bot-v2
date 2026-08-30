from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import (
    get_active_symbols,
    get_tick,
    get_candles
)


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="5.0.0"
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
        "version": "5.0.0"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.get("/markets")
async def markets():

    try:

        data = await get_active_symbols()

        return {
            "status": "success",
            "data": data
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


@app.get("/tick/{symbol}")
async def tick(symbol: str):

    try:

        data = await get_tick(
            symbol.upper()
        )

        return data

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


@app.get(
    "/candles/{symbol}/{timeframe}"
)
async def candles(
    symbol: str,
    timeframe: str
):

    timeframe = timeframe.upper()

    timeframes = {
        "M5": 300,
        "M15": 900,
        "H1": 3600
    }

    if timeframe not in timeframes:

        return {
            "status": "error",
            "message": "Use M5, M15 or H1."
        }


    try:

        data = await get_candles(
            symbol.upper(),
            timeframes[timeframe],
            100
        )

        return data

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }