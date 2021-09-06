const https = require("https");
const { Client, Intents } = require("discord.js");
const { discord_token, http_port } = require("./config.json");

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

client.once("ready", () => {
	console.log(":3");
});

client.on("interactionCreate", async interaction => {
	if (!interaction.isCommand()) return;

	const { commandName } = interaction;
	const { commandArguments } = await interaction.options.getString("input");
    const data = JSON.stringify({
        "message": `${commandName} ${commandArguments}`,
        "is_owner": false,
        "format_name": "discord"
    });
    const options = {
        hostname: "localhost",
        port: http_port,
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Content-Length": data.length
        }
    };

    const req = https.request(options, res => {
        console.log(`statusCode: ${res.statusCode}`);

        res.on("data", async d => {
            await interaction.reply(d.join("\n"));
        });
    });

    req.on("error", error => {
        console.error(error);
    });

    req.write(data);
    req.end();
});

client.login(discord_token);
