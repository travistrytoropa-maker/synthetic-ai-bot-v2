const DERIV_URL =
    "wss://api.derivws.com/trading/v1/options/ws/public";

const connectionElement =
    document.getElementById("connection");

const messageElement =
    document.getElementById("message");


// --------------------------------------------------
// Markets we want to find
// --------------------------------------------------

const TARGET_MARKETS = [
    "Volatility 10 Index",
    "Volatility 25 Index",
    "Volatility 50 Index",
    "Volatility 75 Index",
    "Volatility 100 Index",
    "Step Index",
    "Jump 10 Index",
    "Jump 25 Index",
    "Jump 50 Index",
    "Jump 75 Index"
];


// --------------------------------------------------
// Create WebSocket connection
// --------------------------------------------------

let socket = null;


function connectDeriv() {

    connectionElement.textContent =
        "● CONNECTING TO DERIV...";


    socket = new WebSocket(DERIV_URL);


    socket.onopen = function () {

        connectionElement.textContent =
            "● CONNECTED TO DERIV";

        messageElement.textContent =
            "Connected. Finding synthetic markets...";


        requestMarkets();
    };


    socket.onmessage = function (event) {

        try {

            const data =
                JSON.parse(event.data);

            handleMessage(data);

        } catch (error) {

            console.error(
                "Invalid Deriv message:",
                error
            );
        }
    };


    socket.onerror = function (error) {

        console.error(
            "Deriv WebSocket error:",
            error
        );

        connectionElement.textContent =
            "● CONNECTION ERROR";

        messageElement.textContent =
            "Could not connect to Deriv.";
    };


    socket.onclose = function () {

        connectionElement.textContent =
            "● DISCONNECTED";

        messageElement.textContent =
            "Connection closed. Reconnecting...";


        setTimeout(
            connectDeriv,
            5000
        );
    };
}


// --------------------------------------------------
// Request available markets
// --------------------------------------------------

function requestMarkets() {

    if (
        !socket ||
        socket.readyState !== WebSocket.OPEN
    ) {
        return;
    }


    socket.send(
        JSON.stringify({

            active_symbols: "brief",

            product_type: "basic",

            req_id: 1

        })
    );
}


// --------------------------------------------------
// Handle incoming messages
// --------------------------------------------------

function handleMessage(data) {


    // -------------------------------
    // Active markets
    // -------------------------------

    if (
        data.msg_type ===
        "active_symbols"
    ) {

        processMarkets(
            data.active_symbols || []
        );

        return;
    }


    // -------------------------------
    // Live tick
    // -------------------------------

    if (
        data.msg_type ===
        "tick"
    ) {

        processTick(
            data.tick
        );

        return;
    }


    // -------------------------------
    // API error
    // -------------------------------

    if (data.error) {

        console.error(
            "Deriv error:",
            data.error
        );

        messageElement.textContent =
            data.error.message ||
            "Deriv API error.";
    }
}


// --------------------------------------------------
// Find our 10 markets
// --------------------------------------------------

function processMarkets(markets) {

    const foundMarkets = [];


    markets.forEach(
        function (market) {

            const name =
                (
                    market.display_name ||
                    market.underlying_symbol_name ||
                    ""
                ).toLowerCase();


            TARGET_MARKETS.forEach(
                function (target) {

                    if (
                        name ===
                        target.toLowerCase()
                    ) {

                        foundMarkets.push({
                            target: target,
                            symbol:
                                market.underlying_symbol
                        });

                    }

                }
            );

        }
    );


    console.log(
        "Target markets found:",
        foundMarkets
    );


    if (foundMarkets.length === 0) {

        messageElement.textContent =
            "Deriv connected, but no target synthetic markets were found.";

        return;
    }


    messageElement.textContent =
        `${foundMarkets.length} synthetic markets connected.`;


    // Subscribe to every market we found

    foundMarkets.forEach(
        function (market) {

            subscribeToTick(
                market.symbol
            );

        }
    );
}


// --------------------------------------------------
// Subscribe to live price
// --------------------------------------------------

function subscribeToTick(symbol) {

    socket.send(
        JSON.stringify({

            ticks: symbol,

            subscribe: 1,

            req_id: 100

        })
    );
}


// --------------------------------------------------
// Process live price
// --------------------------------------------------

function processTick(tick) {

    if (!tick) {
        return;
    }


    const symbol =
        tick.symbol;

    const price =
        tick.quote;


    const marketElement =
        findMarketElement(symbol);


    if (!marketElement) {
        return;
    }


    marketElement.price.textContent =
        formatPrice(price);


    marketElement.status.textContent =
        "● LIVE";
}


// --------------------------------------------------
// Find dashboard card by symbol
// --------------------------------------------------

function findMarketElement(symbol) {

    const cards =
        document.querySelectorAll(
            ".card"
        );


    for (
        const card of cards
    ) {

        const priceElement =
            card.querySelector(
                ".price"
            );


        const statusElement =
            card.querySelector(
                ".status"
            );


        if (
            priceElement &&
            statusElement &&
            priceElement.dataset.symbol ===
            symbol
        ) {

            return {
                price: priceElement,
                status: statusElement
            };
        }
    }


    return null;
}


// --------------------------------------------------
// Format price
// --------------------------------------------------

function formatPrice(price) {

    if (
        price === undefined ||
        price === null
    ) {

        return "--";
    }


    return Number(price)
        .toLocaleString(
            undefined,
            {
                maximumFractionDigits: 4
            }
        );
}


// --------------------------------------------------
// Start
// --------------------------------------------------

connectDeriv();