from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from deriv_api import deriv_connection_info


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="5.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def home():
    return FileResponse("index.html")


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.get("/deriv")
async def deriv():
    return deriv_connection_info()


@app.get("/markets")
async def markets():
    return {
        "status": "frontend_required",
        "message": (
            "Market discovery is performed through "
            "Deriv's public WebSocket."
        )
    }