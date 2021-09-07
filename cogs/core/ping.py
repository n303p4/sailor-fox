"""Ping command for a sailor-based bot."""

from sailor import commands


@commands.cooldown(6, 12)
@commands.command()
async def ping(event):
    """
    Ping the bot.

    The main purpose of this command is debugging, to make sure the bot is alive.
    """
    await event.reply(":3")
