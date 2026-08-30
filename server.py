from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import (
    get_active_symbols,
    get_tick,
    get_candles
)


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="2.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def home():

    return {
        "status": "online",
        "message": "Synthetic AI Signal Engine is running",
        "version": "2.1.0"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.get("/markets")
async def markets():

    try:

        markets = await get_active_symbols()

        return {
            "status": "success",
            "count": len(markets),
            "markets": markets
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


@app.get("/tick/{symbol}")
async def tick(symbol: str):

    try:

        result = await get_tick(
            symbol.upper()
        )

        return {
            "status": "success",
            "data": result
        }

    except Exception as error:

        return {
            "status": "error",
            "symbol": symbol.upper(),
            "message": str(error)
        }


@app.get("/candles/{symbol}/{timeframe}")
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
            "message": "Use M5, M15 or H1"
        }

    try:

        data = await get_candles(
            symbol=symbol.upper(),
            granularity=timeframes[timeframe],
            count=200
        )

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "count": len(data),
            "candles": data
        }

    except Exception as error:

        return {
            "status": "error",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "message": str(error)
        }