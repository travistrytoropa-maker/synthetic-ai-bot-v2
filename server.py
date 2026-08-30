from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import deriv


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="4.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup():

    try:
        await deriv.connect()
        print("DERIV CONNECTION: CONNECTED")

    except Exception as error:

        print(
            "DERIV CONNECTION FAILED:",
            error
        )


@app.on_event("shutdown")
async def shutdown():

    await deriv.close()


@app.get("/")
async def home():

    return {
        "status": "online",
        "service": "Synthetic AI Signal Engine",
        "version": "4.0.0"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "deriv_connected": deriv.connected,
        "deriv_error": deriv.last_error
    }


@app.get("/deriv-status")
async def deriv_status():

    return {
        "connected": deriv.connected,
        "error": deriv.last_error
    }


@app.get("/markets")
async def markets():

    try:

        response = await deriv.active_symbols()

        symbols = response.get(
            "active_symbols",
            []
        )

        cleaned = []

        for item in symbols:

            cleaned.append({
                "symbol": item.get(
                    "underlying_symbol"
                ),

                "name": item.get(
                    "underlying_symbol_name"
                ),

                "type": item.get(
                    "underlying_symbol_type"
                ),

                "market": item.get(
                    "market"
                ),

                "submarket": item.get(
                    "submarket"
                )
            })

        return {
            "status": "success",
            "count": len(cleaned),
            "markets": cleaned
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


@app.get("/tick/{symbol}")
async def tick(symbol: str):

    try:

        response = await deriv.tick(
            symbol.upper()
        )

        tick_data = response.get(
            "tick"
        )

        if not tick_data:

            return {
                "status": "error",
                "message": "No tick data returned"
            }

        return {
            "status": "success",
            "data": {
                "symbol": tick_data.get(
                    "symbol"
                ),
                "price": tick_data.get(
                    "quote"
                ),
                "epoch": tick_data.get(
                    "epoch"
                )
            }
        }

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

    timeframes = {
        "M5": 300,
        "M15": 900,
        "H1": 3600
    }

    timeframe = timeframe.upper()

    if timeframe not in timeframes:

        return {
            "status": "error",
            "message": (
                "Invalid timeframe. "
                "Use M5, M15 or H1."
            )
        }

    try:

        response = await deriv.candles(
            symbol.upper(),
            timeframes[timeframe],
            100
        )

        candles_data = response.get(
            "candles",
            []
        )

        cleaned = []

        for candle in candles_data:

            cleaned.append({
                "epoch": candle.get(
                    "epoch"
                ),
                "open": candle.get(
                    "open"
                ),
                "high": candle.get(
                    "high"
                ),
                "low": candle.get(
                    "low"
                ),
                "close": candle.get(
                    "close"
                )
            })

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "count": len(cleaned),
            "candles": cleaned
        }

    except Exception as error:

        return {
            "status": "error",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "message": str(error)
        }