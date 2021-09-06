// Twitch client for http_service.py

const axios = require("axios");
const tmi = require("tmi.js");
const {
    twitch_owner,
    twitch_username,
    twitch_token,
    twitch_channels,
    http_port,
    prefix
} = require("./config.json");
const sailorServiceURL = `http://localhost:${http_port}`;

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
        "is_owner": tags["user-id"] === twitch_owner
    })
    .then((response) => {
        let reply = response.data.join(" | ").split("\n").join(" | ");
        if (!reply) {
            console.log(`sailor (${response.status}): <empty>`);
            return;
        }
        console.log(`sailor (${response.status}): ${reply}`);
        client.say(channel, reply);
    })
    .catch((error) => {
        try {
            let reply = error.response.data.join(" | ").split("\n").join(" | ");
            console.log(`sailor (${error.response.status}): ${reply}`);
            client.say(channel, reply);
        }
        catch {
            reply = `An error occurred: ${error.code}`;
            console.error(reply);
            if (error.code === "ECONNREFUSED") {
                client.say(channel, "My brain stopped working. Please contact my owner. :<");
            }
            else if (error.code !== "ECONNRESET") {
                client.say(channel, reply);
            }
        }
    });
}
