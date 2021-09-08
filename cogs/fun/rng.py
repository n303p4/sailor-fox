"""Commands that invoke random things, part 1."""

# pylint: disable=invalid-name

import re
import secrets

from sailor import commands
from sailor.exceptions import UserInputError


REGEX_DND = r"([1-9][0-9]*)?[dD]([1-9][0-9]*)([\+\-][0-9]+)?"
REGEX_OBJECT_DND = re.compile(REGEX_DND)

MAX_ROLLS = 20
MAX_DICE = 20
MAX_SIDES = 2000
MAX_MODIFIER = 2000


def trim_expressions(*expressions):
    """Remove all expressions from a list that don't match D&D syntax."""
    matches = [
        m for m in [REGEX_OBJECT_DND.fullmatch(e.replace(" ", "")) for e in expressions] if m
    ]
    return matches


def parse_roll(match):
    """Convert a D&D roll expression into a tuple of format (count, size, modifier)."""
    return tuple(int(g) if isinstance(g, str) else 0 for g in match.groups())


def do_roll(dice: int, sides: int, _: int):
    """Given an amount of dice and the number of sides per die, simulate a dice roll and return
    a list of ints representing the outcome values.

    Modifier is ignored.
    """
    dice = dice or 1
    sides = sides or 1
    values = sorted(((secrets.randbelow(sides) + 1) for _ in range(0, dice)), reverse=True)
    return values


def do_rolls(*expressions, max_rolls: int, max_dice: int, max_sides: int, max_modifier: int):
    """Given a list of D&D roll expressions, generate a series of rolls."""

    rolls = []
    expressions = trim_expressions(*expressions)

    for expression in expressions[:max_rolls]:

        roll = parse_roll(expression)
        modifier = roll[2]

        errors = []
        if roll[0] > max_dice:
            errors.append(f"{roll[0]} > max {max_dice}")
        if roll[1] > max_sides:
            errors.append(f"d{roll[1]} > max d{max_sides}")
        if abs(modifier) > max_modifier:
            errors.append(f"{modifier:+d} > max ±{max_modifier}")
        if errors:
            rolls.append(
                f"{expression.group(0)} :: Invalid roll\n[ {' | '.join(errors)} ]"
            )
            continue

        values = do_roll(*roll)
        outcome = sum(values)
        values_string = f"= ({', '.join(str(v) for v in values)})"

        outcome_string = str(outcome)

        if modifier:
            if modifier > 0:
                outcome_string += f" + {modifier}"
            else:
                outcome_string += f" - {abs(modifier)}"
            outcome_string += f" = {outcome+modifier}"
        rolls.append(
            f"{expression.group(0)} :: {outcome_string}\n{values_string}"
        )

    if len(expressions) > max_rolls:
        rolls.append(f"Some rolls were omitted; max # of rolls allowed at a time is {max_rolls}")

    return rolls


@commands.cooldown(6, 12)
@commands.command(aliases=["cflip", "coinflip"])
async def coin(event):
    """Flip a coin."""
    choice = secrets.choice(["Heads!", "Tails!"])
    await event.reply(choice)


@commands.cooldown(6, 12)
@commands.command(aliases=["randint"])
async def rng(event, start: int, end: int):
    """Random number generator.

    * `start` - The lowest number that can be generated.
    * `end` - The highest number that can be generated.
    """
    if start > end:
        start, end = end, start
    number = secrets.randbelow(end - start + 1) + start
    await event.reply(event.f.codeblock(number))


@commands.cooldown(6, 12)
@commands.command(name="choice", aliases=["choose", "c"])
async def choice_(event, *choices):
    """Choose from various choices. Choices are separated with spaces.

    Multi-word choices should be enclosed in "quotes like this".
    """
    if len(choices) < 2:
        raise UserInputError("You must supply more than one choice.")
    choice = secrets.choice(choices)
    await event.reply(event.f.codeblock(choice))


@commands.cooldown(6, 12)
@commands.command(name="roll")
async def roll_(event, *expressions):
    """Roll some dice, using D&D syntax.

    **Example usage**

    * `roll 5d6+2` - Roll five six sided dice with a modifier of 2.
    * `roll 1d20 2d8` - Roll one twenty sided die, and two eight sided dice.

    Roll outcomes are always sorted in descending order.
    """
    outcomes = do_rolls(
        *expressions,
        max_rolls=MAX_ROLLS,
        max_dice=MAX_DICE,
        max_sides=MAX_SIDES,
        max_modifier=MAX_MODIFIER
    )
    if not outcomes:
        raise UserInputError((
            "No valid rolls supplied. Please use D&D format, e.g. 5d6+2.\n"
            "Individual rolls cannot have more than "
            f"{MAX_DICE} dice, and individual dice must have "
            f"between 1 and {MAX_SIDES} sides inclusive. The "
            f"modifier must not exceed ±{MAX_MODIFIER}"
        ))
    for outcome in outcomes:
        await event.reply(event.f.codeblock(outcome, syntax="asciidoc"))
