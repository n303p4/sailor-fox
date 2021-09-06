"""An HTTP service made using sailor's command handler.

Requires Python 3.6+ and aiohttp.
"""

# pylint: disable=invalid-name

import logging

from aiohttp import web
import sailor

from sailor_fox import ProcessorWithConfig


def main():
    """Factory to create and run everything."""

    routes = web.RouteTableDef()

    logging.basicConfig(format="%(asctime)-12s %(levelname)s %(message)s")
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    discord_formatter = sailor.discord_helpers.TextFormatter()

    processor = ProcessorWithConfig()
    processor.register_formatter(discord_formatter, "discord")


    @routes.post("/")
    async def on_message(request):
        """Handle on_message events from Discord and forward them to the processor."""
        form_data = await request.post()

        format_name = form_data.get("format_name")
        is_owner = form_data.get("is_owner", False)
        message = form_data.get("message")

        reply_stack = []

        async def append_to_message_stack(reply_contents):
            reply_stack.append(reply_contents)

        if not message:
            return web.Response(text="Invalid message", status=400)

        try:
            await processor.process(
                message,
                format_name=format_name,
                is_owner=is_owner,
                reply_with=append_to_message_stack
            )
        except (sailor.exceptions.CommandError, sailor.exceptions.CommandProcessorError) as error:
            return web.Response(text=str(error), status=500)

        return web.Response(text="\n".join(reply_stack))

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
