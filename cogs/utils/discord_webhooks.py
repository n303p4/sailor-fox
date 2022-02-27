"""Manage and activate Discord webhooks."""

from sailor import commands
from sailor.web_exceptions import WebAPIUnreachable, WebAPIInvalidResponse

from sailor_fox.helpers import FancyMessage


@commands.command(aliases=["wh"], owner_only=True)
async def webhook(event):
    """Parent command for Discord webhooks. Owner only."""
    try:
        await event.processor.all_commands["help"].invoke(event, "webhook")
    except Exception:
        await event.reply(f"Run {event.f.monospace('help webhook')} for more details.")


@webhook.command(name="list", aliases=["ls", "l"])
async def list_(event):
    """List all registered Discord webhooks. Owner only."""
    event.processor.config.setdefault("discord_webhooks", {})
    message = FancyMessage(event.f)
    message.add_line(event.f.bold("List of webhooks:"))
    for name, webhook in event.processor.config["discord_webhooks"].items():
        message.add_field(name=name, value=f"Post {event.f.monospace(webhook[1])} to {webhook[0]}")
    await event.reply(message)


@webhook.command(aliases=["a"])
async def add(event, name: str, url: str, *, content):
    """Add a Discord webhook. Owner only.

    **Example usage**

    * `webhook add test-webhook https://discord.com/api/webhooks/1234567890/abcdefghijklm Test webhook`
    * `webhook add twitch-webhook https://discord.com/api/webhooks/123456/abcdef I am now streaming live on Twitch!`
    """
    event.processor.config.setdefault("discord_webhooks", {})
    if name in event.processor.config["discord_webhooks"]:
        await event.reply(f"{name} is a webhook that already exists. Run {event.f.monospace('webhook delete')} first.")
        return
    event.processor.config["discord_webhooks"][name] = [url, content]
    event.processor.save_config()
    await event.reply(f"Registered webhook \"{name}\".")


@webhook.command(aliases=["del", "d", "remove", "rm", "r"])
async def delete(event, *, name):
    """Delete a Discord webhook by name. Owner only.

    **Example usage**

    * `webhook delete test-webhook`
    """
    event.processor.config.setdefault("discord_webhooks", {})
    if name not in event.processor.config["discord_webhooks"]:
        await event.reply(f"{name} is not a webhook that exists.")
        return
    del event.processor.config["discord_webhooks"][name]
    event.processor.save_config()
    await event.reply(f"Deleted webhook \"{name}\".")


@webhook.command(aliases=["p"])
async def post(event, *, name):
    """Trigger a registered webhook. Owner only.

    **Example usage**

    * `webhook post test-webhook`
    """
    event.processor.config.setdefault("discord_webhooks", {})
    if name not in event.processor.config["discord_webhooks"]:
        await event.reply(f"{name} is not a webhook that exists.")
        return
    url = event.processor.config["discord_webhooks"][name][0]
    content = event.processor.config["discord_webhooks"][name][1]
    async with event.processor.session.post(url, json={"content": content}, timeout=10) as response:
        if response.status >= 400:
            raise WebAPIUnreachable(service="Discord")
    await event.reply(f"Activated webhook \"{name}\".")
