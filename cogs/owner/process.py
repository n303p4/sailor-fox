"""Commands that affect the bot's execution."""

import sys
import os

from sailor import commands


@commands.command(aliases=["exit", "shutdown", "kys"], owner_only=True)
async def halt(event):
    """Halt the bot. Owner only."""
    if event.invoked_with == "kys":
        await event.reply("Dead! x.x")
    else:
        await event.reply("Good night~")
    await event.processor.logout()


@commands.command(owner_only=True)
async def restart(event):
    """Restart the bot. Owner only."""
    await event.reply("I'll be back soon~")
    await event.processor.logout()
    os.execl(sys.executable, sys.executable, *sys.argv)
