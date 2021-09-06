"""Commands inspired by Roadcrosser's bots."""

# pylint: disable=invalid-name

import secrets

from sailor import commands

AAA = (
    "a",
    "A",
    "\u3041",
    "\u3042",
    "\u30A1",
    "\u30A2"
)
THROWABLE_OBJECTS = {
    "heart": "❤",
    "cat": "🐱",
    "dog": "🐶",
    "fox": "🦊",
    "cookie": "🍪",
    "croissant": "🥐",
    "lollipop": "🍭",
    "book": "📕",
    "tangerine": "🍊"
}


@commands.cooldown(10, 5)
@commands.command(aliases=["aa", "aaa"])
async def a(event):
    """Aaaaaaa!"""
    message = secrets.choice(AAA) * (secrets.randbelow(191) + 10)
    await event.reply(message)


@commands.cooldown(10, 5)
@commands.command(aliases=["snipe"])
async def throw(event, *, someone):
    """Throw something at someone!"""
    hit = secrets.randbelow(6)
    thing, emoji = secrets.choice(tuple(THROWABLE_OBJECTS.items()))
    if hit:
        message = f"{emoji} {someone} got a {thing} thrown at them! :3"
    else:
        message = f"{emoji} You missed! :3"
    await event.reply(message)
