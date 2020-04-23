"""Ping command for a sailor-based bot."""

from sailor import commands


@commands.cooldown(6, 12)
@commands.command()
async def ping(event):
    """Ping the bot."""
    await event.reply(":3")
