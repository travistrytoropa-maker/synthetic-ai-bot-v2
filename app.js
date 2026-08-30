const BACKEND_URL =
    "https://synthetic-ai-bot-v2.onrender.com";

const DERIV_WS =
    "wss://api.derivws.com/trading/v1/options/ws/public";


const connection =
    document.getElementById("connection");

const message =
    document.getElementById("message");


const TARGETS = [
    {
        key: "V10",
        name: "Volatility 10 Index"
    },
    {
        key: "V25",
        name: "Volatility 25 Index"
    },
    {
        key: "V50",
        name: "Volatility 50 Index"
    },
    {
        key: "V75",
        name: "Volatility 75 Index"
    },
    {
        key: "V100",
        name: "Volatility 100 Index"
    },
    {
        key: "STEP",
        name: "Step Index"
    },
    {
        key: "JUMP10",
        name: "Jump 10 Index"
    },
    {
        key: "JUMP25",
        name: "Jump 25 Index"
    },
    {
        key: "JUMP50",
        name: "Jump 50 Index"
    },
    {
        key: "JUMP75",
        name: "Jump 75 Index"
    }
];


let socket = null;

const discoveredMarkets = {};


function setConnection(text) {

    if (connection) {
        connection.textContent = text;
    }
}


function setMessage(text) {

    if (message) {
        message.textContent = text;
    }
}


function normalize(text) {

    return String(text || "")
        .trim()
        .toLowerCase()
        .replace(/\s+/g, " ");
}


function connectDeriv() {

    setConnection(
        "● CONNECTING TO DERIV..."
    );

    setMessage(
        "Opening public market-data connection..."
    );


    socket =
        new WebSocket(DERIV_WS);


    socket.onopen = function() {

        setConnection(
            "● DERIV CONNECTED"
        );

        setMessage(
            "Connected. Discovering markets..."
        );


        socket.send(
            JSON.stringify({
                active_symbols: "brief",
                req_id: 1
            })
        );
    };


    socket.onmessage =
        function(event) {

            let data;

            try {

                data =
                    JSON.parse(event.data);

            } catch (error) {

                console.error(
                    "Invalid Deriv response",
                    error
                );

                return;
            }


            console.log(
                "DERIV RESPONSE:",
                data
            );


            if (data.error) {

                setMessage(
                    "Deriv error: " +
                    data.error.message
                );

                return;
            }


            if (
                data.msg_type ===
                "active_symbols"
            ) {

                discoverMarkets(
                    data.active_symbols || []
                );

                return;
            }


            if (
                data.msg_type ===
                "tick"
            ) {

                updateTick(
                    data.tick
                );
            }
        };


    socket.onerror =
        function(error) {

            console.error(
                "Deriv WebSocket error:",
                error
            );

            setConnection(
                "● DERIV CONNECTION ERROR"
            );

            setMessage(
                "The browser could not connect to Deriv."
            );
        };


    socket.onclose =
        function(event) {

            console.log(
                "Deriv closed:",
                event.code,
                event.reason
            );

            setConnection(
                "● DERIV DISCONNECTED"
            );

            setMessage(
                "Deriv connection closed."
            );
        };
}


function discoverMarkets(list) {

    console.log(
        "Total Deriv markets:",
        list.length
    );


    for (
        const item of list
    ) {

        const symbol =
            item.underlying_symbol ||
            item.symbol;


        const name =
            item.underlying_symbol_name ||
            item.display_name;


        if (!symbol || !name) {
            continue;
        }


        const marketName =
            normalize(name);


        for (
            const target of TARGETS
        ) {

            if (
                marketName ===
                normalize(target.name)
            ) {

                discoveredMarkets[
                    target.key
                ] = {
                    symbol: symbol,
                    name: name
                };


               console.log(
    "DISCOVERED MARKET:",
    target.name,
    "SYMBOL:",
    symbol
);
            }
        }
    }


    const found =
        Object.keys(
            discoveredMarkets
        ).length;


    setConnection(
        "● LIVE MARKET DATA"
    );


    setMessage(
        `${found} of 10 target markets discovered.`
    );


    subscribeToMarkets();


    /*
     * If exact names differ, print all
     * synthetic markets to the console.
     */

    if (found < 10) {

        console.log(
            "Some target markets were not matched."
        );

        console.log(
            "Full Deriv market list:",
            list
        );
    }
}


function subscribeToMarkets() {

    if (
        !socket ||
        socket.readyState !==
        WebSocket.OPEN
    ) {
        return;
    }


    Object.keys(
        discoveredMarkets
    ).forEach(
        function(key) {

            const market =
                discoveredMarkets[key];


            socket.send(
                JSON.stringify({
                    ticks: market.symbol,
                    subscribe: 1
                })
            );
        }
    );
}


function updateTick(tick) {

    if (!tick) {
        return;
    }


    const symbol =
        tick.symbol;


    const quote =
        tick.quote;


    for (
        const key in discoveredMarkets
    ) {

        if (
            discoveredMarkets[key].symbol ===
            symbol
        ) {

            const priceElement =
                document.getElementById(key);


            const statusElement =
                document.getElementById(
                    `${key}-status`
                );


            if (priceElement) {

                priceElement.textContent =
                    Number(quote)
                        .toLocaleString(
                            undefined,
                            {
                                maximumFractionDigits: 4
                            }
                        );
            }


            if (statusElement) {

                statusElement.textContent =
                    "● LIVE";
            }
        }
    }
}


connectDeriv();