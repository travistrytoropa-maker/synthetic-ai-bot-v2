// ======================================================
// SYNTHETIC AI SIGNAL ENGINE
// FRONTEND CONFIGURATION
// ======================================================

// PUT YOUR PYTHON BACKEND RENDER URL HERE
const BACKEND_URL =
    "https://synthetic-ai-bot-v2.onrender.com";


// ======================================================
// Dashboard elements
// ======================================================

const connection =
    document.getElementById("connection");

const message =
    document.getElementById("message");


// ======================================================
// Status helpers
// ======================================================

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


// ======================================================
// Test backend
// ======================================================

async function testBackend() {

    setConnection(
        "● CONNECTING TO BACKEND..."
    );

    setMessage(
        "Checking Python analysis server..."
    );

    try {

        const response =
            await fetch(
                `${BACKEND_URL}/health`,
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        if (
            data.status ===
            "healthy"
        ) {

            setConnection(
                "● BACKEND ONLINE"
            );

            setMessage(
                "Python backend connected successfully."
            );

            console.log(
                "BACKEND:",
                data
            );

            await loadMarkets();

        } else {

            throw new Error(
                "Backend returned an unexpected response."
            );
        }

    } catch (error) {

        console.error(
            "BACKEND CONNECTION ERROR:",
            error
        );

        setConnection(
            "● BACKEND CONNECTION FAILED"
        );

        setMessage(
            "Could not connect to the Render backend."
        );
    }
}


// ======================================================
// Load Deriv markets through backend
// ======================================================

async function loadMarkets() {

    setMessage(
        "Requesting synthetic markets..."
    );

    try {

        const response =
            await fetch(
                `${BACKEND_URL}/markets`,
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            "MARKET RESPONSE:",
            data
        );


        if (
            data.status !==
            "success"
        ) {

            throw new Error(
                data.message ||
                "Market request failed."
            );
        }


        const markets =
            data.markets || [];


        setMessage(
            `${markets.length} markets received from backend.`
        );


        displayMarkets(
            markets
        );


    } catch (error) {

        console.error(
            "MARKET ERROR:",
            error
        );

        setMessage(
            "Backend is online, but market data is not available yet."
        );
    }
}


// ======================================================
// Our 10 target markets
// ======================================================

const TARGET_MARKETS = {

    V10:
        "Volatility 10 Index",

    V25:
        "Volatility 25 Index",

    V50:
        "Volatility 50 Index",

    V75:
        "Volatility 75 Index",

    V100:
        "Volatility 100 Index",

    STEP:
        "Step Index",

    JUMP10:
        "Jump 10 Index",

    JUMP25:
        "Jump 25 Index",

    JUMP50:
        "Jump 50 Index",

    JUMP75:
        "Jump 75 Index"
};


// ======================================================
// Match market names
// ======================================================

function displayMarkets(markets) {

    let found = 0;


    markets.forEach(
        function(market) {

            const symbol =
                market.symbol;

            const name =
                market.name;


            if (!symbol || !name) {
                return;
            }


            const normalizedName =
                name
                    .trim()
                    .toLowerCase();


            for (
                const key in TARGET_MARKETS
            ) {

                const target =
                    TARGET_MARKETS[key]
                        .toLowerCase();


                if (
                    normalizedName ===
                    target
                ) {

                    updateMarketCard(
                        key,
                        symbol,
                        name
                    );

                    found++;

                    console.log(
                        key,
                        symbol,
                        name
                    );
                }
            }
        }
    );


    if (found > 0) {

        setMessage(
            `${found} target synthetic markets identified.`
        );

        startPriceUpdates();

    } else {

        setMessage(
            "Backend returned markets, but the target synthetic markets were not matched."
        );
    }
}


// ======================================================
// Update card
// ======================================================

function updateMarketCard(
    key,
    symbol,
    name
) {

    const price =
        document.getElementById(key);

    const status =
        document.getElementById(
            `${key}-status`
        );


    if (price) {

        price.dataset.symbol =
            symbol;

        price.dataset.market =
            name;
    }


    if (status) {

        status.textContent =
            "● MARKET FOUND";
    }
}


// ======================================================
// Get live price from backend
// ======================================================

async function getPrice(
    key,
    symbol
) {

    try {

        const response =
            await fetch(
                `${BACKEND_URL}/tick/${encodeURIComponent(symbol)}`,
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        if (
            data.status !==
            "success"
        ) {
            return;
        }


        const price =
            data.data.price;


        const priceElement =
            document.getElementById(key);


        const statusElement =
            document.getElementById(
                `${key}-status`
            );


        if (priceElement) {

            priceElement.textContent =
                Number(price).toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 4
                    }
                );
        }


        if (statusElement) {

            statusElement.textContent =
                "● LIVE PRICE";
        }


    } catch (error) {

        console.error(
            `Price error ${key}:`,
            error
        );
    }
}


// ======================================================
// Start price updates
// ======================================================

function startPriceUpdates() {

    Object.keys(TARGET_MARKETS)
        .forEach(
            function(key) {

                const priceElement =
                    document.getElementById(key);


                if (
                    priceElement &&
                    priceElement.dataset.symbol
                ) {

                    getPrice(
                        key,
                        priceElement.dataset.symbol
                    );
                }
            }
        );


    setInterval(
        function() {

            Object.keys(TARGET_MARKETS)
                .forEach(
                    function(key) {

                        const priceElement =
                            document.getElementById(key);


                        if (
                            priceElement &&
                            priceElement.dataset.symbol
                        ) {

                            getPrice(
                                key,
                                priceElement.dataset.symbol
                            );
                        }
                    }
                );

        },
        5000
    );
}


// ======================================================
// START APPLICATION
// ======================================================

testBackend();