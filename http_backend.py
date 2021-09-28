"""
An HTTP service made using sailor's command handler.

Requires Python 3.6+ and aiohttp.
"""

# pylint: disable=invalid-name,broad-except

import hashlib
import json
import sys
import time

from aiohttp import web
import sailor

from sailor_fox.processor import ProcessorWithConfig
from sailor_fox.helpers import create_logger, to_one_liner

logger = create_logger(__name__)


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

        reply_stack = []

        async def append_to_action_stack(reply: str, *, action_type: str = "reply"):
            logger.info("id=%s actionType=%s | %s", request_id, action_type, to_one_liner(reply))
            reply_stack.append(create_action(action_type, reply.strip()))

        async def rename_channel(name: str, *, action_type: str = "rename_channel"):
            logger.info(
                "id=%s actionType=%s channelNewName=%s | Rename requested",
                request_id,
                action_type,
                name
            )
            reply_stack.append(create_action(action_type, name.strip()))

        try:
            await processor.process(
                message,
                character_limit=character_limit,
                format_name=format_name,
                is_owner=is_owner,
                replace_newlines=replace_newlines,
                reply_with=append_to_action_stack,
                channel_name=channel_name,
                rename_channel_with=rename_channel
            )
        except Exception as error:
            logger.error("id=%s | %s", request_id, to_one_liner(str(error)))
            return web.Response(
                text=json.dumps([create_action("reply", str(error))]),
                content_type="application/json",
                status=500
            )

        if not reply_stack:
            logger.info("id=%s | <empty>", request_id)

        return web.Response(
            text=json.dumps(reply_stack),
            content_type="application/json",
        )

    processor.load_config()

    assert (isinstance(processor.config.get("module_blocklist", []), list)), "Blocklist must be a list."

    processor.add_modules_from_dir("cogs", blocklist=processor.config.get("module_blocklist", []))

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=processor.config.get("backend_port_number", 9980))


if __name__ == "__main__":
    main()
