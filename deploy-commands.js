// Before running this, ensure that http_backend.py is running

const { SlashCommandBuilder } = require("@discordjs/builders");
const { DiscordInteractions } = require("slash-commands");
const request = require("sync-request");
const { discord_client_id, discord_guild_id, discord_token, discord_public_key, backend_port_number } = require("./config.json");
const sailorServiceURL = `http://localhost:${backend_port_number}`;

const commands = [];
const serverCommandListResponse = request("GET", sailorServiceURL);
const serverCommandList = JSON.parse(serverCommandListResponse.getBody("utf8"));

for (let commandName in serverCommandList) {
    if (!serverCommandList.hasOwnProperty(commandName)) {
        continue;
    }
    if (!commandName.substring(0, 1).match(/[A-Za-z0-9]/)) {
        continue;
    }
    let newCommand = new SlashCommandBuilder()
    .setName(commandName)
    .setDescription(serverCommandList[commandName].substring(0, 100).split("\n")[0])
    .addStringOption(option =>
        option.setName("input")
            .setDescription(`Run /help ${commandName} for more details`)
    ).toJSON();
    commands.push(newCommand);
}

const interaction = new DiscordInteractions({
    applicationId: discord_client_id,
    authToken: discord_token,
    publicKey: discord_public_key,
});

interaction
    .createApplicationCommand(commands[0], discord_guild_id)
    .then(console.log)
    .catch(console.error);