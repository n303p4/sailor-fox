"""Manage and activate Discord webhooks."""

import secrets

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
async def add(event, name: str, webhook_url: str, *, content: str):
    """Add a Discord webhook. Owner only.

    **Example usage**

    * `webhook add test-webhook https://discord.com/api/webhooks/1234567890/abcdefghijklm Test webhook`
    * `webhook add twitch-webhook https://discord.com/api/webhooks/123456/abcdef I am now streaming live on Twitch!`
    """
    event.processor.config.setdefault("discord_webhooks", {})
    if name in event.processor.config["discord_webhooks"]:
        await event.reply(f"{name} is a webhook that already exists. Run {event.f.monospace('webhook delete')} first.")
        return
    event.processor.config["discord_webhooks"][name] = {
        "webhook_url": webhook_url,
        "content": content
    }
    event.processor.save_config()
    await event.reply(f"Registered webhook \"{name}\".")


@webhook.command(aliases=["aj"])
async def addjson(event, name: str, webhook_url: str, source_url: str, *, json_address: str):
    """Add a Discord webhook based on an JSON source URL. Owner only.
    
    **Example usage**

    * `webhook add battlebots https://webhook-url https://old.reddit.com/r/battlebots/.json data.children.random.data.url`
    """
    event.processor.config.setdefault("discord_webhooks", {})
    if name in event.processor.config["discord_webhooks"]:
        await event.reply(f"{name} is a webhook that already exists. Run {event.f.monospace('webhook delete')} first.")
        return
    event.processor.config["discord_webhooks"][name] = {
        "webhook_url": webhook_url,
        "source_url": source_url,
        "json_address": json_address
    }
    event.processor.save_config()
    await event.reply(f"Registered webhook \"{name}\".")


@webhook.command(aliases=["del", "d", "remove", "rm", "r"])
async def delete(event, name: str):
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
async def post(event, name: str, *, prefix: str = None):
    """Trigger a registered webhook. Owner only.

    Accepts an optional argument `prefix` that will be prepended to the webhook's content.

    **Example usage**

    * `webhook post test-webhook`
    * `webhook post test-webhook Hello!`
    """
    event.processor.config.setdefault("discord_webhooks", {})
    if name not in event.processor.config["discord_webhooks"]:
        await event.reply(f"{name} is not a webhook that exists.")
        return
    webhook = event.processor.config["discord_webhooks"][name]
    webhook_url = webhook["webhook_url"]
    if webhook.get("content"):
        base_content = webhook["content"]
    else:
        source_url = webhook["source_url"]
        async with event.processor.session.get(source_url, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service="Bot owner")
            try:
                response_content = await response.json()
            except Exception as error:
                raise WebAPIInvalidResponse(service="Bot owner") from error
        json_address = webhook["json_address"].split(".")
        json_object_at_address = response_content
        for key_or_index in json_address:
            if key_or_index.isdigit():
                key_or_index = int(key_or_index)
            elif isinstance(json_object_at_address, list) and key_or_index.lower() == "random":
                key_or_index = secrets.randbelow(len(json_object_at_address))
            json_object_at_address = json_object_at_address[key_or_index]
        base_content = json_object_at_address
    if prefix:
        content = f"{prefix} {base_content}"
    else:
        content = str(base_content)
    async with event.processor.session.post(webhook_url, json={"content": content}, timeout=10) as response:
        if response.status >= 400:
            raise WebAPIUnreachable(service="Discord")
    if prefix:
        await event.reply(f"Activated webhook \"{name}\" with prefix {event.f.monospace(prefix)}")
    else:
        await event.reply(f"Activated webhook \"{name}\".")
