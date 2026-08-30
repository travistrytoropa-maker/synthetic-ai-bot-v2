const DERIV_URL =
    "wss://api.derivws.com/trading/v1/options/ws/public";
let socket = null;

const markets = {};

const TARGETS = [
    {
        key: "V10",
        names: ["Volatility 10 Index"]
    },
    {
        key: "V25",
        names: ["Volatility 25 Index"]
    },
    {
        key: "V50",
        names: ["Volatility 50 Index"]
    },
    {
        key: "V75",
        names: ["Volatility 75 Index"]
    },
    {
        key: "V100",
        names: ["Volatility 100 Index"]
    },
    {
        key: "STEP",
        names: ["Step Index"]
    },
    {
        key: "JUMP10",
        names: ["Jump 10 Index"]
    },
    {
        key: "JUMP25",
        names: ["Jump 25 Index"]
    },
    {
        key: "JUMP50",
        names: ["Jump 50 Index"]
    },
    {
        key: "JUMP75",
        names: ["Jump 75 Index"]
    }
];


function setConnection(text) {

    const element =
        document.getElementById("connection");

    if (element) {
        element.textContent = text;
    }
}


function setMessage(text) {

    const element =
        document.getElementById("message");

    if (element) {
        element.textContent = text;
    }
}


function connectDeriv() {

    setConnection("● CONNECTING TO DERIV...");

    socket = new WebSocket(DERIV_URL);


    socket.onopen = function () {

        setConnection("● CONNECTED TO DERIV");

        setMessage(
            "Connected. Discovering synthetic markets..."
        );

        requestMarkets();
    };


    socket.onmessage = function(event) {

        try {

            const data =
                JSON.parse(event.data);

            handleMessage(data);

        } catch (error) {

            console.error(
                "Message parsing error:",
                error
            );
        }
    };
socket.onerror = function(error) {

    console.error(
        "Deriv WebSocket error:",
        error
    );

    setConnection("● DERIV CONNECTION ERROR");

    setMessage(
        "Deriv WebSocket connection failed. Check browser console."
    );
};


socket.onclose = function(event) {

    console.log(
        "Deriv WebSocket closed:",
        event.code,
        event.reason
    );

    setConnection("● DISCONNECTED");

    setMessage(
        `Connection closed (${event.code}). Retrying...`
    );

    setTimeout(
        connectDeriv,
        5000
    );
};

    socket.onclose = function() {

        setConnection("● DISCONNECTED");

        setMessage(
            "Connection closed. Reconnecting..."
        );

        setTimeout(
            connectDeriv,
            5000
        );
    };
}


function requestMarkets() {

    if (
        !socket ||
        socket.readyState !== WebSocket.OPEN
    ) {
        return;
    }


    /*
     * IMPORTANT:
     * Current Deriv API uses active_symbols
     * without the old product_type parameter.
     */

    socket.send(
        JSON.stringify({
            active_symbols: "brief",
            req_id: 1
        })
    );
}


function handleMessage(data) {

    if (data.error) {

        console.error(
            "Deriv API error:",
            data.error
        );

        setMessage(
            data.error.message ||
            "Deriv returned an error."
        );

        return;
    }


    if (
        data.msg_type ===
        "active_symbols"
    ) {

        handleMarkets(
            data.active_symbols || []
        );

        return;
    }


    if (
        data.msg_type ===
        "tick"
    ) {

        handleTick(
            data.tick
        );

        return;
    }
}


function normalizeName(name) {

    return String(name || "")
        .trim()
        .toLowerCase()
        .replace(/\s+/g, " ");
}


function handleMarkets(symbolList) {

    console.log(
        "Deriv returned",
        symbolList.length,
        "markets"
    );


    let found = 0;


    symbolList.forEach(function(item) {

        const symbol =
            item.underlying_symbol;

        const name =
            item.underlying_symbol_name;


        if (!symbol || !name) {
            return;
        }


        const normalized =
            normalizeName(name);


        TARGETS.forEach(function(target) {

            const matches =
                target.names.some(
                    function(targetName) {

                        return (
                            normalizeName(
                                targetName
                            ) === normalized
                        );

                    }
                );


            if (matches) {

                markets[target.key] = {
                    symbol: symbol,
                    name: name
                };

                found++;

                console.log(
                    target.key,
                    "→",
                    symbol,
                    name
                );
            }

        });

    });


    console.log(
        "Target markets found:",
        markets
    );


    /*
     * If exact names don't match,
     * search using keywords.
     */

    if (found === 0) {

        console.warn(
            "Exact market names not found."
        );

        searchSyntheticMarkets(
            symbolList
        );

        return;
    }


    subscribeToMarkets();


    setMessage(
        `${Object.keys(markets).length} target markets found.`
    );
}


function searchSyntheticMarkets(symbolList) {

    symbolList.forEach(function(item) {

        const name =
            normalizeName(
                item.underlying_symbol_name
            );

        const symbol =
            item.underlying_symbol;


        if (!symbol || !name) {
            return;
        }


        if (
            name.includes("volatility") ||
            name.includes("step") ||
            name.includes("jump")
        ) {

            console.log(
                "Synthetic market:",
                name,
                "→",
                symbol
            );
        }

    });


    setMessage(
        "Synthetic markets were received. Check the browser console for their exact names and symbols."
    );
}


function subscribeToMarkets() {

    Object.keys(markets).forEach(
        function(key) {

            const market =
                markets[key];


            socket.send(
                JSON.stringify({
                    ticks: market.symbol,
                    subscribe: 1,
                    req_id: 100 + key.length
                })
            );

        }
    );
}


function handleTick(tick) {

    if (!tick) {
        return;
    }


    const symbol =
        tick.symbol;

    const price =
        tick.quote;


    let marketKey = null;


    Object.keys(markets).forEach(
        function(key) {

            if (
                markets[key].symbol ===
                symbol
            ) {

                marketKey = key;
            }

        }
    );


    if (!marketKey) {
        return;
    }


    updatePrice(
        marketKey,
        price
    );
}


function updatePrice(key, price) {

    const priceElement =
        document.getElementById(key);


    const statusElement =
        document.getElementById(
            `${key}-status`
        );


    if (priceElement) {

        priceElement.textContent =
            formatPrice(price);

        priceElement.dataset.symbol =
            markets[key].symbol;
    }


    if (statusElement) {

        statusElement.textContent =
            "● LIVE";
    }
}


function formatPrice(price) {

    if (
        price === null ||
        price === undefined
    ) {

        return "--";
    }


    const number =
        Number(price);


    if (Number.isNaN(number)) {
        return "--";
    }


    return number.toLocaleString(
        undefined,
        {
            maximumFractionDigits: 4
        }
    );
}


connectDeriv();