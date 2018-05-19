#!/usr/bin/env python3

"""Commands that affect the bot's execution."""

import sys
import os

from sailor import commands


@commands.command(aliases=["exit", "shutdown", "kys"], owner_only=True)
async def halt(ctx):
    """Halt the bot. Owner only."""
    if ctx.invoked_with == "kys":
        await ctx.send("Dead! x.x")
    else:
        await ctx.send("Good night~")
    await ctx.bot.logout()


@commands.command(owner_only=True)
async def restart(ctx):
    """Restart the bot. Owner only."""
    await ctx.send("I'll be back soon~")
    await ctx.bot.logout()
    os.execl(sys.executable, sys.executable, *sys.argv)
