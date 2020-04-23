"""Commands inspired by Roadcrosser's bots."""

# pylint: disable=invalid-name

import random

from sailor import commands

systemrandom = random.SystemRandom()

AAA = (
    "a",
    "A",
    "\u3041",
    "\u3042",
    "\u30A1",
    "\u30A2"
)
THROWABLE_OBJECTS = (
    "heart",
    "cat",
    "dog",
    "fox",
    "cookie",
    "croissant",
    "lollipop",
    "book",
    "tangerine"
)


@commands.cooldown(10, 5)
@commands.command(aliases=["aa", "aaa"])
async def a(event):
    """Aaaaaaa!"""
    message = systemrandom.choice(AAA) * systemrandom.randint(10, 200)
    await event.reply(message)


@commands.cooldown(10, 5)
@commands.command(aliases=["snipe"])
async def throw(event, *, someone):
    """Throw something at someone!"""
    hit = systemrandom.randint(0, 5)
    thing = systemrandom.choice(THROWABLE_OBJECTS)
    if hit:
        message = f":{thing}: {someone} got a {thing} thrown at them! :3"
    else:
        message = f":{thing}: You missed! :3"
    await event.reply(message)
