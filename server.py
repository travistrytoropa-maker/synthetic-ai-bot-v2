from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import get_active_symbols, get_tick
from candle_engine import (
    get_historical_candles,
    get_multi_timeframe_data
)


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():

    return {
        "status": "online",
        "message": "Synthetic AI Signal Engine is running",
        "version": "2.0.0"
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

    except Exception as error:

        return {
            "status": "error",
            "message": str(error),
            "markets": []
        }


@app.get("/tick/{symbol}")
async def tick(symbol: str):

    try:

        data = await get_tick(
            symbol.upper()
        )

        return {
            "status": "success",
            "data": data
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

    try:

        data = await get_historical_candles(
            symbol=symbol.upper(),
            timeframe=timeframe.upper(),
            count=200
        )

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframe": timeframe.upper(),
            "count": len(data),
            "candles": data
        }

    except Exception as error:

        return {
            "status": "error",
            "symbol": symbol.upper(),
            "timeframe": timeframe.upper(),
            "message": str(error),
            "count": 0,
            "candles": []
        }


@app.get("/analysis-data/{symbol}")
async def analysis_data(
    symbol: str
):

    try:

        data = await get_multi_timeframe_data(
            symbol=symbol.upper(),
            count=200
        )

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframes": data
        }

    except Exception as error:

        return {
            "status": "error",
            "symbol": symbol.upper(),
            "message": str(error)
        }