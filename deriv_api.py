DERIV_PUBLIC_WS = "wss://api.derivws.com/trading/v1/options/ws/public"


def deriv_connection_info():
    return {
        "status": "ready",
        "endpoint": DERIV_PUBLIC_WS,
        "authentication": "not_required",
        "purpose": "public market data"
    }