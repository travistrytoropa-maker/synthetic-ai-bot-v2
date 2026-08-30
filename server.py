from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import (
    get_markets,
    get_candles
)

from market_analyzer import (
    analyze_market
)

from market_scanner import (
    scan_markets
)


app = FastAPI(
    title="Synthetic AI Engine",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"]
)


@app.get("/")
async def root():

    return {
        "status": "online",
        "service":
            "Synthetic AI Engine"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.get("/markets")
async def markets():

    try:

        data = await get_markets()

        return {
            "status": "success",
            "count": len(data),
            "markets": data
        }

    except Exception as error:

        return {
            "status": "error",
            "error_type":
                type(error).__name__,
            "message": str(error)
        }


@app.get("/candles/{symbol}/{timeframe}")
async def candles(
    symbol: str,
    timeframe: str
):

    try:

        data = await get_candles(
            symbol,
            timeframe.upper(),
            200
        )

        return {
            "status": "success",
            "symbol":
                symbol.upper(),
            "timeframe":
                timeframe.upper(),
            "count": len(data),
            "candles": data
        }

    except Exception as error:

        return {
            "status": "error",
            "error_type":
                type(error).__name__,
            "message": str(error)
        }


@app.get("/analyze-market/{symbol}")
async def analyze_market_endpoint(
    symbol: str
):

    try:

        result = await analyze_market(
            symbol
        )

        return {
            "status": "success",
            "result": result
        }

    except Exception as error:

        return {
            "status": "error",
            "symbol":
                symbol.upper(),
            "error_type":
                type(error).__name__,
            "message": str(error)
        }


@app.post("/scan-markets")
async def scan_markets_endpoint(
    payload: dict
):

    try:

        markets = payload.get(
            "markets",
            []
        )

        if not isinstance(
            markets,
            list
        ):

            return {
                "status": "error",
                "message":
                    "markets must be a list"
            }

        results = await scan_markets(
            markets
        )

        return {
            "status": "success",
            "count": len(results),
            "markets": results
        }

    except Exception as error:

        return {
            "status": "error",
            "error_type":
                type(error).__name__,
            "message": str(error)
        }