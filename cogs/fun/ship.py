"""A command that ships two things together."""

from sailor import commands


def to_int(string, *, encoding="utf-8", byteorder="big"):
    """Convert a string into a UTF-8 encoded bytestring and then convert that into an integer."""
    return int.from_bytes(string.encode(encoding), byteorder=byteorder)


@commands.cooldown(6, 12)
@commands.command()
async def ship(event, first_item, second_item):
    """Ship two things together."""
    rating = abs(to_int(first_item) - to_int(second_item)) % 101
    await event.reply(f"I rate this ship a {rating}/100!")
