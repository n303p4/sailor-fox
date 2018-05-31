#!/usr/bin/env python3
# pylint: disable=C0103

"""An assorted collection of meme commands."""

import asyncio
import random

import sailor

SUMMONABLES = [
    ("Red-Eyes Black Dragon", "https://i.imgur.com/MiWwmqq.png"),
    ("Blue-Eyes White Dragon", "https://i.imgur.com/7LVixO3.png"),
    ("Exodia the Forbidden One", "https://i.imgur.com/wHWP34x.png"),
    ("Fox Fire", "https://i.imgur.com/xUIQmwa.png"),
    ("Bujingi Fox", "https://i.imgur.com/vFWak5N.png"),
    ("Lunalight Crimson Fox", "https://i.imgur.com/ReMqPsa.png"),
    ("Majespecter Fox - Kyubi", "https://i.imgur.com/5Yu8KJ7.png")
]
PLAY_MESSAGES = [
    "Play with me? o.o",
    "Yay, let's play! Try using the help command for a list of commands~ :3"
]

systemrandom = random.SystemRandom()


@sailor.commands.cooldown(6, 12)
@sailor.command()
async def play(event):
    """Play a game!"""
    message = systemrandom.choice(PLAY_MESSAGES)
    await event.reply(message)


@sailor.commands.cooldown(6, 12)
@sailor.command(name="np", aliases=["noproblem"])
async def np_(event):
    """No problem!"""
    await event.reply("No problem! :3")


@sailor.commands.cooldown(6, 12)
@sailor.command()
async def pause(event):
    """Pause for a bit."""
    await event.reply("...")
    await asyncio.sleep(5)
    await event.reply("...? o.o")


@sailor.commands.cooldown(6, 12)
@sailor.command()
async def summon(event):
    """Summon a monster!"""
    choice = systemrandom.choice(SUMMONABLES)
    name = choice[0]
    image = choice[1]
    await event.reply(f"I-I summon {name}! o.o\n{image}")
