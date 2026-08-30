import asyncio
import json
import websockets


DERIV_URL = "wss://ws.binaryws.com/websockets/v3"


class DerivClient:

    def __init__(self):
        self.websocket = None
        self.lock = asyncio.Lock()
        self.connected = False
        self.last_error = None

    async def connect(self):

        if self.websocket is not None:
            try:
                if not self.websocket.closed:
                    return
            except Exception:
                pass

        try:

            self.websocket = await websockets.connect(
                DERIV_URL,

                # Important for servers that reject
                # unexpected Origin headers.
                origin=None,

                ping_interval=20,
                ping_timeout=20,
                close_timeout=10,
                open_timeout=30
            )

            self.connected = True
            self.last_error = None

        except Exception as error:

            self.connected = False
            self.last_error = str(error)

            raise RuntimeError(
                f"Deriv WebSocket connection failed: {error}"
            )

    async def close(self):

        if self.websocket:

            try:
                await self.websocket.close()
            except Exception:
                pass

        self.websocket = None
        self.connected = False

    async def request(self, payload):

        async with self.lock:

            try:

                await self.connect()

                await self.websocket.send(
                    json.dumps(payload)
                )

                while True:

                    raw = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=30
                    )

                    data = json.loads(raw)

                    if "error" in data:

                        error = data["error"]

                        message = error.get(
                            "message",
                            "Unknown Deriv error"
                        )

                        raise RuntimeError(message)

                    return data

            except Exception as error:

                self.connected = False
                self.last_error = str(error)

                try:
                    await self.close()
                except Exception:
                    pass

                raise RuntimeError(
                    f"Deriv request failed: {error}"
                )

    async def active_symbols(self):

        return await self.request({
            "active_symbols": "brief",
            "req_id": 1001
        })

    async def tick(self, symbol):

        return await self.request({
            "ticks": symbol,
            "subscribe": 0,
            "req_id": 1002
        })

    async def candles(
        self,
        symbol,
        granularity,
        count=100
    ):

        return await self.request({
            "ticks_history": symbol,
            "style": "candles",
            "granularity": granularity,
            "count": count,
            "end": "latest",
            "req_id": 1003
        })


deriv = DerivClient()