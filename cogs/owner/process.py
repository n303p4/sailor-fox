"""Commands that affect the bot's execution."""

from sailor import commands


@commands.command(aliases=["exit", "shutdown", "kys"], owner_only=True)
async def halt(event):
    """Halt the bot. Owner only."""

    if event.invoked_with == "kys":
        await event.reply("Dead! x.x")
    else:
        await event.reply("Good night~")

    def logout():
        event.processor.loop.create_task(event.processor.logout())

    event.processor.loop.call_later(1, logout)
