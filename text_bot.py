#!/usr/bin/env python3

"""A basic command-line bot made using sailor's command handler."""

import sys

from sailor import commands, exceptions


def split_first_word(text, prefix):
    """If a text string starts with a substring, return the substring and the text minus the
    first instance of the substring; otherwise return None and the text.
    """
    if text.startswith(prefix):
        return prefix, text[len(prefix):].lstrip()
    return None, text


async def send(message):
    """Here is a very basic send coroutine for a text bot."""
    print(message)


def main():
    """Main method to start the bot."""
    processor = commands.Processor(logout=sys.exit)

    processor.load_config()
    global_prefix = processor.config.get("prefix", "")

    blacklist = processor.config.get("module_blacklist", [])
    processor.add_modules_from_dir("cogs", blacklist=blacklist)

    print(f"Enter commands here. Commands must start with {global_prefix}")
    print(f"For help, use {global_prefix} help.")

    while True:
        prefix, message = split_first_word(input("> "), global_prefix)
        if prefix:
            try:
                processor.loop.run_until_complete(processor.process(message, reply_with=send,
                                                                    is_owner=True))
            except (exceptions.CommandProcessorError, exceptions.CommandError):
                pass


if __name__ == "__main__":
    main()
