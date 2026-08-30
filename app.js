const DERIV_URL = "wss://api.derivws.com/trading/v1/options/ws/public";
console.log("APP.JS LOADED");
console.log("DERIV URL:", DERIV_URL);
const connection =
    document.getElementById("connection");

const message =
    document.getElementById("message");

connection.textContent =
    "● TESTING DERIV CONNECTION...";

const ws =
    new WebSocket(DERIV_URL);

ws.onopen = function () {

    connection.textContent =
        "● CONNECTED TO DERIV";

    message.textContent =
        "WebSocket connected successfully.";

    console.log("DERIV CONNECTED");

    ws.send(JSON.stringify({
        active_symbols: "brief",
        req_id: 1
    }));
};


ws.onmessage = function(event) {

    console.log(
        "DERIV RESPONSE:",
        event.data
    );

    try {

        const data =
            JSON.parse(event.data);

        if (
            data.msg_type ===
            "active_symbols"
        ) {

            message.textContent =
                "Deriv connected. Markets received: " +
                data.active_symbols.length;
        }

        if (data.error) {

            message.textContent =
                "Deriv API error: " +
                data.error.message;
        }

    } catch (error) {

        message.textContent =
            "Received invalid response.";
    }
};


ws.onerror = function() {

    connection.textContent =
        "● WEBSOCKET ERROR";

    message.textContent =
        "The browser could not establish the Deriv connection.";

    console.log(
        "DERIV WEBSOCKET ERROR"
    );
};


ws.onclose = function(event) {

    connection.textContent =
        "● CONNECTION CLOSED";

    message.textContent =
        "WebSocket closed. Code: " +
        event.code;

    console.log(
        "DERIV CLOSED",
        event.code,
        event.reason
    );
};