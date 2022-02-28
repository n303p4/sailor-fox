"""Manage and activate Discord webhooks."""

from copy import deepcopy
import secrets

from bs4 import BeautifulSoup
from sailor import commands
from sailor.exceptions import UserInputError, NotBotOwner
from sailor.web_exceptions import WebAPIUnreachable, WebAPIInvalidResponse

from sailor_fox.helpers import FancyMessage


async def _handle_json_token(session, response_cache, token):
    json_address, source_url = token[5:].split(":", 1)
    if source_url in response_cache:
        json_data = response_cache[source_url]
    else:
        async with session.get(source_url, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service=source_url)
            try:
                json_data = await response.json()
            except Exception as error:
                raise WebAPIInvalidResponse(service=source_url) from error
        response_cache[source_url] = json_data
    json_address = json_address.split(".")
    json_object_at_address = json_data
    for key_or_index in json_address:
        if key_or_index.isdigit():
            key_or_index = int(key_or_index)
        elif isinstance(json_object_at_address, list) and key_or_index.lower() == "random":
            key_or_index = secrets.randbelow(len(json_object_at_address))
        json_object_at_address = json_object_at_address[key_or_index]
    return json_object_at_address


async def _handle_raw_token(session, response_cache, token):
    source_url = token[4:]
    if source_url in response_cache:
        raw_data = response_cache[source_url]
    else:
        async with session.get(source_url, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service=source_url)
            try:
                raw_data = await response.text()
            except Exception as error:
                raise WebAPIInvalidResponse(service=source_url) from error
        response_cache[source_url] = raw_data
    return raw_data


async def _handle_html_token(session, response_cache, token):
    css_selector, source_url = token[5:].split(":", 1)
    if source_url in response_cache:
        html_data = response_cache[source_url]
    else:
        async with session.get(source_url, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service=source_url)
            try:
                html_data = await response.text()
            except Exception as error:
                raise WebAPIInvalidResponse(service=source_url) from error
        response_cache[source_url] = html_data
    soup = BeautifulSoup(html_data, "html.parser")
    element = secrets.choice(soup.select(css_selector))
    return element.text


@commands.cooldown(2, 1)
@commands.command(aliases=["cc", "c"])
async def custom(event, name: str = None):
    """Execute a custom command.

    **Example usage**

    * `custom bb`
    """
    event.processor.config.setdefault("custom_commands", {})
    if name:
        name = name.lower()
    if name not in event.processor.config["custom_commands"]:
        try:
            await event.processor.all_commands["help"].invoke(event, "custom")
        except Exception:
            await event.reply(f"Run {event.f.monospace('help custom')} for more details.")
        return
    custom_command = event.processor.config["custom_commands"][name]
    discord_webhook_url = custom_command.get("discord_webhook_url")
    if discord_webhook_url and not event.is_owner:
        raise NotBotOwner("Webhook custom commands can only be used by a bot owner.")
    tokens = deepcopy(custom_command["tokens"])
    response_cache = {}
    for index, token in enumerate(tokens):
        token_lower = token.lower()
        if token_lower.startswith("json:"):
            tokens[index] = await _handle_json_token(event.processor.session, response_cache, token)
        elif token_lower.startswith("raw:"):
            tokens[index] = await _handle_raw_token(event.processor.session, response_cache, token)
        elif token_lower.startswith("html:"):
            tokens[index] = await _handle_html_token(event.processor.session, response_cache, token)
    output = " ".join(tokens)
    if discord_webhook_url:
        async with event.processor.session.post(discord_webhook_url, json={"content": output}, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service="Discord")
        await event.reply(f"Activated Discord webhook command \"{name}\".")
    else:
        await event.reply(output)


@commands.cooldown(2, 1)
@custom.command(name="list", aliases=["ls", "l"])
async def list_(event):
    """List all registered custom commands."""
    event.processor.config.setdefault("custom_commands", {})
    message = FancyMessage(event.f, sep="\n\n")
    message.add_line(event.f.bold("List of custom commands:"))
    for name, custom_command in event.processor.config["custom_commands"].items():
        if custom_command.get("discord_webhook_url"):
            name += f" (webhook)"
        value = event.f.monospace(" ".join(custom_command.get("tokens", [])))
        message.add_field(name=name, value=value, sep="\n")
    await event.reply(message)


@custom.command(aliases=["a"], owner_only=True)
async def add(event, name: str, *tokens):
    """Add a custom command. Owner only.
    
    **Example usage**

    * `custom add ping Pong! :3`
    * `custom add xkcdtitle html:#ctitle:https://xkcd.com`
    * `custom add bb From r/battlebots: JSON:data.children.random.data.url:https://old.reddit.com/r/battlebots/.json`
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
        "tokens": list(tokens)
    }
    event.processor.save_config()
    await event.reply(f"Added custom command \"{name}\".")


@add.command(aliases=["dw"])
async def discordwebhook(event, name: str, discord_webhook_url: str, *tokens):
    """Add a custom command that POSTs to a Discord webhook. Owner only."""
    if not tokens:
        raise UserInputError("Must provide at least one command token.")
    if not discord_webhook_url.startswith("https://discord.com/api/webhooks/"):
        raise UserInputError("Not a valid Discord webhook URL.")
    name = name.lower()
    event.processor.config.setdefault("custom_commands", {})
    if name in event.processor.config["custom_commands"]:
        await event.reply(
            f"Custom command \"{name}\" already exists. Run {event.f.monospace('webhook delete ' + name)} first."
        )
        return
    event.processor.config["custom_commands"][name] = {
        "discord_webhook_url": discord_webhook_url,
        "tokens": list(tokens)
    }
    event.processor.save_config()
    await event.reply(f"Added custom command \"{name}\".")


@custom.command(aliases=["del", "d", "remove", "rm", "r"], owner_only=True)
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
