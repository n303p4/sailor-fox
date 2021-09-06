"""A command that sues someone or something."""

# pylint: disable=invalid-name

import re
import secrets

from sailor import commands


@commands.cooldown(6, 12)
@commands.command()
async def sue(event, *, target=""):
    """Sue somebody!

    Example usage:

    * sue
    * sue a person
    """
    conjunctions = " because | for | over "
    parts = [part.strip() for part in re.split(conjunctions, target, 1, re.I)]
    if len(parts) > 1 and parts[1]:
        conjunction = re.search(conjunctions, target, re.I).group(0)
        target = parts[0]
        reason = f"{conjunction}{event.f.bold(parts[1])}"
    else:
        reason = ""
    if target:
        target = f" {target}"
    amount = event.f.bold(f"${secrets.randbelow(999901) + 100}")
    message = f"I'm going to sue{target} for {amount}{reason}!"
    await event.reply(message)
