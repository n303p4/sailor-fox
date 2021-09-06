"""
An HTTP service made using sailor's command handler.

Requires Python 3.6+ and aiohttp.
"""

# pylint: disable=invalid-name

import hashlib
import json
import logging
import sys
import time

from aiohttp import web
import sailor

from sailor_fox import ProcessorWithConfig

logging.basicConfig(format="%(asctime)-12s %(levelname)s %(message)s")
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)


def to_one_liner(text: str, max_length: int = 75):
    """Truncates a string to a single line for logging"""
    one_liner = " ".join(text.split("\n"))
    if len(one_liner) > max_length:
        one_liner = f"{one_liner[:max_length-1]}…"
    if not one_liner:
        one_liner = "<empty>"
    return one_liner


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
            for alias in command.aliases:
                command_list[alias] = command.help
        return web.json_response(command_list)

    @routes.post("/")
    async def on_message(request):
        """Accept incoming messages and forward them to the processor."""

        options = await request.json()

        request_id = str(options.get("id", hashlib.md5(bytes(str(time.time()), encoding="utf-8")).hexdigest()))
        message = str(options.get("message", ""))
        is_owner = options.get("is_owner", False)
        character_limit = options.get("character_limit", 2000)
        format_name = str(options.get("format_name"))

        logger.info(
            "id=%s isOwner=%s characterLimit=%s formatName=%s | %s",
            request_id,
            is_owner,
            character_limit,
            format_name,
            to_one_liner(message)
        )

        error_messages = []

        if not message.strip():
            error_messages.append("Message cannot be only whitespace.")
        if not isinstance(is_owner, bool):
            error_messages.append("is_owner must be boolean.")
        if not isinstance(character_limit, int):
            error_messages.append("character_limit must be integer.")

        if error_messages:
            for error_message in error_messages:
                logger.error("id=%s | %s", request_id, error_message)
            return web.Response(
                text=json.dumps(error_messages),
                content_type="application/json",
                status=400
            )

        reply_stack = []

        async def append_to_message_stack(reply_contents: str):
            logger.info("id=%s | %s", request_id, to_one_liner(reply_contents))
            reply_stack.append(reply_contents.strip())

        try:
            await processor.process(
                message,
                character_limit=character_limit,
                format_name=format_name,
                is_owner=is_owner,
                reply_with=append_to_message_stack
            )
        except (sailor.exceptions.CommandError, sailor.exceptions.CommandProcessorError) as error:
            logger.error("id=%s | %s", request_id, to_one_liner(str(error)))
            return web.Response(
                text=json.dumps([str(error)]),
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
    web.run_app(app, port=processor.config.get("http_port", 9980))


if __name__ == "__main__":
    main()
