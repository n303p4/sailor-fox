"""
A Discord frontend for http_backend.py

Requires Python 3.6+ and discord.py 1.0 or higher.
"""

# pylint: disable=invalid-name,broad-except

import json
from typing import List

import aiohttp
import discord

from sailor_fox.helpers import create_logger, to_one_liner

logger = create_logger("discord")


def get_prefix(text: str, prefixes_: List[str]):
    """
    If a text string starts with a substring, return the substring and the text minus the first instance of the
    substring; otherwise return None and the text.
    """
    for prefix in prefixes_:
        if text.startswith(prefix):
            return prefix, text[len(prefix):].lstrip()
    return None, text


async def do_action(action: dict, message: discord.Message, *, is_error: bool = False):
    """Perform a single action requested by the backend."""
    if not isinstance(action.get("type"), str) \
    or not isinstance(action.get("value"), str):
        return
    log_message = f"id={message.id} actionType={action['type']}"
    if action["type"] == "rename_channel":
        log_message += (
            f" channelId={message.channel.id}"
            f" channelOldName={message.channel.name}"
            f" channelNewName={to_one_liner(action['value'])}"
        )
        try:
            await message.channel.edit(name=action["value"])
        except discord.HTTPException as error:
            logger.warning("%s | Rename failed: %s", log_message, error)
        else:
            logger.warning("%s | Rename succeeded", log_message)
    elif action["type"] == "reply":
        log_message += f" | {to_one_liner(action['value'])}"
        if is_error:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        await message.channel.send(action["value"])
    else:
        logger.warning("%s | Unsupported action", log_message)


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

        prefix_or_none, message_text = get_prefix(message.content, prefixes)
        if prefix_or_none is None or not message_text:
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

        request_body = {
            "id": f"discord_classic.py:{message.id}",
            "message": message_text,
            "is_owner": is_owner,
            "character_limit": 2000,
            "format_name": "discord",
            "channel_name": message.channel.name
        }

        try:
            async with client_session.post(
                f"http://localhost:{backend_port_number}",
                json=request_body,
                timeout=10
            ) as response:
                action_stack = await response.json()
            is_error = response.status != 200
            for action in action_stack:
                await do_action(action, message, is_error=is_error)

        except Exception as error:
            logger.error("id=%s | %s", message.id, to_one_liner(str(error)))
            if isinstance(error, aiohttp.client_exceptions.ClientConnectorError):
                await message.channel.send("My brain stopped working. Please contact my owner. :<")
            else:
                await message.channel.send(str(error))

    client.run(config["discord_token"])


if __name__ == "__main__":
    main()
