import asyncio
import json
import urllib.request


# Deriv public market-data endpoint
DERIV_API = "https://api.derivws.com"


async def http_get(path):
    """
    Performs a public HTTP request to Deriv.
    """

    url = DERIV_API + path

    def request():
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Synthetic-AI-Signal-Engine/1.0"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=20
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    return await asyncio.to_thread(request)


async def get_market_data():

    return await http_get(
        "/trading/v1/active_symbols"
    )


async def get_active_symbols():

    data = await get_market_data()

    return data


async def get_tick(symbol):

    # This will be connected to the live
    # market-data stream after symbol discovery.
    return {
        "status": "pending",
        "symbol": symbol,
        "message": "Live tick connection will be enabled after market discovery."
    }


async def get_candles(
    symbol,
    granularity,
    count=100
):

    # Candle engine comes immediately after
    # successful market discovery.
    return {
        "status": "pending",
        "symbol": symbol,
        "granularity": granularity,
        "count": count
    }