#!/usr/bin/env python3

"""A command that ships two things together."""

from sailor import commands


@commands.cooldown(6, 12)
@commands.command()
async def ship(ctx, first_item, second_item):
    """Ship two things together."""
    rating = abs(hash(first_item) - hash(second_item)) % 101
    await ctx.send(f"I rate this ship a {rating}/100!")
