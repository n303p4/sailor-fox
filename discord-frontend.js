// Discord slash command frontend for http_backend.py

const axios = require("axios");
const { Client, Intents, Permissions } = require("discord.js");

const { discord_slash_prefix, discord_token, backend_port_number } = require("./config.json");
const sailorServiceURL = `http://localhost:${backend_port_number}`;

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

client.on("ready", onceReady);
client.on("interactionCreate", onInteractionCreate);

client.login(discord_token);

// Truncates an array of strings to a single line for logging
function toOneLiner(data, maxLength=75) {
    let oneLiner = data.map(item => item.value).join(" ").split("\n").join(" ");
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

    let channel = interaction.channel;
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
        "id": `discordjs:${interaction.id}`,
        "message": fullCommand,
        "is_owner": false,
        "character_limit": 2000,
        "format_name": "discord",
        "channel_name": channel.name
    })
    .then(async (response) => {
        let replyOneLiner = toOneLiner(response.data);
        console.log(`id=${interaction.id} status=${response.status} | ${replyOneLiner}`);
        if (response.data.length) {
            let replyStack = [];
            response.data.forEach(item => {
                if (item.type === "rename_channel") {
                    if (
                        channel.type !== "GUILD_TEXT" ||
                        !channel.permissionsFor(client.user).has(Permissions.FLAGS.MANAGE_CHANNELS)
                    ) {
                        console.warn(
                            `id=${interaction.id} | Channel rename for ${channel.name} (${channel.id}) can't be done!`
                        );
                        return;
                    }
                    console.log(
                        `id=${interaction.id} | Renaming channel ${channel.name} (${channel.id}) to ${item.value}`
                    );
                    channel.edit({"name": item.value});
                }
                else if (item.type === "reply") {
                    replyStack.push(item.value);
                }
            });
            if (replyStack.length) {
                await interaction.reply(replyStack.join("\n").substring(0, 2001));
            }
            else {
                await interaction.reply("I did the thing! :3");
            }
        }
    })
    .catch(async (error) => {
        try {
            let replyOneLiner = toOneLiner(error.response.data);
            console.error(`id=${interaction.id} status=${error.response.status} | ${replyOneLiner}`);
            if (error.response.data.length) {
                await interaction.reply(error.response.data.map(item => item.value).join("\n"));
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
