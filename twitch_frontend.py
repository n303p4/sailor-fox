"""
A Twitch frontend for http_backend.py

Requires Python 3.6 or higher.
"""

# pylint: disable=invalid-name,broad-except

import asyncio
import json
import secrets

import aiohttp
import twitchio

from sailor_fox.helpers import create_logger, get_prefix, to_one_liner

logger = create_logger(__name__)


def main():
    """Factory to create and start the bot."""

    with open("config.json") as config_file:
        config = json.load(config_file)

    token = config.get("twitch_token")
    assert isinstance(token, str), "OAuth token not valid."

    backend_port_number = config.get("backend_port_number", 9980)
    prefix = str(config.get("prefix", ""))

    client = twitchio.Client(token, initial_channels=config.get("twitch_channels", []))
    client_session = aiohttp.ClientSession(loop=client.loop)

    @client.event()
    async def event_ready():
        """Bot has logged in."""
        logger.info("Logged in as %s", client.nick)

    @client.event()
    async def event_message(message: twitchio.Message):
        """Handle on_message events from Discord and forward them to the processor."""

        prefix_or_none, message_text = get_prefix(message.content, prefix)
        if prefix_or_none is None or not message_text:
            return

        tags = message.tags or {}

        message_id = tags.get("id", secrets.token_hex(16))
        author_id = tags.get("user-id", "unknown")

        is_owner = (author_id == config.get("twitch_owner_id"))

        logger.info(
            "id=%s user=%s userId=%s channel=%s | %s",
            message_id,
            tags.get("display-name", "unknown"),
            author_id,
            message.channel.name,
            to_one_liner(message.content)
        )

        request_body = {
            "id": f"twitchpy:{message_id}",
            "message": message_text,
            "is_owner": is_owner,
            "character_limit": 500,
            "replace_newlines": True
        }

        try:
            async with client_session.post(
                f"http://localhost:{backend_port_number}",
                json=request_body,
                timeout=10
            ) as response:
                reply_stack = await response.json()
            error = response.status != 200
            for reply in reply_stack:
                if error:
                    logger.error("id=%s | %s", message_id, to_one_liner(reply))
                else:
                    logger.info("id=%s | %s", message_id, to_one_liner(reply))
                await message.channel.send(reply)
                # Hardcode ratelimit for now
                if len(reply_stack) > 1:
                    await asyncio.sleep(2)

        except Exception as error:
            logger.error("id=%s | %s", message_id, to_one_liner(str(error)))
            if isinstance(error, aiohttp.client_exceptions.ClientConnectorError):
                await message.channel.send("My brain stopped working. Please contact my owner. :<")
            else:
                await message.channel.send(str(error))

    client.run()


if __name__ == "__main__":
    main()
