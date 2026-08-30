from market_analyzer import analyze_market


async def scan_markets(markets):

    results = []

    for market in markets:

        if not isinstance(market, dict):
            continue

        symbol = market.get(
            "symbol"
        )

        name = market.get(
            "name",
            symbol
        )

        if not symbol:
            continue

        try:

            result = await analyze_market(
                symbol
            )

            result["name"] = name

            result["status"] = "success"

            results.append(result)

        except Exception as error:

            results.append({

                "status": "error",

                "name": name,

                "symbol": symbol,

                "error_type":
                    type(error).__name__,

                "message": str(error)

            })

    successful = [
        x for x in results
        if x.get("status") == "success"
    ]

    failed = [
        x for x in results
        if x.get("status") != "success"
    ]

    successful.sort(
        key=lambda item:
        item.get(
            "analysis",
            {}
        ).get(
            "confidence",
            0
        ),

        reverse=True
    )

    return successful + failed