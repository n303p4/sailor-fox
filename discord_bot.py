"""
A Discord client for http_service.py

Requires Python 3.6+ and discord.py 1.0 or higher.
"""

# pylint: disable=invalid-name

import json
import logging

import aiohttp
import async_timeout
import discord

logging.basicConfig(format="%(asctime)-12s %(levelname)s %(message)s")
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

client = discord.AutoShardedClient()
client_session = aiohttp.ClientSession(loop=client.loop)

with open("config.json") as config_file:
    config = json.load(config_file)
http_port = config.get("http_port", 9980)
prefixes = []


def to_one_liner(text, max_length: int = 75):
    """Truncates a string to a single line for logging"""
    one_liner = " ".join(text.split("\n"))
    if len(one_liner) > max_length:
        one_liner = f"{one_liner[:max_length-1]}…"
    if not one_liner:
        one_liner = "<empty>"
    return one_liner


def get_prefix(text, prefixes_):
    """
    If a text string starts with a substring, return the substring and the text minus the first instance of the
    substring; otherwise return None and the text.
    """
    for prefix in prefixes_:
        if text.startswith(prefix):
            return prefix, text[len(prefix):].lstrip()
    return None, text


@client.event
async def on_ready():
    """Set the bot's playing status to the help command."""
    main_prefix = config.get("prefix", "sf")
    prefixes.append(client.user.mention)
    prefixes.append(main_prefix)
    game = discord.Game(name=f"Type {main_prefix} help for help!")
    await client.change_presence(activity=game)


@client.event
async def on_message(message):
    """Handle on_message events from Discord and forward them to the processor."""
    if message.author.bot:
        return

    application_info = await client.application_info()
    is_owner = (message.author.id == application_info.owner.id)

    prefix, message_text = get_prefix(message.content, prefixes)

    if prefix and message_text.strip():
        async def send_and_log(reply_contents, error: bool = False):
            if error:
                logger.error("id=%s | %s", message.id, to_one_liner(reply_contents))
            else:
                logger.info("id=%s | %s", message.id, to_one_liner(reply_contents))
            await message.channel.send(reply_contents)

        request_body = {
            "message": message_text,
            "is_owner": is_owner,
            "character_limit": 2000,
            "format_name": "discord"
        }

        try:
            async with async_timeout.timeout(10):
                async with client_session.post(f"http://localhost:{http_port}", json=request_body) as response:
                    reply_stack = await response.json()
                    for reply_contents in reply_stack:
                        await send_and_log(reply_contents, error=(response.status != 200))
        except Exception as error:
            logger.error("id=%s | %s", message.id, error)
            await message.channel.send(str(error))


if __name__ == "__main__":
    assert (isinstance(config.get("discord_token"), str)), "Bot token not valid."

    client.run(config["discord_token"])
