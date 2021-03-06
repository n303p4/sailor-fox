"""Manage and activate custom commands.

These can be potentially dangerous! Be careful out there.
"""

from copy import deepcopy
import re
import secrets
from urllib.parse import urljoin, quote_plus

from bs4 import BeautifulSoup
from sailor import commands
from sailor.exceptions import CommandNotFound, UserInputError, NotBotOwner
from sailor.web_exceptions import WebAPIUnreachable, WebAPIInvalidResponse, WebAPINoResultsFound

from sailor_fox.helpers import FancyMessage

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.105 "
              "Safari/537.36")
HEADERS = {"User-Agent": USER_AGENT}


async def _execute_json_token(session, response_cache, token, *, headers: dict = None):
    if not headers:
        headers = HEADERS
    json_address, source_url = token[5:].split("|", 1)
    if source_url in response_cache:
        json_data = response_cache[source_url]
    else:
        async with session.get(source_url, headers=headers, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service=source_url)
            try:
                json_data = await response.json()
            except Exception as error:
                raise WebAPIInvalidResponse(service=source_url) from error
        response_cache[source_url] = json_data
    json_address = json_address.split(".")
    try:
        json_object_at_address = json_data
        for key_or_index in json_address:
            if key_or_index.isdigit():
                key_or_index = int(key_or_index)
            elif isinstance(json_object_at_address, list) and key_or_index.lower() == "random":
                key_or_index = secrets.randbelow(len(json_object_at_address))
            json_object_at_address = json_object_at_address[key_or_index]
    except Exception as error:
        raise WebAPINoResultsFound(message="No results found.") from error
    return json_object_at_address


async def _execute_raw_token(session, response_cache, token, *, headers: dict = None):
    if not headers:
        headers = HEADERS
    source_url = token[4:]
    if source_url in response_cache:
        raw_data = response_cache[source_url]
    else:
        async with session.get(source_url, headers=headers, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service=source_url)
            try:
                raw_data = await response.text()
            except Exception as error:
                raise WebAPIInvalidResponse(service=source_url) from error
        response_cache[source_url] = raw_data
    return raw_data


async def _execute_html_token(session, response_cache, token, *, headers: dict = None):
    if not headers:
        headers = HEADERS
    css_selector, source_url = token[5:].split("|", 1)
    if source_url in response_cache:
        html_data = response_cache[source_url]
    else:
        async with session.get(source_url, headers=headers, timeout=10) as response:
            if response.status >= 400:
                raise WebAPIUnreachable(service=source_url)
            try:
                html_data = await response.text()
            except Exception as error:
                raise WebAPIInvalidResponse(service=source_url) from error
        response_cache[source_url] = html_data
    try:
        soup = BeautifulSoup(html_data, "html.parser")
        tag = secrets.choice(soup.select(css_selector))
    except Exception as error:
        raise WebAPINoResultsFound(message="No results found.") from error
    if tag.name == "a" and tag.get("href") and not tag["href"].startswith("#"):
        return urljoin(source_url, tag["href"])
    if tag.name == "img" and tag.get("src"):
        img_url = urljoin(source_url, tag["src"])
        if tag.get("title"):
            return f"{img_url}\nHovertext: {tag['title']}"
        return img_url
    return tag.text


RE_ARGUMENT = r"{[0-9]+}"
SPECIAL_TOKEN_EXECUTORS = {
    "json|": _execute_json_token,
    "raw|": _execute_raw_token,
    "html|": _execute_html_token
}


def get_special_token_prefix(token: str):
    token_lower = token.lower()
    for prefix in SPECIAL_TOKEN_EXECUTORS:
        if token_lower.startswith(prefix):
            return prefix
    return None


def validate_special_token(token: str):
    if token.count("}") > 1:
        return False
    if token.count("}") == 1 and not token.endswith("}"):
        return False
    return True


def validate_tokens_and_get_prefixes(tokens):
    prefixes = []
    for token in tokens:
        special_token_prefix = get_special_token_prefix(token)
        if special_token_prefix and not validate_special_token(token):
           raise ValueError("Special tokens cannot have arguments anywhere but the end.")
        prefixes.append(special_token_prefix)
    return prefixes


