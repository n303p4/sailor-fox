// discord.js client for http_backend.py

const https = require("https");
const { Client, Intents } = require("discord.js");
const { discord_token, http_port } = require("./config.json");

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

client.once("ready", () => {
	console.log(":3");
});

client.on("interactionCreate", async interaction => {
	if (!interaction.isCommand()) return;

	const commandName = interaction;
	const commandArguments = await interaction.options.getString("input");
    const fullCommand = `${commandName} ${commandArguments}`;

    console.log(`${fullCommand} | ${interaction.user.tag} (${interaction.user.id})`);

    const requestBody = JSON.stringify({
        "message": fullCommand,
        "is_owner": false,
        "format_name": "discord"
    });
    const requestOptions = {
        hostname: "localhost",
        port: http_port,
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Content-Length": requestBody.length
        }
    };

    const request = https.request(requestOptions, (response) => {
        console.log(`sailor service responded with ${response.statusCode}`);
        if (response.statusCode !== 200) {
            return;
        }
        response.on("data", async (messages) => {
            await interaction.reply(messages.join("\n"));
        });
    });

    request.on("error", error => {
        console.error(error);
    });

    request.write(requestBody);
    request.end();
});

client.login(discord_token);
