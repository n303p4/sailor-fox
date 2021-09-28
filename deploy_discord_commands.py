"""Deploy sailor-fox slash command. Pretty much just a hack."""

# pylint: disable=invalid-name

import asyncio
import sys

import aiohttp
import discord

from sailor_fox.processor import ProcessorWithConfig
from sailor_fox.helpers import create_logger

logger = create_logger(__name__)


def main():
    """Factory that creates a Discord client and uses it to register slash commands."""

    client = discord.Client()
    processor = ProcessorWithConfig(loop=client.loop)
    processor.load_config()
    assert (isinstance(processor.config.get("module_blocklist", []), list)), "Blocklist must be a list."
    processor.add_modules_from_dir("cogs", blocklist=processor.config.get("module_blocklist", []))

    @client.event
    async def on_ready():
        """When ready, deploy commands."""

        if not processor.session:
            processor.session = aiohttp.ClientSession(loop=processor.loop)

        guild_id = processor.config.get("discord_guild_id")
        if guild_id:
            url = f"https://discord.com/api/v8/applications/{client.user.id}/guilds/{guild_id}/commands"
        else:
            url = f"https://discord.com/api/v8/applications/{client.user.id}/commands"

        headers = {
            "Authorization": f"Bot {processor.config['discord_token']}"
        }

        for index, command in enumerate(processor.commands.values(), start=1):
            request_payload = {
                "name": command.name,
                "type": 1,
                "description": " ".join(command.help.split("\n"))[:100][0],
                "options": [
                    {
                        "name": "input",
                        "description": f"Run /help {command.name} for more details",
                        "type": 3,
                        "required": False
                    }
                ]
            }
            logger.info("Registering %s (%s of %s)...", command.name, index, len(processor.commands))
            async with processor.session.post(url, headers=headers, json=request_payload) as response:
                if response.status >= 400:
                    logger.error(response)
                    logger.warning("Command not registered (HTTP %s)", response.status)
                else:
                    logger.info("Command registered (HTTP %s)", response.status)
            await asyncio.sleep(5)

        request_payload = {
            "name": processor.config["discord_slash_prefix"],
            "type": 1,
            "description": "Run a command",
            "options": [
                {
                    "name": "input",
                    "description": "The command you want to run, plus any optional arguments",
                    "type": 3,
                    "required": True
                }
            ]
        }
        logger.info("Registering %s...", processor.config["discord_slash_prefix"])
        async with processor.session.post(url, headers=headers, json=request_payload) as response:
            if response.status >= 400:
                logger.error(response)
                logger.warning("Command not registered (HTTP %s)", response.status)
            else:
                logger.info("Command registered (HTTP %s)", response.status)

        await processor.session.close()

        sys.exit(0)

    client.run(processor.config["discord_token"])


if __name__ == "__main__":
    main()
