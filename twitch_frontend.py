"""
A Twitch frontend for http_backend.py

Requires Python 3.6 or higher.
"""

# pylint: disable=invalid-name,broad-except

import json
import secrets

import aiohttp
import twitchio

from sailor_fox.helpers import create_logger, get_prefix, to_one_liner

logger = create_logger(__name__)


async def ext_send(session, channel, message_id, reply_stack, *,
                   use_ghostbin: bool = False, url_ghostbin_api: str = "https://ghostbin.com/paste/new"):
    """
    Sends a message normally if it's short enough.
    If use_ghostbin is true and the message is too long, post the message to Ghostbin and sends the link in chat.
    """
    if not reply_stack:
        return
    if len(reply_stack) == 1 or not use_ghostbin:
        await channel.send(reply_stack[0])
        return
    request_body = aiohttp.FormData({
        "text": "\n".join(reply_stack),
        "title": "Multiline post",
        "password": secrets.token_hex(32)
    })
    async with session.post(url_ghostbin_api, data=request_body, timeout=10) as response:
        reply = f"Multiline post: {response.url}"
    logger.info("id=%s | %s", message_id, reply)
    await channel.send(reply)


def main():
    """Factory to create and start the bot."""

    with open("config.json") as config_file:
        config = json.load(config_file)

    token = config.get("twitch_token")
    assert isinstance(token, str), "OAuth token not valid."

    backend_port_number = config.get("backend_port_number", 9980)
    prefix = str(config.get("prefix", ""))
    use_ghostbin = config.get("twitch_post_long_messages_to_ghostbin", False)

    client = twitchio.Client(token, initial_channels=config.get("twitch_channels", []))
    client_session = aiohttp.ClientSession(loop=client.loop)

    @client.event()
    async def event_ready():
        """Bot has logged in."""
        logger.info("%s is now online", client.nick)

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
            message.channel,
            to_one_liner(message.content)
        )

        request_body = {
            "id": f"twitchpy:{message_id}",
            "message": message_text,
            "is_owner": is_owner,
            "character_limit": 500
        }

        try:
            async with client_session.post(
                f"http://localhost:{backend_port_number}",
                json=request_body,
                timeout=10
            ) as response:
                reply_stack = await response.json()
                if response.status != 200:
                    logger.error("id=%s | %s", message_id, to_one_liner(reply_stack[0]))
                else:
                    logger.info("id=%s | %s", message_id, to_one_liner(reply_stack[0]))
            await ext_send(
                client_session,
                message.channel,
                message_id,
                reply_stack,
                use_ghostbin=use_ghostbin
            )

        except Exception as error:
            logger.error("id=%s | %s", message_id, to_one_liner(str(error)))
            if isinstance(error, aiohttp.client_exceptions.ClientConnectorError):
                await message.channel.send("My brain stopped working. Please contact my owner. :<")
            else:
                await message.channel.send(str(error))

    client.run()


if __name__ == "__main__":
    main()
