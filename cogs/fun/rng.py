#!/usr/bin/env python3
# pylint: disable=C0103

"""Commands that invoke random things, part 1."""

import random
import re

from sailor import commands, exceptions

REGEX_DND = "[0-9]+[dD][0-9]+"
REGEX_DND_SPLIT = "[dD]"
REGEX_OBJECT_DND = re.compile(REGEX_DND)

MAX_ROLLS = 20
MAX_ROLL_SIZE = 30
MAX_DIE_SIZE = 2000

systemrandom = random.SystemRandom()


def trim_expressions(*expressions):
    """Remove all expressions from a list that don't match D&D syntax."""
    expressions = [e for e in expressions if REGEX_OBJECT_DND.fullmatch(e)]
    return expressions


def parse_roll(expression):
    """Convert a D&D roll expression into a tuple of format (die_count, die_size)."""
    expression_parts = re.split(REGEX_DND_SPLIT, expression)
    roll_ = tuple(int(value) for value in expression_parts)
    return roll_


def generate_roll(die_count, die_size):
    """Given an amount of dice and the number of sides per die, simulate a dice roll and return
    a list of ints representing the outcome values.
    """
    roll_ = [systemrandom.randint(1, die_size) for times in range(0, die_count)]
    return roll_


def parse_rolls(*expressions, **kwargs):
    """Given a list of D&D roll expressions, generate a series of rolls."""

    if not expressions:
        return []

    max_rolls = kwargs["max_rolls"]
    max_roll_size = kwargs["max_roll_size"]
    max_die_size = kwargs["max_die_size"]

    rolls = []

    expressions = trim_expressions(*expressions)

    for expression in expressions[:max_rolls]:

        roll_ = parse_roll(expression)

        if roll_[0] > max_roll_size or roll_[1] > max_die_size:
            continue

        elif roll_[1] > 1 and roll_[0] >= 1:
            outcome = generate_roll(roll_[0], roll_[1])
            rolls.append(f"{expression}: {outcome} ({sum(outcome)})")

    return rolls


@commands.cooldown(6, 12)
@commands.command(aliases=["cflip", "coinflip"])
async def coin(event):
    """Flip a coin."""
    choice = systemrandom.choice(["Heads!", "Tails!"])
    await event.reply(choice)


@commands.cooldown(6, 12)
@commands.command()
async def roll(event, *expressions):
    """Roll some dice, using D&D syntax.

    Examples:
    roll 5d6 - Roll five six sided dice.
    roll 1d20 2d8 - Roll one twenty sided die, and two eight sided dice.
    """

    rolls = parse_rolls(*expressions,
                        max_rolls=MAX_ROLLS,
                        max_roll_size=MAX_ROLL_SIZE,
                        max_die_size=MAX_DIE_SIZE)

    if rolls:
        roll_join = "\n".join(rolls)
        await event.reply(event.f.codeblock(roll_join))

    else:
        raise exceptions.UserInputError(("No valid rolls supplied. "
                                         f"Please use D&D format, e.g. 5d6.\n"
                                         "Individual rolls cannot have more than "
                                         f"{MAX_ROLL_SIZE} dice, and individual dice cannot "
                                         f"have more than {MAX_DIE_SIZE} sides."))
