// A Twitch frontend for http_backend.py

const crypto = require('crypto');
const url = require("url");
const axios = require("axios");
const tmi = require("tmi.js");

const characterLimit = 500;
const {
    prefix,
    backend_port_number,
    twitch_owner_id,
    twitch_username,
    twitch_token,
    twitch_channels
} = require("./config.json");
const sailorServiceURL = `http://localhost:${backend_port_number}`;
const pastebinURL = "https://ghostbin.com/paste/new";

const clientOptions = {
    identity: {
        username: twitch_username,
        password: twitch_token
    },
    channels: twitch_channels
};

const client = new tmi.client(clientOptions);

client.on("message", onMessage);
client.on("connected", onConnected);

client.connect();

// Truncates an array of strings to a single line for logging
function toOneLiner(data, maxLength=75) {
    let oneLiner = data.join(" ").split("\n").join(" ");
    if (oneLiner.length > maxLength) {
        oneLiner = oneLiner.substring(0, maxLength-1) + "…";
    }
    if (oneLiner.length === 0) {
        oneLiner = "<empty>";
    }
    return oneLiner;
}

/*
Sends a message normally if it's short enough.
Otherwise, posts the message to a pastebin site (currently Ghostbin) and sends the link in chat.
*/
function extSay(channel, tags, data) {
    if (data.length === 0) {
        return;
    }
    else if (data.length === 1) {
        client.say(channel, data[0].split("\n").join(" | "));
    }
    else {
        let pastebinRequestBody = new url.URLSearchParams({
            "text": data.join("\n"),
            "title": "Multiline post",
            "password": crypto
                .randomBytes(32)
                .toString("hex")
        });
        axios
        .post(pastebinURL, pastebinRequestBody.toString())
        .then((response) => {
            let reply = `Multiline post: ${response.request.res.responseUrl}`;
            console.log(`id=${tags.id} | ${reply}`);
            client.say(channel, reply);
        });
    }
}

// Standard ready message
function onConnected(addr, port) {
    console.log(`Connected to ${addr}:${port}`);
}

// Command handler (and potential other stuff)
function onMessage(channel, tags, message, self) {
    if (self) return;
    if (!message.startsWith(prefix)) return;

    console.log(`id=${tags.id} user=${tags.username} userId=${tags["user-id"]} channel=${channel} | ${message}`);

    axios
    .post(sailorServiceURL, {
        "id": `twitch:${tags.id}`,
        "message": message.replace(prefix, "").trim(),
        "is_owner": tags["user-id"] === twitch_owner_id,
        "character_limit": characterLimit
    })
    .then((response) => {
        let replyOneLiner = toOneLiner(response.data);
        console.log(`id=${tags.id} status=${response.status} | ${replyOneLiner}`);
        extSay(channel, tags, response.data);
    })
    .catch((error) => {
        try {
            let replyOneLiner = toOneLiner(error.response.data);
            console.log(`id=${tags.id} status=${error.response.status} | ${replyOneLiner}`);
            extSay(channel, tags, error.response.data);
        }
        catch {
            let errorMessage;
            if (error.code) {
                errorMessage = `An error occurred: ${error.code}`;
            }
            else {
                errorMessage = "An unknown error occurred.";
            }
            console.error(`id=${tags.id} | ${errorMessage}`);
            if (error.code === "ECONNREFUSED") {
                client.say(channel, "My brain stopped working. Please contact my owner. :<");
            }
            else if (error.code !== "ECONNRESET") {
                client.say(channel, errorMessage);
            }
        }
    });
}
