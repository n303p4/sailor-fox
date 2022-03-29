// Discord slash command client for server.py

const assert = require("assert");
const axios = require("axios");
const { Client, Intents } = require("discord.js");

const { discord_slash_prefix, discord_token, discord_owner_ids, port_number } = require("./config.json");
assert.ok(
    typeof discord_slash_prefix === "string" && discord_slash_prefix.match(/^[\w-]{1,32}$/),
    "In config.json, discord_slash_prefix must be a 1-32 character alphanumeric string; _- are also allowed."
);
assert.ok(typeof discord_token === "string", "In config.json, discord_token must be a string.");
assert.ok(
    Array.isArray(discord_owner_ids) && discord_owner_ids.every(userId => typeof userId === "string"),
    "In config.json, discord_owner_ids must be an array of strings."
);
assert.ok(Number.isInteger(port_number), "In config.json, port_number must be an integer.");

const sailorServerURL = `http://localhost:${port_number}`;

const client = new Client({ intents: [ Intents.FLAGS.GUILDS ] });

client.on("ready", onceReady);
client.on("interactionCreate", async (interaction) => {
    try { await onInteractionCreate(interaction); }
    catch {}
});

client.login(discord_token);

// Standard ready message. Also sets playing status
function onceReady() {
    console.info(
        `clientUser=${client.user.tag} ` +
        `clientUserId=${client.user.id}` +
        " | Bot is now online :3"
    );
    updatePlayingStatus();
}

// Update playing status every 30 minutes
function updatePlayingStatus() {
    client.user.setPresence({
        status: "online",
        activities: [{
            name: `Type /${discord_slash_prefix} help for help!`
        }]
    });
    setTimeout(updatePlayingStatus, 1000*60*30);
}

// Command handling
async function onInteractionCreate(interaction) {
    if (!interaction.isCommand()) return;

    await interaction.deferReply();

    let commandArguments = await interaction.options.getString("input", false);
    if (commandArguments === undefined) return await deleteOriginalReply(interaction);

    let channel = interaction.channel;
    let commandName = interaction.commandName;
    let fullCommand;
    if (commandName === discord_slash_prefix) {
        if (commandArguments) fullCommand = commandArguments;
        else return await deleteOriginalReply(interaction);
    }
    else {
        if (commandArguments) fullCommand = `${commandName} ${commandArguments}`;
        else fullCommand = commandName;
    }
    let originalCommand = `/${commandName} ${commandArguments}`;

    console.info(
        `id=${interaction.id} ` +
        `user=${interaction.user.tag} ` +
        `userId=${interaction.user.id} ` +
        `| ${fullCommand}`
    );

    let requestBody = {
        id: `discord.js:${interaction.id}`,
        message: fullCommand,
        is_owner: discord_owner_ids.includes(interaction.user.id),
        character_limit: 2000,
        format_name: "discord"
    }
    if (channel && typeof channel.name === "string") {
        requestBody.channel_name = channel.name;
    }

    axios
        .post(sailorServerURL, requestBody)
        .then(async response => await doActions(response, interaction, channel, false, originalCommand))
        .catch(async error => {
            try { await doActions(error.response, interaction, channel, true, originalCommand); }
            catch {
                let errorMessage;
                if (error.code) errorMessage = `An error occurred: ${error.code}`
                else errorMessage = "An unknown error occurred.";

                console.error(`id=${interaction.id} | ${errorMessage}`);
                if (error.code === "ECONNREFUSED") {
                    await interaction.editReply("My brain stopped working. Please contact my owner. :<");
                }
                else if (error.code !== "ECONNRESET") {
                    await interaction.editReply(errorMessage);
                }
            }
        });
}

// Delete original reply to interaction (assumes reply or deferReply is called already)
async function deleteOriginalReply(interaction) {
    await interaction.editReply("…");
    await interaction.deleteReply();
}

// Truncates a string to a single line for logging
function toOneLiner(string, maxLength=75) {
    let oneLiner = string.split("\n").join(" ");
    if (oneLiner.length > maxLength) {
        oneLiner = oneLiner.substring(0, maxLength-1) + "…";
    }
    if (oneLiner.length === 0) oneLiner = "<empty>";
    return oneLiner;
}

// Execute a single action requested by the server
function doAction(action, interaction, channel, isError=false) {
    if (typeof action.type !== "string" || typeof action.value !== "string") {
        return;
    }
    let logMessage = `id=${interaction.id} actionType=${action.type}`;
    switch (action.type) {
        case "rename_channel":
            if (!channel) {
                console.warn(`${logMessage} | Channel rename can't be done!`);
                return;
            }
            logMessage += (
                ` channelId=${channel.id}` +
                ` channelOldName=${channel.name}` +
                ` channelNewName=${toOneLiner(action.value)}`
            );
            channel.edit({ name: action.value })
                .then(() => console.info(`${logMessage} | Rename succeeded`))
                .catch(error => console.warn(`${logMessage} | Rename failed: ${error}`));
            break;
        case "reply":
            logMessage += ` | ${toOneLiner(action.value)}`;
            if (isError) {
                console.error(logMessage);
                interaction.followUp({ content: action.value, ephemeral: true });
            }
            else {
                console.info(logMessage);
                interaction.followUp(action.value);
            }
            break;
        default:
            console.warn(`${logMessage} | Unsupported action`);
    }
}

// Read over a response with a list of actions and perform the actions in sequence
async function doActions(response, interaction, channel, isError=false, originalCommand=null) {
    if (isError) await deleteOriginalReply(interaction);
    if (response.data.length && response.status !== 404) {
        let numReplies = 0;
        response.data.forEach(action => {
            doAction(action, interaction, channel, isError);
            if (action.type === "reply") numReplies++;
        });
        if (numReplies === 0) await deleteOriginalReply(interaction);
    }
    else if (originalCommand) {
        await interaction.followUp({
            content: `\`${originalCommand}\` is not a valid command. Type /${discord_slash_prefix} help for a list of commands.`,
            ephemeral: true
        });
    }
    else {
        await interaction.followUp({
            content: `Not a valid command. Type /${discord_slash_prefix} help for a list of commands.`,
            ephemeral: true
        });
    }
}
