from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deriv_api import deriv_connection_info


app = FastAPI(
    title="Synthetic AI Signal Engine",
    version="3.0.0"
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
        "message": "Synthetic AI Signal Engine is running",
        "version": "3.0.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.get("/deriv")
async def deriv():
    return deriv_connection_info()