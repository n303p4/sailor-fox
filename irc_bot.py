#!/usr/bin/env python3

"""A basic IRC bot made using sailor's command handler.

Requires Python 3.6+ and irc.
"""

import logging

import irc.bot

from sailor import commands, exceptions

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


class Bot(irc.bot.SingleServerIRCBot):
    """Custom bot subclass that uses sailor."""

    def __init__(self, channel, nickname, server, processor, realname=None, port=6667):
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, realname or nickname)
        self.channel = channel
        self.processor = processor

    def on_nicknameinuse(self, c, _):
        """If the bot's nickname collides, add a _ after it."""
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, _):
        """Join the channel specified in config."""
        c.join(self.channel)

    def on_pubmsg(self, _, e):
        """On message, invoke the command processor."""

        def split_notice(message):
            """A helper function. IRC doesn't like newlines, so we split the message by newlines.
            """
            for line in message.split("\n"):
                self.connection.notice(e.source.nick, line)

        async def send(message):
            """Define a custom send callback for the processor."""
            split_notice(message)

        message = e.arguments[0]

        try:
            self.processor.process_sync(message, character_limit=512, callback_send=send)
        except (exceptions.CommandError, exceptions.CommandProcessorError) as error:
            split_notice(f"{error}")


def main():
    """Main function to start the bot."""
    processor = commands.Processor(config_file="config.json")
    processor.load_config()

    nick = processor.config.get("nick")
    channel = processor.config.get("channel")
    network = processor.config.get("network")
    port = processor.config.get("port", 6667)
    realname = processor.config.get("realname", nick)

    processor.prefix = processor.config.get("prefix", "")

    blacklist = processor.config.get("module_blacklist", [])

    processor.add_modules_from_dir("cogs", blacklist=blacklist)

    bot = Bot(channel, nick, network, processor, realname=realname, port=port)
    bot.start()


if __name__ == "__main__":
    main()
