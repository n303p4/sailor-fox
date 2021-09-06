"""A Magic 8-Ball command."""

# pylint: disable=invalid-name

import secrets

from sailor import commands


ANSWERS = [
    "It it certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",

    "Reply hazy try again.",
    "Ask again later.",
    "Better not to tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",

    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]
ANSWERS_KITSUCHAN = [
    "Yay!",
    "🦊",
    "🌣 :3",
    "👏",
    "Kon kon!",
    "+1",
    "Awau! :3",
    "👍",
    "Yes. :3",
    ":3",

    "Awau? o.o",
    "Ask again later?",
    "/mobileshrug",
    "Don't know? :<",
    "Kon kon kon.",

    "Awau. :<",
    "Get bent. :3",
    "No. :<",
    "👎",
    "RIP"
]


@commands.cooldown(6, 12)
@commands.command(name="8ball", aliases=["eightball"])
async def eightball_(event):
    """Ask the Magic 8-Ball a question."""
    choice = secrets.choice(ANSWERS)
    await event.reply(f"🎱 {choice}")


@commands.cooldown(6, 12)
@commands.command(aliases=["kitsuball"])
async def kball(event):
    """Ask the Magic 8-Ball a question, with added Kitsuchan replies."""
    choice = secrets.choice(ANSWERS + ANSWERS_KITSUCHAN)
    await event.reply(f"🎱 {choice}")
