#!/usr/bin/env python3

"""Bot information command."""

import resource
import sys

import sailor
from sailor import commands


@commands.cooldown(6, 12)
@commands.command(aliases=["about", "stats"])
async def info(event):
    """Display some basic information about the bot, such as memory usage."""
    usage_memory = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000, 2)
    message = [
        event.processor.name,
        event.processor.description,
        f"# of commands: {len(event.processor.commands)}",
        "Python: {0}.{1}.{2}".format(*sys.version_info),
        f"sailor: {sailor.version}",
        f"Cookies eaten: {usage_memory} megabites"
    ]
    message = event.f.codeblock("\n".join([str(line) for line in message if len(line) > 0]))

    await event.reply(message)
