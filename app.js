const DERIV_URL =
    "wss://api.derivws.com/trading/v1/options/ws/public";

const connection =
    document.getElementById("connection");

const message =
    document.getElementById("message");

let socket;


function status(text) {
    if (connection) {
        connection.textContent = text;
    }
}


function messageText(text) {
    if (message) {
        message.textContent = text;
    }
}


function connect() {

    status("● CONNECTING TO DERIV...");
    messageText("Opening live market connection...");

    try {

        socket = new WebSocket(DERIV_URL);

    } catch (error) {

        status("● CONNECTION FAILED");
        messageText(error.message);
        return;
    }


    socket.onopen = function () {

        status("● CONNECTED TO DERIV");

        messageText(
            "Live connection established. Requesting markets..."
        );

        socket.send(
            JSON.stringify({
                active_symbols: "brief",
                req_id: 1
            })
        );
    };


    socket.onmessage = function(event) {

        console.log(
            "DERIV:",
            event.data
        );

        try {

            const data =
                JSON.parse(event.data);


            if (data.error) {

                status("● DERIV API ERROR");

                messageText(
                    data.error.message
                );

                return;
            }


            if (
                data.msg_type ===
                "active_symbols"
            ) {

                const markets =
                    data.active_symbols || [];


                status(
                    "● LIVE MARKET DATA"
                );


                messageText(
                    `Connected successfully. ${markets.length} markets received.`
                );


                console.log(
                    "MARKETS:",
                    markets
                );
            }

        } catch (error) {

            console.error(
                "Message error:",
                error
            );
        }
    };


    socket.onerror = function(error) {

        console.error(
            "WEBSOCKET ERROR:",
            error
        );

        status(
            "● WEBSOCKET ERROR"
        );

        messageText(
            "The browser could not establish the Deriv WebSocket."
        );
    };


    socket.onclose = function(event) {

        console.log(
            "WEBSOCKET CLOSED:",
            event.code,
            event.reason
        );

        status(
            "● CONNECTION CLOSED"
        );

        messageText(
            `Deriv connection closed. Code: ${event.code}`
        );
    };
}


connect();