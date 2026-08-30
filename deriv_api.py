DERIV_PUBLIC_WS = (
    "wss://api.derivws.com/"
    "trading/v1/options/ws/public"
)


def deriv_connection_info():
    return {
        "status": "ready",
        "websocket": DERIV_PUBLIC_WS,
        "market_data": True,
        "authentication_required": False
    }