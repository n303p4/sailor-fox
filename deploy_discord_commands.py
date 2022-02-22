"""Deploy sailor-fox slash command. Just one."""

# pylint: disable=invalid-name

import aiohttp
import discord

from sailor_fox.processor import ProcessorWithConfig
from sailor_fox.helpers import create_logger

logger = create_logger(__name__)


def main():
    """Factory that creates a Discord client and uses it to create a single application command."""

    client = discord.Client()
    processor = ProcessorWithConfig(loop=client.loop)
    processor.load_config()

    discord_slash_prefix = processor.config.get("discord_slash_prefix", "")
    assert isinstance(discord_slash_prefix, str) \
           and discord_slash_prefix.replace("_", "").isalnum() \
           and len(discord_slash_prefix) <= 32, \
           "In config.json, discord_slash_prefix must be a 1-32 character alphanumeric string; _- are also allowed."

    @client.event
    async def on_ready():
        """When ready, deploy command."""

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

        await client.close()

    client.run(processor.config["discord_token"])


if __name__ == "__main__":
    main()
