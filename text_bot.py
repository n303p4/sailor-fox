#!/usr/bin/env python3

"""A basic command-line bot made using sailor's command handler."""

import sys

from sailor import commands, exceptions


async def send(message):
    """Here is a very basic send coroutine for a text bot."""
    print(message)


def main():
    """Main method to start the bot."""
    processor = commands.Processor(logout=sys.exit)

    processor.load_config()
    processor.prefix = processor.config.get("prefix", "")

    blacklist = processor.config.get("module_blacklist", [])
    processor.add_modules_from_dir("cogs", blacklist=blacklist)

    print(f"Enter commands here. Commands must start with {processor.prefix}")
    print(f"For help, use {processor.prefix} help.")

    while True:
        message = input("> ")
        try:
            processor.process_sync(message, is_owner=True, callback_send=send)
        except (exceptions.CommandProcessorError, exceptions.CommandError):
            pass


if __name__ == "__main__":
    main()
