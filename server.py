from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import get_active_symbols, get_tick


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="1.0.0"
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
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/tick/{symbol}")
async def tick(symbol: str):
    try:
        result = await get_tick(symbol.upper())

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No tick received"
            )

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )