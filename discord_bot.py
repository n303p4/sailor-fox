"""A basic Discord bot made using sailor's command handler.

Requires Python 3.6+ and discord.py 1.0 or higher.
"""

# pylint: disable=invalid-name

import logging

import discord
import sailor

from sailor_fox import ProcessorWithConfig

logging.basicConfig(format="%(asctime)-12s %(levelname)s %(message)s")
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

client = discord.AutoShardedClient()

processor = ProcessorWithConfig(loop=client.loop)
processor.default_formatter = sailor.discord_helpers.TextFormatter()

prefixes = []


def split_first_word(text, prefixes_):
    """If a text string starts with a substring, return the substring and the text minus the first instance of the
    substring; otherwise return None and the text.
    """
    for prefix in prefixes_:
        if text.startswith(prefix):
            return prefix, text[len(prefix):].lstrip()
    return None, text


@client.event
async def on_ready():
    """Set the bot's playing status to the help command."""
    main_prefix = processor.config.get("prefix", "sf")
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

    prefix, message_text = split_first_word(message.content, prefixes)

    if prefix:
        try:
            await processor.process(message_text, is_owner=is_owner, reply_with=message.channel.send)
        except (sailor.exceptions.CommandError, sailor.exceptions.CommandProcessorError) as error:
            await message.channel.send(str(error))


if __name__ == "__main__":
    processor.load_config()

    assert (isinstance(processor.config.get("discord_token"), str)), "Bot token not valid."
    assert (isinstance(processor.config.get("module_blocklist", []), list)), "blocklist must be a list."

    if processor.config.get("description"):
        processor.description = processor.config["description"]

    processor.add_modules_from_dir("cogs", blocklist=processor.config.get("module_blocklist", []))

    client.run(processor.config["discord_token"])
