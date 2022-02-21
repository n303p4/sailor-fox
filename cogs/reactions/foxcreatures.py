"""Commands that produce fox creatures."""

import random

from sailor import commands
from sailor.exceptions import UserInputError

FOXWHALE = R"""
 /\_/\{0}   ____
/     {1}\_/  / \
| . . {1}     \  \
|  ^  {1} _   /  /
\_____{0}/ \__\_/
""".strip("\n")
FOXSQUID = R"""
  /\_/\
 /     \
 | . . |
 \  ^  /{0}
  |   |
 /// \\\
/||| |||\
|||| ||||
|       |
O       O
""".strip("\n")
FOXASCII = R"""
  /\_/\
 / . . \       ____
/__ ^ __\     /   /
  /__ \      /\/\/
  |  | \    /   /
  |  |  \__/   /
  \__/_/_\____/
""".strip("\n")
FLUFFSAW = R"""
 /\_/\{0}_____
| ˙-˙ {1}\:\_\\
 ˇˇˇˇˇ{2}ˇˇ
""".strip("\n")
FOXINVADER = [
    R" /\_/\  ",
    R"/_˙-˙_\ ",
    R"[/   \] "
]
FOXJELLYFISH = [
    R" /\_/\  ",
    R"| ˙-˙ | ",
    R"/|||||\ "
]
FOXWHALE_EAT = R"""
        /\_/\__________   ____
       / . .           \_/  / \
       ''''''\              \  \
:<>:<  ,,,,,,/          _   /  /
       \_______________/ \__\_/
""".strip("\n")


async def _foxgrid(event, rows, columns, creature_segments):
    """Generic function that generates a grid of creatures."""
    if rows not in range(1, 6):
        raise UserInputError("Rows must be from 1 to 5.")
    if columns not in range(1, 7):
        raise UserInputError("Columns must be from 1 to 6.")
    creatures = []
    for index in range(rows):
        for segment in creature_segments:
            creatures.append(segment*columns)
        if index != rows-1:
            creatures.append("")
    await event.reply(event.f.codeblock("\n".join(creatures)))


@commands.cooldown(4, 1)
@commands.command(aliases=["ftp"])
async def foxtotempole(event):
    """:<:::3<:::>:3><:><><<:3:><>:3:<"""
    fox_totem_pole = ":" + random.choice(["<", "3", ">"]) + "".join(
        random.choices(["<", ":", ">", ":3"], k=random.randint(10, 30))
    )
    await event.reply(fox_totem_pole)


@commands.cooldown(4, 1)
@commands.command(aliases=["fw"])
async def foxwhale(event, length: int = 10):
    """
    The foxwhale, a creature of the ocean.

    You may specify a length - max 20, min 0.
    """
    if length not in range(0, 21):
        raise UserInputError("Length must be from 0 to 20.")
    edge = "_" * length
    spaces = " " * length
    await event.reply(event.f.codeblock(FOXWHALE.format(edge, spaces)))


@commands.cooldown(4, 1)
@commands.command(aliases=["ff"])
async def foxfish(event, length: int = 1):
    """
    Generate a foxfish.

    You may specify a length - max 20, min 0.
    """
    if length not in range(0, 21):
        raise UserInputError("Length must be from 0 to 20.")
    await event.reply(f":<{'='*length}><")


@commands.cooldown(4, 1)
@commands.command(aliases=["fwe"])
async def foxwhaleeat(event):
    """The foxwhale, eating a foxfish."""
    await event.reply(event.f.codeblock(FOXWHALE_EAT))


@commands.cooldown(4, 1)
@commands.command(aliases=["fs"])
async def foxsquid(event, height: int = 1):
    """
    The foxsquid, archenemy of the foxwhale.

    You may specify a height - max 10, min 0.
    """
    if height not in range(0, 11):
        raise UserInputError("Height must be from 0 to 10.")
    neck = "\n  |   |" * height
    await event.reply(event.f.codeblock(FOXSQUID.format(neck)))


@commands.cooldown(4, 1)
@commands.command(aliases=["fa"])
async def foxascii(event):
    """An ASCII fox."""
    await event.reply(event.f.codeblock(FOXASCII))


@commands.cooldown(4, 1)
@commands.command(aliases=["foxsaw", "fsaw"])
async def fluffsaw(event, length: int = 12):
    """
    Generate a fluffsaw, an elegant weapon for a more fluffy age.

    You may specify a length - max 20, min 0.
    """
    if length not in range(0, 21):
        raise UserInputError("Length must be from 0 to 20.")
    await event.reply(event.f.codeblock(FLUFFSAW.format("_"*length, " "*length, "ˇ"*length)))


@commands.cooldown(4, 1)
@commands.command(aliases=["foxinvader", "fi"])
async def foxinvaders(event, rows: int = 3, columns: int = 5):
    """
    Fox invaders from space have arrived!

    You may specify a number of rows - max 5, min 1.
    You may specify a number of columns - max 6, min 1.
    """
    await _foxgrid(event, rows, columns, FOXINVADER)


@commands.cooldown(4, 1)
@commands.command(aliases=["fj"])
async def foxjellyfish(event, rows: int = 1, columns: int = 1):
    """
    The foxjellyfish, squishy fluffy animals that live in the sea.

    You may specify a number of rows - max 5, min 1.
    You may specify a number of columns - max 6, min 1.
    """
    await _foxgrid(event, rows, columns, FOXJELLYFISH)
