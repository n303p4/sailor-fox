#!/usr/bin/env python3

"""A basic Discord bot made using sailor's command handler.

Requires Python 3.6+ and discord.py rewrite (1.0).
"""

import logging

import discord
from sailor import commands, exceptions
import sailor.formatters.discord

FORMAT = '%(asctime)-12s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

client = discord.AutoShardedClient()

formatter = sailor.formatters.discord.DiscordFormatter()
processor = commands.Processor(loop=client.loop, logout=client.logout,
                               formatter=formatter, config_file="config.json")


@client.event
async def on_ready():
    """Set the bot's playing status to the help command."""
    game = discord.Game(name=f"Type {processor.prefix} help for help!")
    await client.change_presence(activity=game)

@client.event
async def on_message(message):
    """Broadly handle on_message events from Discord."""
    if message.author.bot:  # Ignore other bots.
        return
    # Check if the message author is the bot owner.
    application_info = await client.application_info()
    is_owner = message.author.id == application_info.owner.id
    # Transfer processing to the sailor command handler.
    try:
        await processor.process(message.content, is_owner=is_owner,
                                callback_send=message.channel.send, character_limit=2000)
    except (exceptions.CommandError, exceptions.CommandProcessorError) as error:
        await message.channel.send(error)


if __name__ == "__main__":
    processor.load_config()

    assert (isinstance(processor.config.get("discord_token"), str)), "Bot token not valid."
    assert (isinstance(processor.config.get("module_blacklist", []), list)), \
        "Blacklist must be a list."

    processor.prefix = processor.config.get("prefix", "")
    if processor.config.get("description"):
        processor.description = processor.config["description"]

    processor.add_modules_from_dir("cogs", blacklist=processor.config.get("module_blacklist", []))

    client.run(processor.config["discord_token"])
