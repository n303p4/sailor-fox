"""
Change the name of a channel.

As it is incredibly abusable, this command should not be used in a public bot, ever.
"""

from sailor import commands


@commands.cooldown(6, 12)
@commands.command(aliases=["cn", "title", "threadname", "tn", "thread"])
async def channelname(event, *, channel_name: str):
    """Change the name of a channel."""
    await event.reply(event.f.bold(channel_name))
    await event.channel.edit(name=channel_name)
