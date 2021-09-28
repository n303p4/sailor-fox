"""Edit the title of a channel."""

from sailor import commands


@commands.cooldown(6, 12)
@commands.command(aliases=["cn", "title", "threadname", "tn", "thread"])
async def channelname(ctx, *, channel_name: str):
    """
    Change the name of a channel.

    As it is incredibly abusable, this command should not be used in a public bot, ever.
    """
    await ctx.send(f"**{channel_name}**")
    await ctx.channel.edit(name=channel_name)
