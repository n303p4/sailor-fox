#!/usr/bin/env python3

"""Ping command for a sailor-based bot."""

from sailor import commands


@commands.cooldown(6, 12)
@commands.command()
async def ping(ctx):
    """Ping the bot."""
    await ctx.send(":3")