@commands.cooldown(2, 1)
@commands.command(aliases=["cc", "k"])
async def custom(event, name: str = None, *args):
    """Execute a custom command.

    **Example usage**

    * `custom ping`
    * `custom hello world`
    * `custom multiargtest a b c d`
    * `custom ddg "bat eared fox"`
    * `custom xkcd`
    * `custom xkcd 2000`
    * `custom xkcdprev`
    * `custom bb0`
    * `custom bbr`
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

    base_tokens = tuple(custom_command["tokens"])

    # Validation phase
    token_prefixes = validate_tokens_and_get_prefixes(base_tokens)

    # Pre-parsing phase
    if not args:
        args = ("",)

    # Parsing phase
    parsed_tokens = []
    for token_index, (base_token, prefix) in enumerate(zip(base_tokens, token_prefixes)):
        parsed_token = base_token
        if prefix:
            for arg_index, arg in enumerate(args):
                parsed_token = parsed_token.replace(f"{{{arg_index}}}", quote_plus(arg))
        else:
            for arg_index, arg in enumerate(args):
                parsed_token = parsed_token.replace(f"{{{arg_index}}}", arg)
        if re.findall(RE_ARGUMENT, parsed_token):
            raise UserInputError("Command requires at least one more argument.")
        parsed_tokens.append(parsed_token)

    # Execution phase
    executed_tokens = deepcopy(parsed_tokens)
    response_cache = {}
    for index, (parsed_token, prefix) in enumerate(zip(executed_tokens, token_prefixes)):
        if not prefix:
            continue
        executor = SPECIAL_TOKEN_EXECUTORS[prefix]
        try:
            executed_tokens[index] = await executor(event.processor.session, response_cache, parsed_token)
        except WebAPINoResultsFound as error:
            if args[0] == "":
                raise UserInputError("Command requires at least one more argument.") from error
            raise error

    output = " ".join(executed_tokens)

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
    custom_commands = event.processor.config["custom_commands"]
    if not custom_commands:
        await event.reply("No custom commands are registered.")
        return
    message = FancyMessage(event.f, sep="\n\n")
    message.add_line(event.f.bold("List of custom commands:"))
    for name, custom_command in custom_commands.items():
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
    * `custom add hello Hello, {0}!`
    * `custom add multiargtest {0} {1} {2} {3}`
    * `custom add ddg DuckDuckGo search result for {0}: html|a.result-link|https://lite.duckduckgo.com/lite?q={0}`
    * `custom add xkcd html|#ctitle|https://xkcd.com/{0} | "html|#comic img|https://xkcd.com/{0}"`
    * `custom add xkcdprev The second-most recent xkcd comic is html|a[rel=prev]|https://xkcd.com`
    * `custom add bb0 From r/battlebots: json|data.children.0.data.url|https://old.reddit.com/r/battlebots/.json`
    * `custom add bbr From r/battlebots: json|data.children.random.data.url|https://old.reddit.com/r/battlebots/.json`
    """
    if not tokens:
        raise UserInputError("Must provide at least one command token.")
    name = name.lower()
    if name in custom.all_commands:
        raise UserInputError(f"{name} is a reserved name and cannot be used.")
    event.processor.config.setdefault("custom_commands", {})
    if name in event.processor.config["custom_commands"]:
        await event.reply(
            f"Custom command \"{name}\" already exists. Run {event.f.monospace('webhook delete ' + name)} first."
        )
        return
    validate_tokens_and_get_prefixes(tokens)
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
    validate_tokens_and_get_prefixes(tokens)
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
    name = name.lower()
    event.processor.config.setdefault("custom_commands", {})
    if name not in event.processor.config["custom_commands"]:
        raise CommandNotFound(name=f"{name} (custom command)")
    del event.processor.config["custom_commands"][name]
    event.processor.save_config()
    await event.reply(f"Deleted custom command \"{name}\".")
