#!/usr/bin/env python3

"""A command that ships two things together."""

from sailor import commands


def to_int(string, *, encoding="utf-8", byteorder="big"):
    """Convert a string into a UTF-8 encoded bytestring and then convert that into an integer."""
    return int.from_bytes(bytes(string, encoding), byteorder=byteorder)


@commands.cooldown(6, 12)
@commands.command()
async def ship(ctx, first_item, second_item):
    """Ship two things together."""
    rating = abs(to_int(first_item) - to_int(second_item)) % 101
    await ctx.send(f"I rate this ship a {rating}/100!")
