const BACKEND_URL =
    "https://YOUR-BACKEND-URL.onrender.com";


const marketsContainer =
    document.getElementById(
        "markets"
    );


const connection =
    document.getElementById(
        "connection"
    );


async function api(path) {

    const response =
        await fetch(
            BACKEND_URL + path
        );

    if (!response.ok) {

        throw new Error(
            "HTTP " +
            response.status
        );
    }

    return response.json();
}


async function checkBackend() {

    try {

        const data =
            await api("/health");

        if (
            data.status ===
            "healthy"
        ) {

            connection.textContent =
                "Backend Online";

            connection.className =
                "connection online";

        }

    } catch (error) {

        connection.textContent =
            "Backend Offline";

        connection.className =
            "connection offline";
    }
}


function createMarketCard(
    market
) {

    const card =
        document.createElement(
            "div"
        );

    card.className =
        "market-card";


    card.innerHTML = `

        <div class="market-header">

            <div>

                <h3>
                    ${market.name}
                </h3>

                <span>
                    ${market.symbol}
                </span>

            </div>

            <div class="status">
                ${market.status}
            </div>

        </div>

        <div
            class="analysis"
            id="analysis-${market.symbol}"
        >
            Waiting for analysis...
        </div>

    `;


    return card;
}


async function analyzeCard(
    card,
    market
) {

    const box =
        card.querySelector(
            ".analysis"
        );


    try {

        const data =
            await api(
                "/analyze-market/" +
                encodeURIComponent(
                    market.symbol
                )
            );


        if (
            data.status !==
            "success"
        ) {

            throw new Error(
                data.message ||
                "Analysis failed"
            );
        }


        const analysis =
            data.result.analysis;


        box.innerHTML = `

            <div class="signal">

                <span>
                    SIGNAL
                </span>

                <strong>
                    ${analysis.signal}
                </strong>

            </div>

            <div class="metrics">

                <div>
                    <small>
                        Confidence
                    </small>

                    <strong>
                        ${analysis.confidence}%
                    </strong>
                </div>

                <div>
                    <small>
                        Score
                    </small>

                    <strong>
                        ${analysis.overall_score}
                    </strong>
                </div>

                <div>
                    <small>
                        Quality
                    </small>

                    <strong>
                        ${analysis.setup_quality}
                    </strong>
                </div>

            </div>

            <div class="timeframes">

                <div>
                    H1:
                    ${analysis.timeframe_alignment.H1}
                </div>

                <div>
                    M15:
                    ${analysis.timeframe_alignment.M15}
                </div>

                <div>
                    M5:
                    ${analysis.timeframe_alignment.M5}
                </div>

            </div>

        `;

    } catch (error) {

        box.innerHTML = `

            <div class="error">
                Analysis error:
                ${error.message}
            </div>

        `;
    }
}


async function loadMarkets() {

    marketsContainer.innerHTML =
        "Discovering markets...";


    try {

        const data =
            await api(
                "/markets"
            );


        if (
            data.status !==
            "success"
        ) {

            throw new Error(
                data.message ||
                "Market discovery failed"
            );
        }


        const markets =
            data.markets.slice(
                0,
                10
            );


        marketsContainer.innerHTML =
            "";


        if (markets.length === 0) {

            marketsContainer.textContent =
                "No markets found.";

            return;
        }


        for (
            const market
            of markets
        ) {

            const card =
                createMarketCard(
                    market
                );

            marketsContainer.appendChild(
                card
            );


            // Analyze independently.
            analyzeCard(
                card,
                market
            );

        }

    } catch (error) {

        marketsContainer.innerHTML = `

            <div class="error">

                Market discovery error:
                ${error.message}

            </div>

        `;
    }
}


async function start() {

    await checkBackend();

    await loadMarkets();

}


start();


setInterval(
    checkBackend,
    20000
);


setInterval(
    loadMarkets,
    60000
);