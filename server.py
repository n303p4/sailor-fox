"""
An HTTP service made using sailor's command handler.

Requires Python 3.6+ and aiohttp.
"""

# pylint: disable=invalid-name,broad-except

import asyncio
import hashlib
import json
import sys
import time

from aiohttp import web
import sailor
from sailor.channel import AbstractChannel
from sailor.exceptions import NotCoroutine

from sailor_fox.processor import ProcessorWithConfig
from sailor_fox.helpers import create_logger, to_one_liner

logger = create_logger(__name__)


class HTTPResponseChannel(AbstractChannel):
    """A simple class that implements AbstractChannel."""

    def __init__(self, **kwargs):
        super(HTTPResponseChannel, self).__init__(**kwargs)
        rename_channel_with = kwargs.get("rename_channel_with")
        if not asyncio.iscoroutinefunction(rename_channel_with):
            raise NotCoroutine(f"{rename_channel_with} is not a coroutine function.")
        self.__rename_channel = kwargs["rename_channel_with"]

    async def edit(self, **kwargs):
        """Reimplement edit command."""
        if "name" in kwargs:
            await self.__rename_channel(kwargs["name"])


def create_action(type_: str, value: str):
    """Create an action for clients to use."""
    return {"type": type_, "value": value}


def main():
    """Factory to create and run everything."""

    discord_formatter = sailor.discord_helpers.TextFormatter()

    processor = ProcessorWithConfig(logout=sys.exit)
    processor.register_formatter(discord_formatter, "discord")

    routes = web.RouteTableDef()

    @routes.get("/")
    async def command_list(_):
        """Return JSON dict of all commands, minus their aliases. Mainly for Discord slash command registration."""
        command_list = {}
        for command in processor.commands.values():
            command_list[command.name] = command.help
        return web.json_response(command_list)

    @routes.post("/")
    async def on_message(request):
        """Accept incoming messages and forward them to the processor."""

        try:
            options = await request.json()
        except json.JSONDecodeError:
            error_message = "Request does not contain valid JSON data."
            logger.error(error_message)
            return web.Response(
                text=json.dumps([create_action("reply", error_message)]),
                content_type="application/json",
                status=400
            )

        request_id = str(options.get("id", hashlib.md5(bytes(str(time.time()), encoding="utf-8")).hexdigest()))
        message = options.get("message")
        if message is None:
            error_message = "message is a required property that is missing."
            logger.error("id=%s | %s", request_id, error_message)
            return web.Response(
                text=json.dumps([create_action("reply", error_message)]),
                content_type="application/json",
                status=400
            )
        message = str(message)
        is_owner = options.get("is_owner", False)
        character_limit = options.get("character_limit", 0)
        format_name = str(options.get("format_name"))
        replace_newlines = options.get("replace_newlines", False)
        channel_name = str(options.get("channel_name", "untitled"))

        logger.info(
            "id=%s isOwner=%s characterLimit=%s formatName=%s replaceNewlines=%s channelName=%s | %s",
            request_id,
            is_owner,
            character_limit,
            format_name,
            replace_newlines,
            channel_name,
            to_one_liner(message)
        )

        error_messages = []

        if not message.strip():
            error_messages.append("message cannot be only whitespace.")
        if not isinstance(is_owner, bool):
            error_messages.append("is_owner must be boolean.")
        if not isinstance(character_limit, int):
            error_messages.append("character_limit must be integer.")
        if not isinstance(replace_newlines, bool):
            error_messages.append("replace_newlines must be boolean.")

        if error_messages:
            for error_message in error_messages:
                logger.error("id=%s | %s", request_id, error_message)
            return web.Response(
                text=json.dumps([create_action("reply", e) for e in error_messages]),
                content_type="application/json",
                status=400
            )

        action_stack = []

        async def reply(reply: str, *, action_type: str = "reply"):
            logger.info("id=%s actionType=%s | %s", request_id, action_type, to_one_liner(reply))
            action_stack.append(create_action(action_type, reply.strip()))

        async def rename_channel(new_channel_name: str, *, action_type: str = "rename_channel"):
            logger.info(
                "id=%s actionType=%s channelNewName=%s | Rename requested",
                request_id,
                action_type,
                to_one_liner(new_channel_name)
            )
            action_stack.append(create_action(action_type, new_channel_name.strip()))

        channel = HTTPResponseChannel(name=channel_name, rename_channel_with=rename_channel)

        try:
            await processor.process(
                message,
                character_limit=character_limit,
                format_name=format_name,
                is_owner=is_owner,
                replace_newlines=replace_newlines,
                reply_with=reply,
                channel=channel
            )
        except Exception as error:
            logger.error("id=%s | %s", request_id, to_one_liner(str(error)))
            if isinstance(error, sailor.exceptions.CommandNotFound):
                status = 404
            else:
                status = 500
            return web.Response(
                text=json.dumps([create_action("reply", str(error))]),
                content_type="application/json",
                status=status
            )

        if not action_stack:
            logger.info("id=%s | <empty>", request_id)

        return web.Response(
            text=json.dumps(action_stack),
            content_type="application/json",
        )

    processor.load_config()

    module_blocklist = processor.config.get("module_blocklist", [])
    assert isinstance(module_blocklist, list) and all(isinstance(m, str) for m in module_blocklist), \
           "module_blocklist must be an array of string."

    assert "port_number" in processor.config, "port_number must be set."
    port_number = processor.config["port_number"]
    assert isinstance(port_number, int), "port_number must be an integer."

    processor.add_modules_from_dir("cogs", blocklist=module_blocklist)

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=port_number)


if __name__ == "__main__":
    main()
