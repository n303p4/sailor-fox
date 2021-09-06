"""An HTTP service made using sailor's command handler.

Requires Python 3.6+ and aiohttp.
"""

# pylint: disable=invalid-name

import json
import logging
import sys

from aiohttp import web
import sailor

from sailor_fox import ProcessorWithConfig

logging.basicConfig(format="%(asctime)-12s %(levelname)s %(message)s")
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)


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

        form_data = await request.json()

        format_name = form_data.get("format_name")
        is_owner = form_data.get("is_owner", False)
        message = form_data.get("message", "")

        if not message.strip():
            return web.Response(
                text=json.dumps(["Invalid message"]),
                content_type="application/json",
                status=400
            )

        reply_stack = []

        async def append_to_message_stack(reply_contents):
            reply_stack.append(reply_contents.strip())

        try:
            await processor.process(
                message,
                format_name=format_name,
                is_owner=is_owner,
                reply_with=append_to_message_stack
            )
        except (sailor.exceptions.CommandError, sailor.exceptions.CommandProcessorError) as error:
            return web.Response(
                text=json.dumps([str(error)]),
                content_type="application/json",
                status=500
            )

        return web.Response(
            text=json.dumps(reply_stack),
            content_type="application/json",
        )

    processor.load_config()

    assert (isinstance(processor.config.get("module_blocklist", []), list)), "Blocklist must be a list."

    if processor.config.get("description"):
        processor.description = processor.config["description"]

    processor.add_modules_from_dir("cogs", blocklist=processor.config.get("module_blocklist", []))

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=processor.config.get("http_port", 9980))


if __name__ == "__main__":
    main()
