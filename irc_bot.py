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

    def __init__(self, quick_init=False):
        self.channel = None
        self.processor = commands.Processor()
        if quick_init:
            self.processor.load_config()

            nick = self.processor.config.get("nick")
            self.channel = self.processor.config.get("channel")
            network = self.processor.config.get("network")
            port = self.processor.config.get("port", 6667)
            realname = self.processor.config.get("realname", nick)

            self.processor.prefix = self.processor.config.get("prefix", "")

            blacklist = self.processor.config.get("module_blacklist", [])

            self.processor.add_modules_from_dir("cogs", blacklist=blacklist)

            irc.bot.SingleServerIRCBot.__init__(
                self, [(network, port)], nick, realname or nick)

    def on_nicknameinuse(self, connection, _):
        """If the bot's nickname collides, add a _ after it."""
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, _):
        """Join the channel specified in config."""
        connection.join(self.channel)

    def on_pubmsg(self, _, event):
        """On message, invoke the command processor."""

        def split_notice(message):
            """A helper function. IRC doesn't like newlines, so we split the message by newlines.
            """
            for line in message.split("\n"):
                self.connection.notice(event.source.nick, line)

        async def send(message):
            """Define a custom send callback for the processor."""
            split_notice(message)

        message = event.arguments[0]

        try:
            self.processor.process_sync(message, character_limit=512, callback_send=send)
        except (exceptions.CommandError, exceptions.CommandProcessorError) as error:
            split_notice(f"{error}")


def main():
    """Main function to start the bot."""
    bot = Bot(quick_init=True)
    bot.start()


if __name__ == "__main__":
    main()
