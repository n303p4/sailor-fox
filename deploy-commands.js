// Before running this, ensure that http_backend.py is running

const { SlashCommandBuilder } = require("@discordjs/builders");
const { REST } = require("@discordjs/rest");
const { Routes } = require("discord-api-types/v9");
const request = require("sync-request");
const { discord_client_id, discord_guild_id, discord_token, http_port } = require("./config.json");
const sailorServiceURL = `http://localhost:${http_port}`;

const commands = [];
const serverCommandListResponse = request("GET", sailorServiceURL);
const serverCommandList = JSON.parse(serverCommandListResponse.getBody("utf8"))[0];

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
    );
    commands.push(newCommand.toJSON());
}

const rest = new REST({ version: "9" }).setToken(discord_token);

(async () => {
	try {
		await rest.put(
			Routes.applicationGuildCommands(discord_client_id, discord_guild_id),
			{ body: commands },
		);

		console.log("Successfully registered application commands.");
	} catch (error) {
		console.error(error);
	}
})();
