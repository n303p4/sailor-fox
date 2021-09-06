// Twitch client for http_service.py

const crypto = require('crypto');
const url = require("url");
const axios = require("axios");
const tmi = require("tmi.js");

const characterLimit = 500;
const {
    twitch_owner,
    twitch_username,
    twitch_token,
    twitch_channels,
    http_port,
    prefix
} = require("./config.json");
const sailorServiceURL = `http://localhost:${http_port}`;
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

function toOneLiner(data, maxLength=100) {
    let oneLiner = data.join(" ").split("\n").join(" ");
    if (oneLiner.length > maxLength) {
        oneLiner = oneLiner.substring(0, maxLength-1) + "…";
    }
    return oneLiner;
}

function multiSay(channel, data) {
    if (data.length === 1) {
        client.say(channel, data[0]);
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
            console.log(reply);
            client.say(channel, reply);
        });
    }
}

function onConnected(addr, port) {
    console.log(`Connected to ${addr}:${port}`);
}

function onMessage(channel, tags, message, self) {
    if (self) return;
    if (!message.startsWith(prefix)) return;

    console.log(`user=${tags.username} userId=${tags["user-id"]} channel=${channel} | ${message}`);

    axios
    .post(sailorServiceURL, {
        "message": message.replace(prefix, ""),
        "is_owner": tags["user-id"] === twitch_owner,
        "character_limit": characterLimit
    })
    .then((response) => {
        if (!response.data) {
            console.log(`sailor (${response.status}): <empty>`);
            return;
        }
        let replyOneLiner = toOneLiner(response.data);
        console.log(`sailor (${response.status}): ${replyOneLiner}`);
        multiSay(channel, response.data);
    })
    .catch((error) => {
        try {
            let replyOneLiner = toOneLiner(error.response.data);
            console.log(`sailor (${error.response.status}): ${replyOneLiner}`);
            multiSay(channel, error.response.data);
        }
        catch {
            let errorMessage;
            if (error.code) {
                errorMessage = `An error occurred: ${error.code}`;
            }
            else {
                errorMessage = "An unknown error occurred.";
            }
            console.error(errorMessage);
            if (error.code === "ECONNREFUSED") {
                client.say(channel, "My brain stopped working. Please contact my owner. :<");
            }
            else if (error.code !== "ECONNRESET") {
                client.say(channel, errorMessage);
            }
        }
    });
}
