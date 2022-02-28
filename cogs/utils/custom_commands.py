"""Manage and activate Discord webhooks."""

from copy import deepcopy
import secrets

from sailor import commands
from sailor.exceptions import UserInputError
from sailor.web_exceptions import WebAPIUnreachable, WebAPIInvalidResponse

from sailor_fox.helpers import FancyMessage


@commands.command(aliases=["cc", "c"], owner_only=True)
async def custom(event, name: str = None):
    """Execute a custom command. Owner only.

    **Example usage**

    * `custom bb`
    """
    event.processor.config.setdefault("custom_commands", {})
    if name not in event.processor.config["custom_commands"]:
        try:
            await event.processor.all_commands["help"].invoke(event, "custom")
        except Exception:
            await event.reply(f"Run {event.f.monospace('help custom')} for more details.")
        return
    custom_command = event.processor.config["custom_commands"][name]
    tokens = deepcopy(custom_command["tokens"])
    json_data_cache = {}
    for index, token in enumerate(tokens):
        if not (token.startswith("<") and token.endswith(">")):
            continue
        try:
            source_url, json_address = token[1:-1].split("|")
            if source_url in json_data_cache:
                json_data = json_data_cache[source_url]
            else:
                async with event.processor.session.get(source_url, timeout=10) as response:
                    if response.status >= 400:
                        raise WebAPIUnreachable(service="Bot owner")
                    try:
                        json_data = await response.json()
                    except Exception as error:
                        raise WebAPIInvalidResponse(service="Bot owner") from error
                json_data_cache[source_url] = json_data
            json_address = json_address.split(".")
            json_object_at_address = json_data
            for key_or_index in json_address:
                if key_or_index.isdigit():
                    key_or_index = int(key_or_index)
                elif isinstance(json_object_at_address, list) and key_or_index.lower() == "random":
                    key_or_index = secrets.randbelow(len(json_object_at_address))
                json_object_at_address = json_object_at_address[key_or_index]
            tokens[index] = json_object_at_address
        except Exception:
            continue
    output = " ".join(tokens)
    discord_webhook_url = custom_command.get("discord_webhook_url")
    if discord_webhook_url:
        async with event.processor.session.post(discord_webhook_url, json={"content": output}, timeout=10):
            if response.status >= 400:
                raise WebAPIUnreachable(service="Discord")
        await event.reply(f"Activated Discord webhook command \"{name}\".")
    else:
        await event.reply(output)


@custom.command(name="list", aliases=["ls", "l"])
async def list_(event):
    """List all registered custom commands. Owner only."""
    event.processor.config.setdefault("custom_commands", {})
    message = FancyMessage(event.f, sep="\n\n")
    message.add_line(event.f.bold("List of custom commands:"))
    for name, custom_command in event.processor.config["custom_commands"].items():
        if custom_command.get("discord_webhook_url"):
            name += f" (webhook)"
        value = event.f.monospace(" ".join(custom_command.get("tokens", [])))
        message.add_field(name=name, value=value, sep="\n")
    await event.reply(message)


@custom.command(aliases=["a"])
async def add(event, name: str, *tokens):
    """Add a custom command. Owner only.
    
    **Example usage**

    * `custom add bb From r/battlebots: <https://old.reddit.com/r/battlebots/.json|data.children.random.data.url>`
    """
    if not tokens:
        raise UserInputError("Must provide at least one command token.")
    name = name.lower()
    event.processor.config.setdefault("custom_commands", {})
    if name in event.processor.config["custom_commands"]:
        await event.reply(
            f"Custom command \"{name}\" already exists. Run {event.f.monospace('webhook delete ' + name)} first."
        )
        return
    event.processor.config["custom_commands"][name] = {
        "tokens": tokens
    }
    event.processor.save_config()
    await event.reply(f"Added custom command \"{name}\".")


@add.command(aliases=["dw"])
async def discordwebhook(event, name: str, discord_webhook_url: str, *tokens):
    """Add a custom command that POSTs to a Discord webhook. Owner only."""
    if not tokens:
        raise UserInputError("Must provide at least one command token.")
    name = name.lower()
    event.processor.config.setdefault("custom_commands", {})
    if name in event.processor.config["custom_commands"]:
        await event.reply(
            f"Custom command \"{name}\" already exists. Run {event.f.monospace('webhook delete ' + name)} first."
        )
        return
    event.processor.config["custom_commands"][name] = {
        "discord_webhook_url": discord_webhook_url,
        "tokens": tokens
    }
    event.processor.save_config()
    await event.reply(f"Added custom command \"{name}\".")


@custom.command(aliases=["del", "d", "remove", "rm", "r"])
async def delete(event, name: str):
    """Delete a custom command by name. Owner only.

    **Example usage**

    * `custom delete bb`
    """
    event.processor.config.setdefault("custom_commands", {})
    if name not in event.processor.config["custom_commands"]:
        await event.reply(f"\"{name}\" is not a valid custom command.")
        return
    del event.processor.config["custom_commands"][name]
    event.processor.save_config()
    await event.reply(f"Deleted custom command \"{name}\".")
