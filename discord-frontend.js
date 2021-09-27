// Discord slash command frontend for http_backend.py

const axios = require("axios");
const { Client, Intents } = require("discord.js");

const { discord_slash_prefix, discord_token, backend_port_number } = require("./config.json");
const sailorServiceURL = `http://localhost:${backend_port_number}`;

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

client.on("ready", onceReady);
client.on("interactionCreate", onInteractionCreate);

client.login(discord_token);

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

// Standard ready message
// Also sets playing status
function onceReady() {
    console.log(":3");
    client.user.setPresence({
        "status": "online",
        "activities": [{
            "name": `Type /${discord_slash_prefix} help for help!`
        }]
    });
}

// Command handler (and potential other stuff)
async function onInteractionCreate(interaction) {
	if (!interaction.isCommand()) return;

	let commandName = interaction.commandName;
	let commandArguments = await interaction.options.getString("input");
    let fullCommand;
    if (commandName === discord_slash_prefix) {
        if (commandArguments) {
            fullCommand = commandArguments;
        }
        else {
            return;
        }
    }
    else {
        if (commandArguments) {
            fullCommand = `${commandName} ${commandArguments}`;
        }
        else {
            fullCommand = commandName;
        }
    }

    console.log(`id=${interaction.id} user=${interaction.user.tag} userId=${interaction.user.id} | ${fullCommand}`);

    axios
    .post(sailorServiceURL, {
        "id": `discordslash:${interaction.id}`,
        "message": fullCommand,
        "is_owner": false,
        "character_limit": 2000,
        "format_name": "discord"
    })
    .then(async (response) => {
        let replyOneLiner = toOneLiner(response.data);
        console.log(`id=${interaction.id} status=${response.status} | ${replyOneLiner}`);
        if (response.data.length) {
            await interaction.reply(response.data.join("\n"));
        }
    })
    .catch(async (error) => {
        try {
            let replyOneLiner = toOneLiner(error.response.data);
            console.error(`id=${interaction.id} status=${error.response.status} | ${replyOneLiner}`);
            if (error.response.data.length) {
                await interaction.reply(error.response.data.join("\n"));
            }
        }
        catch {
            let errorMessage;
            if (error.code) {
                errorMessage = `An error occurred: ${error.code}`;
            }
            else {
                errorMessage = "An unknown error occurred.";
            }
            console.error(`id=${interaction.id} | ${errorMessage}`);
            if (error.code === "ECONNREFUSED") {
                await interaction.reply("My brain stopped working. Please contact my owner. :<");
            }
            else if (error.code !== "ECONNRESET") {
                await interaction.reply(errorMessage);
            }
        }
    });
}
