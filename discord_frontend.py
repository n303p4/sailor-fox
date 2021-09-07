"""
A Discord frontend for http_backend.py

Requires Python 3.6+ and discord.py 1.0 or higher.
"""

# pylint: disable=invalid-name

import json
import logging
from typing import List

import aiohttp
import async_timeout
import discord

logging.basicConfig(format="%(asctime)-12s %(levelname)s %(message)s")
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)


def to_one_liner(text: str, max_length: int = 75):
    """Truncates a string to a single line for logging"""
    one_liner = " ".join(text.split("\n"))
    if len(one_liner) > max_length:
        one_liner = f"{one_liner[:max_length-1]}…"
    if not one_liner:
        one_liner = "<empty>"
    return one_liner


def get_prefix(text: str, prefixes_: List[str]):
    """
    If a text string starts with a substring, return the substring and the text minus the first instance of the
    substring; otherwise return None and the text.
    """
    for prefix in prefixes_:
        if text.startswith(prefix):
            return prefix, text[len(prefix):].lstrip()
    return None, text


def main():
    """Factory to create and start the bot."""

    with open("config.json") as config_file:
        config = json.load(config_file)
    backend_port_number = config.get("backend_port_number", 9980)
    prefixes = []

    assert (isinstance(config.get("discord_token"), str)), "Bot token not valid."

    client = discord.AutoShardedClient()
    client_session = aiohttp.ClientSession(loop=client.loop)

    @client.event
    async def on_ready():
        """Set the bot's playing status to the help command."""

        main_prefix = config.get("prefix", "")
        prefixes.append(main_prefix)
        prefixes.append(client.user.mention)
        prefixes.append(client.user.mention.replace("@", "@!"))  # Mentions are cursed

        prefix_space = " " if main_prefix and main_prefix[-1].isalnum() else ""
        game = discord.Game(name=f"Type {main_prefix}{prefix_space}help for help!")
        await client.change_presence(activity=game)

    @client.event
    async def on_message(message: discord.Message):
        """Handle on_message events from Discord and forward them to the processor."""

        if message.author.bot:
            return

        prefix, message_text = get_prefix(message.content, prefixes)
        if not prefix or not message_text:
            return

        application_info = await client.application_info()
        is_owner = (message.author.id == application_info.owner.id)

        logger.info(
            "id=%s user=%s userId=%s guild=%s guildId=%s | %s",
            message.id,
            message.author,
            message.author.id,
            message.guild.name,
            message.guild.id,
            to_one_liner(message.content)
        )

        async def send_and_log(reply_contents: str, error: bool = False):
            if error:
                logger.error("id=%s | %s", message.id, to_one_liner(reply_contents))
            else:
                logger.info("id=%s | %s", message.id, to_one_liner(reply_contents))
            await message.channel.send(reply_contents)

        request_body = {
            "id": f"discord:{message.id}",
            "message": message_text,
            "is_owner": is_owner,
            "character_limit": 2000,
            "format_name": "discord"
        }

        try:
            async with async_timeout.timeout(10):
                async with client_session.post(
                    f"http://localhost:{backend_port_number}", json=request_body
                ) as response:
                    reply_stack = await response.json()
                    for reply_contents in reply_stack:
                        await send_and_log(reply_contents, error=(response.status != 200))
        except Exception as error:
            logger.error("id=%s | %s", message.id, to_one_liner(str(error)))
            if isinstance(error, aiohttp.client_exceptions.ClientConnectorError):
                await message.channel.send("My brain stopped working. Please contact my owner. :<")
            else:
                await message.channel.send(str(error))

    client.run(config["discord_token"])


if __name__ == "__main__":
    main()
